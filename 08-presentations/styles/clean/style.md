---
# Read by the renderer. Colours are hex without '#'.
name: clean
description: Calm and light, dark green with an orange accent. Work talks, reports, updates.
fonts:
  heading: Georgia   # both ship with macOS and Windows, so the deck looks
  body: Arial        # the same on whatever computer it's shown from
sizes:               # points
  cover: 48          # title and closing slides
  title: 34          # slide titles
  heading: 22        # subtitles, column and card headings
  body: 18
  caption: 12
  stat: 60           # big numbers on stats slides
colors:
  background: FFFFFF # content slides
  surface: EEF2F0    # panels, cards, quote slide, table stripes
  text: 1B2422
  muted: 5C6966      # secondary text, captions, footer
  primary: 1D3B36    # title, section and closing slides; column headings
  on_primary: FFFFFF # text on primary
  accent: E4572E     # bullets, numbers, the motif dot. Use for one thing per slide
motif: circle        # circle | none: a large soft circle + accent dot on dark slides
footer: ""           # text bottom-left on content slides
slide_numbers: true
logo:                # file next to this style.md, shown on title and closing slides
---

# clean

## Mood

Quiet and confident. Lots of white, one dark green that carries the title
and section slides, and an orange accent used sparingly. Serif titles give
it some warmth; the sans body keeps it readable at a distance.

## When to use

Work presentations, status updates, reports, a talk to colleagues. Not for
playful or festive occasions; make a new style for those.

## Rules

- Dark slides (title, section, closing) bracket the content; content
  slides are white.
- Titles say the point of the slide as a short sentence, not just the topic
  ("Fejlene faldt 42 %", not "Fejl").
- Body text no smaller than 16 pt. If it doesn't fit, cut words or split the
  slide.
- Accent orange marks one thing per slide: a number, a bullet, a key word.
- Photos: real, natural light, not stock-photo handshakes. Cropped to fill.
- Vary layouts: no more than two `bullets` slides in a row.
