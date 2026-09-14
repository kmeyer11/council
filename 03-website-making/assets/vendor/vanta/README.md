# vanta

Vanta.js (free) — animated canvas backgrounds built on Three.js. Big visual impact for near-zero effort, good for hero sections. Needs `three.min.js` loaded first, then the effect file, then init on an element:

```html
<script src="../../assets/vendor/vanta/three.min.js"></script>
<script src="../../assets/vendor/vanta/vanta.waves.min.js"></script>
<script>
  VANTA.WAVES({
    el: "#hero",
    mouseControls: true,
    touchControls: true,
    color: 0x0a1a2f,
  });
</script>
```

Effects included: `waves`, `net`, `fog`, `birds`, `globe`, `dots`, `halo`. Each is loaded/initialized the same way — swap the filename and `VANTA.<EFFECT>(...)` call. Grab another effect (`trunk`, `topology`, `rings`, `cells`) from `https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.<effect>.min.js` if needed — note `trunk`/`topology`/`cells` don't require `three.min.js`.

`three.min.js` is pinned to r134 (Vanta's last-tested compatible build) rather than latest — don't bump it without checking Vanta compat first. Effect files are unpinned (`@latest`, downloaded 2026-09-11) — re-download to update.
