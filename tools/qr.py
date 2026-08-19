"""A QR encoder in pure Python. No dependencies, no external service.

The deck's closing slide carries a QR code pointing at the repository. Fetching
that from a QR web service would mean the build depends on somebody else's
uptime and that the URL travels to a third party, so it is generated here.

Scope, deliberately narrow:

* Byte mode only. URLs are what this is for.
* Error correction level M, roughly 15 percent recovery. The right level for a
  code projected on a screen and photographed at an angle.
* Versions 1 to 3, which is a single error correction block and up to 42 bytes.
  Multi-block interleaving is where a from-scratch encoder goes wrong, so it is
  not attempted. Longer input raises rather than guessing.

Correctness is checked three ways in tests/test_qr.py, because an encoder that
produces a plausible-looking but unscannable square is worse than no encoder:

1. The Reed-Solomon codeword stream is verified to have zero syndromes, which
   tests the field arithmetic independently of the rest.
2. The finished matrix is decoded back to the input string, which tests
   placement, masking and format information.
3. Structural invariants: module count, finder patterns, timing patterns.

    from tools.qr import encode, to_svg
    matrix = encode("https://github.com/hotragn/verb")
    Path("qr.svg").write_text(to_svg(matrix))
"""

from __future__ import annotations

import struct
import zlib
from typing import Sequence

__all__ = ["QRError", "encode", "to_svg", "to_png", "to_ascii", "decode"]


class QRError(ValueError):
    """Raised when the input does not fit the supported versions."""


# ---------------------------------------------------------------------------
# Tables. Level M, versions 1 to 3, one error correction block each.
# ---------------------------------------------------------------------------

#: version -> (total codewords, data codewords, error correction codewords)
_CAPACITY: dict[int, tuple[int, int, int]] = {
    1: (26, 16, 10),
    2: (44, 28, 16),
    3: (70, 44, 26),
}

#: version -> alignment pattern centres. Centres that collide with a finder
#: pattern are filtered out when the pattern is drawn.
_ALIGNMENT: dict[int, list[int]] = {1: [], 2: [6, 18], 3: [6, 22]}

#: Level M in the format information table.
_ECC_BITS = 0b00

_FORMAT_MASK = 0b101_0100_0001_0010
_FORMAT_GENERATOR = 0b101_0011_0111

_PAD_BYTES = (0xEC, 0x11)

_MASKS = [
    lambda r, c: (r + c) % 2 == 0,
    lambda r, c: r % 2 == 0,
    lambda r, c: c % 3 == 0,
    lambda r, c: (r + c) % 3 == 0,
    lambda r, c: (r // 2 + c // 3) % 2 == 0,
    lambda r, c: (r * c) % 2 + (r * c) % 3 == 0,
    lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
    lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0,
]


# ---------------------------------------------------------------------------
# GF(256) arithmetic, the field the QR spec uses (primitive polynomial 0x11D)
# ---------------------------------------------------------------------------

_EXP: list[int] = [0] * 512
_LOG: list[int] = [0] * 256


def _build_tables() -> None:
    value = 1
    for i in range(255):
        _EXP[i] = value
        _LOG[value] = i
        value <<= 1
        if value & 0x100:
            value ^= 0x11D
    for i in range(255, 512):
        _EXP[i] = _EXP[i - 255]


_build_tables()


def _gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return _EXP[_LOG[a] + _LOG[b]]


def _rs_generator(degree: int) -> list[int]:
    """Generator polynomial for ``degree`` error correction codewords.

    Built as the product of (x + alpha^i) for i in 0..degree-1, and returned
    highest degree first with a leading coefficient of 1, which is the order
    :func:`_rs_encode` expects. Getting this order wrong produces a matrix that
    round-trips through :func:`decode` and fails on a real scanner, because the
    data codewords are right and only the error correction bytes are wrong.
    That is what :func:`rs_syndromes` is for.
    """
    poly = [1]  # lowest degree first while building
    for i in range(degree):
        poly.append(0)
        for j in range(len(poly) - 1, 0, -1):
            poly[j] = poly[j - 1] ^ _gf_mul(poly[j], _EXP[i])
        poly[0] = _gf_mul(poly[0], _EXP[i])
    return poly[::-1]


def _rs_encode(data: Sequence[int], ec_count: int) -> list[int]:
    """Reed-Solomon error correction codewords for ``data``."""
    generator = _rs_generator(ec_count)
    remainder = [0] * ec_count
    for byte in data:
        factor = byte ^ remainder[0]
        remainder = remainder[1:] + [0]
        for i in range(ec_count):
            remainder[i] ^= _gf_mul(generator[i + 1], factor)
    return remainder


def rs_syndromes(codewords: Sequence[int], ec_count: int) -> list[int]:
    """Syndromes of a full codeword stream. All zero means no detected error.

    Exposed so the test suite can check the field arithmetic on its own, without
    relying on the decoder agreeing with the encoder about an unrelated mistake.
    """
    syndromes = []
    for i in range(ec_count):
        value = 0
        for byte in codewords:
            value = _gf_mul(value, _EXP[i]) ^ byte
        syndromes.append(value)
    return syndromes


# ---------------------------------------------------------------------------
# Bit stream
# ---------------------------------------------------------------------------


def _choose_version(length: int) -> int:
    for version in sorted(_CAPACITY):
        # 4 mode bits + 8 length bits + 8 bits per byte, rounded up to codewords.
        needed = (4 + 8 + length * 8 + 7) // 8
        if needed <= _CAPACITY[version][1]:
            return version
    raise QRError(
        f"{length} bytes does not fit versions 1 to 3 at error correction level M "
        f"(maximum {_CAPACITY[3][1] - 2} bytes). This encoder does not implement "
        "multi-block interleaving. Shorten the URL, or use a full QR library."
    )


def _data_codewords(payload: bytes, version: int) -> list[int]:
    capacity = _CAPACITY[version][1]
    bits: list[int] = []

    def push(value: int, width: int) -> None:
        for shift in range(width - 1, -1, -1):
            bits.append((value >> shift) & 1)

    push(0b0100, 4)              # byte mode
    push(len(payload), 8)        # character count, 8 bits for versions 1 to 9
    for byte in payload:
        push(byte, 8)

    terminator = min(4, capacity * 8 - len(bits))
    push(0, terminator)
    while len(bits) % 8:
        bits.append(0)

    codewords = [int("".join(str(b) for b in bits[i : i + 8]), 2) for i in range(0, len(bits), 8)]
    index = 0
    while len(codewords) < capacity:
        codewords.append(_PAD_BYTES[index % 2])
        index += 1
    return codewords


# ---------------------------------------------------------------------------
# Matrix construction
# ---------------------------------------------------------------------------


def _size(version: int) -> int:
    return version * 4 + 17


def _blank(version: int) -> tuple[list[list[int | None]], list[list[bool]]]:
    n = _size(version)
    return [[None] * n for _ in range(n)], [[False] * n for _ in range(n)]


def _place_finder(matrix, reserved, row: int, col: int) -> None:
    n = len(matrix)
    for dr in range(-1, 8):
        for dc in range(-1, 8):
            r, c = row + dr, col + dc
            if not (0 <= r < n and 0 <= c < n):
                continue
            inside = 0 <= dr <= 6 and 0 <= dc <= 6
            ring = inside and (dr in (0, 6) or dc in (0, 6))
            core = inside and 2 <= dr <= 4 and 2 <= dc <= 4
            matrix[r][c] = 1 if (ring or core) else 0
            reserved[r][c] = True


def _place_alignment(matrix, reserved, version: int) -> None:
    centres = _ALIGNMENT[version]
    n = _size(version)
    for row in centres:
        for col in centres:
            # Skip the three that collide with finder patterns.
            if (row < 8 and col < 8) or (row < 8 and col > n - 9) or (row > n - 9 and col < 8):
                continue
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    ring = max(abs(dr), abs(dc))
                    matrix[row + dr][col + dc] = 1 if ring != 1 else 0
                    reserved[row + dr][col + dc] = True


def _place_timing(matrix, reserved) -> None:
    n = len(matrix)
    for i in range(8, n - 8):
        bit = 1 if i % 2 == 0 else 0
        if not reserved[6][i]:
            matrix[6][i] = bit
            reserved[6][i] = True
        if not reserved[i][6]:
            matrix[i][6] = bit
            reserved[i][6] = True


def _reserve_format(matrix, reserved) -> None:
    n = len(matrix)
    # The dark module, always set, always at (4*version + 9, 8).
    matrix[n - 8][8] = 1
    reserved[n - 8][8] = True
    for i in range(9):
        if not reserved[8][i]:
            reserved[8][i] = True
            matrix[8][i] = 0
        if not reserved[i][8]:
            reserved[i][8] = True
            matrix[i][8] = 0
    for i in range(8):
        if not reserved[8][n - 1 - i]:
            reserved[8][n - 1 - i] = True
            matrix[8][n - 1 - i] = 0
        if not reserved[n - 1 - i][8]:
            reserved[n - 1 - i][8] = True
            matrix[n - 1 - i][8] = 0


def _placement_order(version: int, reserved) -> list[tuple[int, int]]:
    """The zigzag, bottom-right upward, skipping the vertical timing column."""
    n = _size(version)
    order: list[tuple[int, int]] = []
    col = n - 1
    upward = True
    while col > 0:
        if col == 6:          # the vertical timing pattern column is skipped
            col -= 1
        rows = range(n - 1, -1, -1) if upward else range(n)
        for row in rows:
            for c in (col, col - 1):
                if not reserved[row][c]:
                    order.append((row, c))
        upward = not upward
        col -= 2
    return order


def _format_bits(mask: int) -> int:
    data = (_ECC_BITS << 3) | mask
    value = data << 10
    for _ in range(5):
        if value.bit_length() >= 11:
            value ^= _FORMAT_GENERATOR << (value.bit_length() - 11)
    return ((data << 10) | value) ^ _FORMAT_MASK


def _write_format(matrix, mask: int) -> None:
    n = len(matrix)
    bits = _format_bits(mask)
    for i in range(15):
        bit = (bits >> i) & 1
        # Copy one, around the top-left finder.
        if i < 6:
            matrix[8][i] = bit
        elif i == 6:
            matrix[8][7] = bit
        elif i == 7:
            matrix[8][8] = bit
        elif i == 8:
            matrix[7][8] = bit
        else:
            matrix[14 - i][8] = bit
        # Copy two: bits 0 to 6 run up column 8 from the bottom, bits 7 to 14
        # run along row 8 to the right edge. The split is at 7, not 8: taking
        # eight bits down the column overwrites the dark module at row n-8.
        if i < 7:
            matrix[n - 1 - i][8] = bit
        else:
            matrix[8][n - 15 + i] = bit


def _penalty(matrix) -> int:
    """The four penalty rules used to choose a mask."""
    n = len(matrix)
    score = 0

    # Rule 1: runs of five or more identical modules in a row or column.
    for line in list(matrix) + [list(col) for col in zip(*matrix)]:
        run, previous = 1, line[0]
        for value in line[1:]:
            if value == previous:
                run += 1
            else:
                if run >= 5:
                    score += 3 + (run - 5)
                run, previous = 1, value
        if run >= 5:
            score += 3 + (run - 5)

    # Rule 2: 2x2 blocks of one colour.
    for r in range(n - 1):
        for c in range(n - 1):
            block = {matrix[r][c], matrix[r][c + 1], matrix[r + 1][c], matrix[r + 1][c + 1]}
            if len(block) == 1:
                score += 3

    # Rule 3: the finder-like pattern 1011101 with four light modules either side.
    patterns = ([1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1])
    for line in list(matrix) + [list(col) for col in zip(*matrix)]:
        for i in range(n - 10):
            window = list(line[i : i + 11])
            if window in patterns:
                score += 40

    # Rule 4: deviation from an even balance of dark and light.
    dark = sum(sum(row) for row in matrix)
    percent = dark * 100 / (n * n)
    score += 10 * int(abs(percent - 50) // 5)
    return score


def encode(text: str) -> list[list[int]]:
    """Encode ``text`` as a QR matrix of 0 and 1, without a quiet zone.

    Raises:
        QRError: if the payload does not fit versions 1 to 3 at level M.
    """
    payload = text.encode("utf-8")
    version = _choose_version(len(payload))
    _, data_capacity, ec_count = _CAPACITY[version]

    data = _data_codewords(payload, version)
    codewords = data + _rs_encode(data, ec_count)
    assert len(data) == data_capacity

    matrix, reserved = _blank(version)
    n = _size(version)
    _place_finder(matrix, reserved, 0, 0)
    _place_finder(matrix, reserved, 0, n - 7)
    _place_finder(matrix, reserved, n - 7, 0)
    _place_alignment(matrix, reserved, version)
    _place_timing(matrix, reserved)
    _reserve_format(matrix, reserved)

    order = _placement_order(version, reserved)
    bits = [(byte >> shift) & 1 for byte in codewords for shift in range(7, -1, -1)]
    for (row, col), bit in zip(order, bits):
        matrix[row][col] = bit
    for row, col in order[len(bits) :]:
        matrix[row][col] = 0

    best: tuple[int, list[list[int]]] | None = None
    for mask_index, rule in enumerate(_MASKS):
        candidate = [list(row) for row in matrix]
        for row, col in order:
            if rule(row, col):
                candidate[row][col] ^= 1
        _write_format(candidate, mask_index)
        score = _penalty(candidate)
        if best is None or score < best[0]:
            best = (score, candidate)

    assert best is not None
    return [[int(v or 0) for v in row] for row in best[1]]


# ---------------------------------------------------------------------------
# Decoding, for the round-trip self-test
# ---------------------------------------------------------------------------


def decode(matrix: Sequence[Sequence[int]]) -> str:
    """Read a matrix produced by :func:`encode` back to its input string.

    Assumes no damage, so there is no error correction step. This exists to prove
    the encoder round-trips, not to read photographs.
    """
    n = len(matrix)
    version = (n - 17) // 4
    if version not in _CAPACITY:
        raise QRError(f"unsupported size: {n} modules")

    # Recover the mask from the format information.
    stored = 0
    for i in range(15):
        if i < 6:
            bit = matrix[8][i]
        elif i == 6:
            bit = matrix[8][7]
        elif i == 7:
            bit = matrix[8][8]
        elif i == 8:
            bit = matrix[7][8]
        else:
            bit = matrix[14 - i][8]
        stored |= bit << i
    mask = ((stored ^ _FORMAT_MASK) >> 10) & 0b111

    _, reserved = _blank(version)
    scratch, _ = _blank(version)
    _place_finder(scratch, reserved, 0, 0)
    _place_finder(scratch, reserved, 0, n - 7)
    _place_finder(scratch, reserved, n - 7, 0)
    _place_alignment(scratch, reserved, version)
    _place_timing(scratch, reserved)
    _reserve_format(scratch, reserved)

    rule = _MASKS[mask]
    bits: list[int] = []
    for row, col in _placement_order(version, reserved):
        bit = matrix[row][col]
        if rule(row, col):
            bit ^= 1
        bits.append(bit)

    codewords = [int("".join(str(b) for b in bits[i : i + 8]), 2) for i in range(0, len(bits) // 8 * 8, 8)]
    if codewords[0] >> 4 != 0b0100:
        raise QRError("not byte mode")
    length = ((codewords[0] & 0x0F) << 4) | (codewords[1] >> 4)
    payload = bytearray()
    for i in range(length):
        high = codewords[1 + i] & 0x0F
        low = codewords[2 + i] >> 4
        payload.append((high << 4) | low)
    return payload.decode("utf-8")


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def to_svg(
    matrix: Sequence[Sequence[int]],
    module: int = 8,
    quiet_zone: int = 4,
    dark: str = "#101418",
    light: str = "#F6F5F2",
    title: str = "QR code",
) -> str:
    """Render a matrix as an SVG string.

    A quiet zone of four modules is part of the specification, not decoration.
    Scanners need it, and a code pasted flush against a coloured slide will not
    read.
    """
    n = len(matrix)
    span = n + quiet_zone * 2
    size = span * module

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {span} {span}" shape-rendering="crispEdges" role="img" '
        f'aria-label="{title}">',
        f"  <title>{title}</title>",
        f'  <rect width="{span}" height="{span}" fill="{light}"/>',
        f'  <g fill="{dark}">',
    ]
    for r, row in enumerate(matrix):
        c = 0
        while c < n:
            if row[c]:
                run = 1
                while c + run < n and row[c + run]:
                    run += 1
                parts.append(
                    f'    <rect x="{c + quiet_zone}" y="{r + quiet_zone}" '
                    f'width="{run}" height="1"/>'
                )
                c += run
            else:
                c += 1
    parts.append("  </g>")
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def to_png(
    matrix: Sequence[Sequence[int]],
    module: int = 10,
    quiet_zone: int = 4,
    dark: tuple[int, int, int] = (16, 20, 24),
    light: tuple[int, int, int] = (255, 255, 255),
) -> bytes:
    """Render a matrix as PNG bytes.

    Written out by hand because zlib and struct are in the standard library and
    an image encoder is not worth a dependency. PowerPoint and most document
    tools will not place an SVG, so the deck build writes both.
    """
    n = len(matrix)
    span = (n + quiet_zone * 2) * module

    rows = bytearray()
    for y in range(span):
        rows.append(0)  # filter type 0, none
        my = y // module - quiet_zone
        for x in range(span):
            mx = x // module - quiet_zone
            inside = 0 <= my < n and 0 <= mx < n
            pixel = dark if (inside and matrix[my][mx]) else light
            rows.extend(pixel)

    def chunk(tag: bytes, payload: bytes) -> bytes:
        body = tag + payload
        return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body))

    header = struct.pack(">IIBBBBB", span, span, 8, 2, 0, 0, 0)  # 8-bit truecolour
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + chunk(b"IEND", b"")
    )


def to_ascii(matrix: Sequence[Sequence[int]], quiet_zone: int = 2) -> str:
    """Render a matrix as text, for checking it in a terminal."""
    n = len(matrix)
    blank = "  " * (n + quiet_zone * 2)
    lines = [blank] * quiet_zone
    for row in matrix:
        cells = "".join("##" if value else "  " for value in row)
        lines.append("  " * quiet_zone + cells + "  " * quiet_zone)
    lines.extend([blank] * quiet_zone)
    return "\n".join(lines)
