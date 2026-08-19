"""The QR encoder.

Three independent checks, because an encoder that produces a plausible-looking
but unscannable square is worse than no encoder at all.
"""

from __future__ import annotations

import pytest

from tools.qr import (
    QRError,
    _CAPACITY,
    _data_codewords,
    _rs_encode,
    _rs_generator,
    decode,
    encode,
    rs_syndromes,
    to_ascii,
    to_svg,
)

REPO_URL = "https://github.com/hotragn/verb"
PAGES_URL = "https://hotragn.github.io/verb"


# ---------------------------------------------------------------------------
# Check 1: the field arithmetic, on its own
# ---------------------------------------------------------------------------


def test_generator_polynomial_is_highest_degree_first():
    """(x + 1)(x + a) = x^2 + 3x + 2 over GF(256)."""
    assert _rs_generator(2) == [1, 3, 2]
    assert _rs_generator(10)[0] == 1


@pytest.mark.parametrize("text", [REPO_URL, PAGES_URL, "hi", "x" * 42])
def test_codeword_stream_has_zero_syndromes(text):
    """A valid Reed-Solomon codeword evaluates to zero at every generator root.

    This tests the encoder without relying on the decoder, so a matching mistake
    in both cannot hide.
    """
    matrix = encode(text)
    version = (len(matrix) - 17) // 4
    ec_count = _CAPACITY[version][2]
    data = _data_codewords(text.encode(), version)
    stream = data + _rs_encode(data, ec_count)
    assert rs_syndromes(stream, ec_count) == [0] * ec_count


# ---------------------------------------------------------------------------
# Check 2: round trip
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [REPO_URL, PAGES_URL, "hi", "A", "x" * 42, "https://x.com/hotragn", "VB = (R*H*u)/c"],
)
def test_round_trip(text):
    assert decode(encode(text)) == text


def test_round_trip_survives_utf8():
    text = "verb: c-hat 1.25h"
    assert decode(encode(text)) == text


# ---------------------------------------------------------------------------
# Check 3: structure
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("text,version,size", [("A", 1, 21), ("x" * 20, 2, 25), (REPO_URL, 3, 29)])
def test_version_selection_and_size(text, version, size):
    matrix = encode(text)
    assert len(matrix) == size == version * 4 + 17
    assert all(len(row) == size for row in matrix)


def test_finder_patterns_are_present_in_all_three_corners():
    matrix = encode(REPO_URL)
    n = len(matrix)
    for row, col in ((0, 0), (0, n - 7), (n - 7, 0)):
        assert matrix[row][col] == 1
        assert matrix[row + 1][col + 1] == 0          # the light ring
        assert matrix[row + 3][col + 3] == 1          # the dark core
        assert matrix[row + 6][col + 6] == 1


def test_timing_patterns_alternate():
    matrix = encode(REPO_URL)
    n = len(matrix)
    for i in range(8, n - 8):
        assert matrix[6][i] == (1 if i % 2 == 0 else 0)
        assert matrix[i][6] == (1 if i % 2 == 0 else 0)


def test_the_dark_module_is_set():
    matrix = encode(REPO_URL)
    assert matrix[len(matrix) - 8][8] == 1


def test_every_module_is_zero_or_one():
    for row in encode(REPO_URL):
        assert set(row) <= {0, 1}


def test_alignment_pattern_present_for_version_3():
    matrix = encode(REPO_URL)
    assert matrix[22][22] == 1        # centre
    assert matrix[21][22] == 0        # light ring
    assert matrix[20][20] == 1        # dark border


def test_output_is_deterministic():
    assert encode(REPO_URL) == encode(REPO_URL)


# ---------------------------------------------------------------------------
# Limits
# ---------------------------------------------------------------------------


def test_too_long_raises_rather_than_guessing():
    with pytest.raises(QRError, match="multi-block"):
        encode("x" * 60)


def test_the_error_names_the_limit():
    with pytest.raises(QRError, match="maximum 42 bytes"):
        encode("x" * 100)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def test_svg_is_well_formed_and_carries_a_quiet_zone():
    svg = to_svg(encode(REPO_URL), module=8, quiet_zone=4)
    assert svg.startswith("<svg")
    assert svg.rstrip().endswith("</svg>")
    assert 'viewBox="0 0 37 37"' in svg        # 29 modules plus 4 either side
    assert 'width="296"' in svg                # 37 * 8


def test_svg_uses_the_meter_palette_by_default():
    svg = to_svg(encode("hi"))
    assert "#101418" in svg and "#F6F5F2" in svg


def test_svg_accepts_a_title_for_screen_readers():
    assert "<title>Repository</title>" in to_svg(encode("hi"), title="Repository")


def test_ascii_render_has_one_line_per_module_plus_quiet_zone():
    lines = to_ascii(encode(REPO_URL), quiet_zone=2).split("\n")
    assert len(lines) == 29 + 4
