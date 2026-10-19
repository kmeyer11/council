---
# Read by the renderer. Colours are hex without '#'.
name: bold
description: Base style. High contrast, near-black with an electric blue accent. Every deck starts from a copy.
fonts:
  heading: Trebuchet MS  # both ship with macOS and Windows
  body: Arial
sizes:               # points
  cover: 56          # title and closing slides
  title: 36          # slide titles
  heading: 22        # subtitles, column and card headings
  body: 20
  caption: 12
  stat: 72           # big numbers on stats slides
colors:
  background: FFFFFF # content slides
  surface: F1F3F7    # panels, cards, quote slide, table stripes
  text: 111111
  muted: 6B7280      # secondary text, captions, footer
  primary: 111111    # title, section and closing slides; column headings
  on_primary: FFFFFF # text on primary
  accent: 2D5BFF     # bullets, numbers. Use for one thing per slide
  # heading:         # optional, column headings; defaults to primary. Set it light on a dark background
motif: none          # circle | none
footer: ""           # text bottom-left on content slides
slide_numbers: true
logo:                # file next to this style.md, shown on title and closing slides
---

# bold

## Mood

Direct and modern. Black and white with one loud blue. Big type, few
words. No decoration: the type does the work.

## When to use

This is the base for every deck. `new` copies it into the deck folder,
where it is tailored to the talk: swap colours for a brand, change fonts,
add a footer or logo, relax the rules for a longer, denser talk. Rewrite
this Mood and these Rules in the copy when they no longer fit.

## Rules

- Dark slides (title, section, closing) bracket the content; content
  slides are white.
- Titles are short claims, at most about six words.
- At most three bullets per slide. If you need more, split the slide or use
  `cards`.
- Blue marks one thing per slide: a number, a key word.
- Prefer `stats`, `cards` and `quote` over `bullets`.
- Photos: high contrast, one clear subject. Cropped to fill.
