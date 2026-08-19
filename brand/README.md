# Meter

The colour and icon system for VERB. Small on purpose. Everything here exists to make a number readable at a glance in a room where somebody is about to argue with it.

## The mark

`logo.svg` is a frame with four bars in it. Three fit. The fourth breaks out of the frame.

That is the whole framework in one glyph: three decision classes sit inside the verification budget, and the fourth does not. The bars are ordered by cost of checking, and the colour of each bar is the colour of its class everywhere else in the repository, so the mark and the charts use the same encoding.

| File | Use |
|---|---|
| `logo.svg` | Default mark, light backgrounds |
| `logo-dark.svg` | Mark for dark backgrounds |
| `favicon.svg` | Solid tile, small sizes, browser tabs |
| `wordmark.svg` | VERB set in square-counter stencil letterforms, drawn as paths |
| `logo-lockup.svg` | Mark plus wordmark plus descriptor, horizontal |

The wordmark is drawn as vector paths, not text, so it renders identically everywhere and needs no font. The descriptor line in the lockup is the one piece of live text; convert it to outlines before print.

Minimum size for `logo.svg` is 24px. Below that the four bars stop resolving, so use `favicon.svg`.

## Colour

Seven neutrals, four class colours, three status colours. That is the whole palette. If you need a colour that is not here, one of the ones that is here is being used wrongly.

| Token | Light | Dark | Meaning |
|---|---|---|---|
| `--meter-class-a` | `#2E7D6B` | `#5FBFA6` | Class A, machine-checkable |
| `--meter-class-b` | `#3C6E9F` | `#7FB0DE` | Class B, sample-checkable |
| `--meter-class-c` | `#B8843A` | `#E0AE63` | Class C, expert-checkable |
| `--meter-class-d` | `#A34432` | `#E4785C` | Class D, not checkable in advance |
| `--meter-ok` | `#1F7A5C` | `#5FBFA6` | In budget, O < 0.95 |
| `--meter-limit` | `#B8843A` | `#E0AE63` | At the limit, 0.95 ≤ O ≤ 1.0 |
| `--meter-over` | `#A34432` | `#E4785C` | Overdraft, O > 1.0 |

The class ramp runs cool to warm as the cost of checking rises. It is deliberately not a traffic light: Class C is not "bad", it is expensive. Status colours are separate from class colours for exactly that reason, even though two of the hex values are close. Do not merge them.

Contrast: every foreground token meets WCAG AA against its paired surface at body size. The class colours are used as fills behind white text at 16px and above, and as text on `--meter-paper` at 14px and above.

Never encode class by colour alone. Every class chip in this repository carries its letter.

## Type

Two families, one rule.

- **Every number is set in mono.** Budgets, ratios, costs, drift rates, confidence values.
- **Every sentence is set in sans.**

Both are system stacks. There is no webfont, no download, and no flash of unstyled text. Numbers in mono align in columns, which matters because most of this framework is people comparing one figure against another.

## Icons

24 by 24, 1.8px stroke, round caps and joins, `currentColor` so they inherit. The class icons are the exception: they are solid tiles in their class colour with a knocked-out letter, because a class marker has to be identifiable without context.

| Icon | For |
|---|---|
| `budget.svg` | Verification budget, VB |
| `overdraft.svg` | Overdraft, O > 1 |
| `drift.svg` | Silent drift rate |
| `evidence.svg` | The evidence plane |
| `contract.svg` | The agent role contract |
| `gate.svg` | Eval gates |
| `containment.svg` | Agentic verification, k |
| `classify.svg` | The classifier |
| `reviewer.svg` | Qualified reviewer capacity |
| `reversal.svg` | Reversal, reversal latency |
| `escalation.svg` | Escalation conditions |
| `revocation.svg` | Revocation of agent authority |
| `maturity.svg` | Maturity stages |
| `class-a.svg` to `class-d.svg` | Class markers |

## Using the tokens

CSS custom properties, including the dark scheme, are in `tokens.css`. The same values in a build-tool-friendly shape are in `tokens.json`.

```html
<link rel="stylesheet" href="brand/tokens.css">
```

The calculator in `/calculator` inlines these values rather than linking the file, because it has to work when opened directly from disk with no server. If you change a token here, change it there too. There are two copies and that is a deliberate trade for a single-file calculator with no build step.

## Licence

Apache 2.0, same as the rest of the repository. Use the marks to refer to VERB, including in your own materials. Do not use them to imply that the author endorses your product.
