# lenis

Lenis smooth-scroll library (free) — makes native scroll feel buttery, pairs directly with GSAP ScrollTrigger for scroll-driven animation. Include with:

```html
<script src="../../assets/vendor/lenis/lenis.min.js"></script>
<script>
  const lenis = new Lenis();
  function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
  }
  requestAnimationFrame(raf);
</script>
```

If using with GSAP ScrollTrigger, sync them: call `lenis.on('scroll', ScrollTrigger.update)` and drive the raf loop through `gsap.ticker` instead of a raw `requestAnimationFrame` — see Lenis docs' GSAP recipe.

Version unpinned (`@1`, latest at download time: 2026-09-11) — re-download to update.
