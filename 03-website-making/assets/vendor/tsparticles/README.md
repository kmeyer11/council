# tsparticles

tsParticles (free) — configurable particle effects (snow, confetti, network links, stars, etc.), lighter-weight than Vanta/Three.js for simple particle backgrounds. This is the full bundle (all presets/shapes included, no separate config needed). Include with:

```html
<script src="../../assets/vendor/tsparticles/tsparticles.bundle.min.js"></script>
<script>
  tsParticles.load({
    id: "particles",
    options: {
      particles: {
        number: { value: 80 },
        links: { enable: true },
        move: { enable: true },
      },
    },
  });
</script>
<div id="particles" style="position: absolute; inset: 0;"></div>
```

Full option reference: https://particles.js.org/ — presets (confetti, snow, fireworks, etc.) are built into this bundle, load via `tsParticles.loadPreset` calls documented there.

Version unpinned (`@3`, latest at download time: 2026-09-11) — re-download to update.
