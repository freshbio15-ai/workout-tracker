import re

# Fix index.html: use three.js r128 which has proper global examples/js
with open('/Users/mfolwh/Desktop/TRA/index.html', 'r') as f:
    html = f.read()

old_scripts = """  <script src="https://cdn.jsdelivr.net/npm/three@0.152.2/build/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.152.2/examples/js/loaders/GLTFLoader.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.152.2/examples/js/controls/OrbitControls.js"></script>"""

new_scripts = """  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>"""

html = html.replace(old_scripts, new_scripts)

with open('/Users/mfolwh/Desktop/TRA/index.html', 'w') as f:
    f.write(html)

print("index.html CDN fixed.")

# Fix app.js: update deprecated API + add timing fix
with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Replace the entire broken Three.js init useEffect with fixed version
old_effect_start = "  // ── BODY VIEWER THREE.JS INIT ──────────────────────────────────────────"
old_effect_end = "  function startTimer(sec) {"

start_idx = js.index(old_effect_start)
end_idx = js.index(old_effect_end)

new_effect = """  // ── BODY VIEWER THREE.JS INIT ──────────────────────────────────────────
  React.useEffect(() => {
    if (tab !== 'body') return;
    let cancelled = false;

    const MUSCLES = [
      { id: 'chest',      rx: 0.0,   ry: 0.72, rz: 0.48 },
      { id: 'shoulder_l', rx: -0.48, ry: 0.80, rz: 0.05 },
      { id: 'shoulder_r', rx: 0.48,  ry: 0.80, rz: 0.05 },
      { id: 'bicep_l',    rx: -0.5,  ry: 0.62, rz: 0.22 },
      { id: 'bicep_r',    rx: 0.5,   ry: 0.62, rz: 0.22 },
      { id: 'tricep',     rx: 0.5,   ry: 0.62, rz: -0.22 },
      { id: 'abs',        rx: 0.0,   ry: 0.53, rz: 0.48 },
      { id: 'back',       rx: 0.0,   ry: 0.68, rz: -0.45 },
      { id: 'glute',      rx: 0.1,   ry: 0.38, rz: -0.45 },
      { id: 'quad_l',     rx: -0.2,  ry: 0.22, rz: 0.42 },
      { id: 'quad_r',     rx: 0.2,   ry: 0.22, rz: 0.42 },
      { id: 'hamstring',  rx: 0.1,   ry: 0.23, rz: -0.42 },
      { id: 'calf_l',     rx: -0.12, ry: 0.07, rz: 0.32 },
      { id: 'calf_r',     rx: 0.12,  ry: 0.07, rz: 0.32 },
    ];

    // Wait for canvas to be in DOM and have dimensions
    const initTimer = setTimeout(() => {
      if (cancelled) return;
      const canvas = bodyCanvasRef.current;
      if (!canvas || !window.THREE) { console.error('Canvas or THREE not ready', {canvas, THREE: !!window.THREE}); return; }
      const THREE = window.THREE;

      const w = canvas.offsetWidth || canvas.parentElement.offsetWidth || 400;
      const h = canvas.offsetHeight || 480;

      const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setSize(w, h);
      renderer.outputEncoding = 3001; // sRGBEncoding numeric value
      renderer.setClearColor(0x0d0d1a, 1);

      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x0d0d1a);

      const camera = new THREE.PerspectiveCamera(45, w / h, 0.01, 100);
      camera.position.set(0, 0.2, 4);

      const ambient = new THREE.AmbientLight(0xffffff, 1.5);
      scene.add(ambient);
      const dir1 = new THREE.DirectionalLight(0xffffff, 2);
      dir1.position.set(2, 4, 3);
      scene.add(dir1);
      const dir2 = new THREE.DirectionalLight(0xa78bfa, 0.8);
      dir2.position.set(-3, 1, -3);
      scene.add(dir2);
      const dir3 = new THREE.DirectionalLight(0x34d399, 0.4);
      dir3.position.set(0, -2, 2);
      scene.add(dir3);

      const controls = new THREE.OrbitControls(camera, canvas);
      controls.enableDamping = true;
      controls.dampingFactor = 0.08;
      controls.enablePan = false;
      controls.minDistance = 1.5;
      controls.maxDistance = 8;
      controls.target.set(0, 0, 0);

      let modelBounds = null;
      const loader = new THREE.GLTFLoader();
      loader.load('assets/dalbaeb.glb',
        (gltf) => {
          if (cancelled) return;
          const model = gltf.scene;
          const box = new THREE.Box3().setFromObject(model);
          const center = box.getCenter(new THREE.Vector3());
          const size = box.getSize(new THREE.Vector3());
          const maxDim = Math.max(size.x, size.y, size.z);
          const scale = 2.5 / maxDim;
          model.scale.setScalar(scale);
          model.position.set(-center.x * scale, -center.y * scale, -center.z * scale);
          scene.add(model);
          const scaled = size.clone().multiplyScalar(scale);
          const smin = box.min.clone().multiplyScalar(scale).sub(center.clone().multiplyScalar(scale));
          modelBounds = { min: smin, size: scaled };
          setBodyLoading(false);
        },
        undefined,
        (err) => { console.error('GLB error:', err); setBodyLoading(false); }
      );

      let animId;
      const hotspotEls = bodyHotspotsRef.current;
      const vecTmp = new THREE.Vector3();

      function animate() {
        if (cancelled) return;
        animId = requestAnimationFrame(animate);
        controls.update();
        if (modelBounds) {
          const cw = canvas.offsetWidth, ch = canvas.offsetHeight;
          MUSCLES.forEach(m => {
            const el = hotspotEls[m.id];
            if (!el) return;
            vecTmp.set(
              modelBounds.min.x + (m.rx + 0.5) * modelBounds.size.x,
              modelBounds.min.y + m.ry * modelBounds.size.y,
              modelBounds.min.z + (m.rz + 0.5) * modelBounds.size.z
            );
            vecTmp.project(camera);
            const sx = ((vecTmp.x + 1) / 2) * cw;
            const sy = ((-vecTmp.y + 1) / 2) * ch;
            const behind = vecTmp.z > 1;
            el.style.left = sx + 'px';
            el.style.top = sy + 'px';
            el.style.opacity = behind ? '0' : '1';
            el.style.pointerEvents = behind ? 'none' : 'auto';
          });
        }
        renderer.render(scene, camera);
      }
      animate();

      bodySceneRef.current = { renderer, controls, animId: () => animId };
    }, 100); // give React 100ms to mount the canvas

    return () => {
      cancelled = true;
      clearTimeout(initTimer);
      const s = bodySceneRef.current;
      if (s.animId) cancelAnimationFrame(s.animId());
      if (s.controls) s.controls.dispose();
      if (s.renderer) s.renderer.dispose();
      bodySceneRef.current = {};
    };
  }, [tab]);

  """

js = js[:start_idx] + new_effect + js[end_idx:]

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("app.js effect fixed.")
