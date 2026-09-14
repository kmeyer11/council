# gsap

GSAP animation library (free, incl. all plugins as of 2025) — for scroll reveals, parallax, timelines, and other motion across site builds. Include with a plain `<script>` tag, e.g.:

```html
<script src="../../assets/vendor/gsap/gsap.min.js"></script>
<script src="../../assets/vendor/gsap/ScrollTrigger.min.js"></script>
<script>gsap.registerPlugin(ScrollTrigger);</script>
```

Files here: `gsap.min.js` (core, always needed) + plugins `ScrollTrigger`, `ScrollSmoother`, `SplitText`, `Flip`, `Draggable`, `MotionPathPlugin`. Grab any other plugin from `https://cdn.jsdelivr.net/npm/gsap@3/dist/<Plugin>.min.js` if a site needs one not listed here.

Version is unpinned (`@3`, latest at download time: 2026-09-11) — re-download to update.
