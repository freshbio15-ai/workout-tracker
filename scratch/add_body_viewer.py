import re

# ── 1. index.html ─────────────────────────────────────────────────────────────
with open('/Users/mfolwh/Desktop/TRA/index.html', 'r') as f:
    html = f.read()

three_scripts = """  <script src="https://cdn.jsdelivr.net/npm/three@0.152.2/build/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.152.2/examples/js/loaders/GLTFLoader.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.152.2/examples/js/controls/OrbitControls.js"></script>"""
if 'three@0.152.2' not in html:
    html = html.replace('</head>', three_scripts + '\n</head>')

with open('/Users/mfolwh/Desktop/TRA/index.html', 'w') as f:
    f.write(html)

print("index.html updated.")

# ── 2. app.js ─────────────────────────────────────────────────────────────────
with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 2a. Add state + refs for body viewer
old_state = '  const tRef=useRef(null);\n  const saveTimer=useRef(null);\n  const isFirstLoad=useRef(true);'
new_state = '''  const tRef=useRef(null);
  const saveTimer=useRef(null);
  const isFirstLoad=useRef(true);
  // body viewer
  const bodyCanvasRef = useRef(null);
  const bodySceneRef = useRef({});
  const bodyHotspotsRef = useRef({});
  const [selectedMuscle, setSelectedMuscle] = useState(null);
  const [bodyLoading, setBodyLoading] = useState(true);'''
js = js.replace(old_state, new_state)

# 2b. Add body viewer useEffect (inject before "function startTimer")
body_effect = '''
  // ── BODY VIEWER THREE.JS INIT ──────────────────────────────────────────
  React.useEffect(() => {
    if (tab !== 'body') return;
    const canvas = bodyCanvasRef.current;
    if (!canvas || !window.THREE) return;
    const THREE = window.THREE;

    const MUSCLES = [
      { id: 'chest',     name: 'Груди',          latin: 'Pectoralis Major',     color: '#a78bfa', rx: 0.0,   ry: 0.72, rz: 0.48 },
      { id: 'shoulder_l',name: 'Плечі (ліве)',   latin: 'Deltoid',              color: '#60a5fa', rx: -0.48, ry: 0.80, rz: 0.05 },
      { id: 'shoulder_r',name: 'Плечі (праве)',  latin: 'Deltoid',              color: '#60a5fa', rx: 0.48,  ry: 0.80, rz: 0.05 },
      { id: 'bicep_l',   name: 'Біцепс',         latin: 'Biceps Brachii',       color: '#34d399', rx: -0.5,  ry: 0.62, rz: 0.22 },
      { id: 'bicep_r',   name: 'Біцепс',         latin: 'Biceps Brachii',       color: '#34d399', rx: 0.5,   ry: 0.62, rz: 0.22 },
      { id: 'tricep',    name: 'Трицепс',        latin: 'Triceps Brachii',      color: '#f87171', rx: 0.5,   ry: 0.62, rz: -0.22 },
      { id: 'abs',       name: 'Прес',           latin: 'Rectus Abdominis',     color: '#fbbf24', rx: 0.0,   ry: 0.53, rz: 0.48 },
      { id: 'back',      name: 'Спина',          latin: 'Latissimus Dorsi',     color: '#f472b6', rx: 0.0,   ry: 0.68, rz: -0.45 },
      { id: 'glute',     name: 'Сідниці',        latin: 'Gluteus Maximus',      color: '#fb923c', rx: 0.1,   ry: 0.38, rz: -0.45 },
      { id: 'quad_l',    name: 'Квадрицепс',     latin: 'Quadriceps Femoris',   color: '#38bdf8', rx: -0.2,  ry: 0.22, rz: 0.42 },
      { id: 'quad_r',    name: 'Квадрицепс',     latin: 'Quadriceps Femoris',   color: '#38bdf8', rx: 0.2,   ry: 0.22, rz: 0.42 },
      { id: 'hamstring', name: 'Біцепс стегна',  latin: 'Hamstring',            color: '#e879f9', rx: 0.1,   ry: 0.23, rz: -0.42 },
      { id: 'calf_l',    name: 'Литки',          latin: 'Gastrocnemius',        color: '#a3e635', rx: -0.12, ry: 0.07, rz: 0.32 },
      { id: 'calf_r',    name: 'Литки',          latin: 'Gastrocnemius',        color: '#a3e635', rx: 0.12,  ry: 0.07, rz: 0.32 },
    ];

    setBodyLoading(true);
    const scene = new THREE.Scene();

    const w = canvas.offsetWidth, h = canvas.offsetHeight;
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h);
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;

    const camera = new THREE.PerspectiveCamera(45, w / h, 0.01, 100);
    camera.position.set(0, 0, 4);

    const ambient = new THREE.AmbientLight(0xffffff, 1.2);
    scene.add(ambient);
    const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.8);
    dirLight1.position.set(3, 5, 3);
    scene.add(dirLight1);
    const dirLight2 = new THREE.DirectionalLight(0xa78bfa, 0.6);
    dirLight2.position.set(-3, 2, -3);
    scene.add(dirLight2);
    const fillLight = new THREE.DirectionalLight(0x34d399, 0.3);
    fillLight.position.set(0, -3, 2);
    scene.add(fillLight);

    const controls = new THREE.OrbitControls(camera, canvas);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.enablePan = false;
    controls.minDistance = 1.5;
    controls.maxDistance = 8;
    controls.autoRotate = false;
    controls.target.set(0, 0, 0);

    let modelBounds = null;
    const group = new THREE.Group();
    scene.add(group);

    const loader = new THREE.GLTFLoader();
    loader.load('assets/dalbaeb.glb', (gltf) => {
      const model = gltf.scene;
      const box = new THREE.Box3().setFromObject(model);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const maxDim = Math.max(size.x, size.y, size.z);
      const scale = 2.5 / maxDim;
      model.scale.setScalar(scale);
      model.position.set(-center.x * scale, -center.y * scale, -center.z * scale);
      group.add(model);
      modelBounds = {
        min: new THREE.Vector3(box.min.x * scale - center.x * scale, box.min.y * scale - center.y * scale, box.min.z * scale - center.z * scale),
        size: new THREE.Vector3(size.x * scale, size.y * scale, size.z * scale)
      };
      setBodyLoading(false);
    }, undefined, (err) => { console.error('GLB load error:', err); setBodyLoading(false); });

    let animId;
    const hotspotEls = bodyHotspotsRef.current;

    function animate() {
      animId = requestAnimationFrame(animate);
      controls.update();

      if (modelBounds) {
        MUSCLES.forEach(m => {
          const el = hotspotEls[m.id];
          if (!el) return;
          const wx = modelBounds.min.x + (m.rx + 0.5) * modelBounds.size.x;
          const wy = modelBounds.min.y + m.ry * modelBounds.size.y;
          const wz = modelBounds.min.z + (m.rz + 0.5) * modelBounds.size.z;
          const vec = new THREE.Vector3(wx, wy, wz);
          vec.project(camera);
          const cx = canvas.offsetWidth, cy = canvas.offsetHeight;
          const sx = ((vec.x + 1) / 2) * cx;
          const sy = ((-vec.y + 1) / 2) * cy;
          const behind = vec.z > 1;
          el.style.left = sx + 'px';
          el.style.top = sy + 'px';
          el.style.opacity = behind ? '0' : '1';
          el.style.pointerEvents = behind ? 'none' : 'auto';
        });
      }

      renderer.render(scene, camera);
    }
    animate();

    bodySceneRef.current = { renderer, scene, camera, controls, animId };

    return () => {
      cancelAnimationFrame(animId);
      controls.dispose();
      renderer.dispose();
    };
  }, [tab]);

'''
js = js.replace('  function startTimer(sec) {', body_effect + '  function startTimer(sec) {')

# 2c. Add renderBodyViewer function before renderSettings
body_viewer_fn = r"""  function renderBodyViewer() {
    const MUSCLES_LIST = [
      { id: 'chest',     name: 'Груди',          latin: 'Pectoralis Major',     color: '#a78bfa' },
      { id: 'shoulder_l',name: 'Плечі (ліве)',   latin: 'Deltoid',              color: '#60a5fa' },
      { id: 'shoulder_r',name: 'Плечі (праве)',  latin: 'Deltoid',              color: '#60a5fa' },
      { id: 'bicep_l',   name: 'Біцепс',         latin: 'Biceps Brachii',       color: '#34d399' },
      { id: 'bicep_r',   name: 'Біцепс',         latin: 'Biceps Brachii',       color: '#34d399' },
      { id: 'tricep',    name: 'Трицепс',        latin: 'Triceps Brachii',      color: '#f87171' },
      { id: 'abs',       name: 'Прес',           latin: 'Rectus Abdominis',     color: '#fbbf24' },
      { id: 'back',      name: 'Спина',          latin: 'Latissimus Dorsi',     color: '#f472b6' },
      { id: 'glute',     name: 'Сідниці',        latin: 'Gluteus Maximus',      color: '#fb923c' },
      { id: 'quad_l',    name: 'Квадрицепс',     latin: 'Quadriceps Femoris',   color: '#38bdf8' },
      { id: 'quad_r',    name: 'Квадрицепс',     latin: 'Quadriceps Femoris',   color: '#38bdf8' },
      { id: 'hamstring', name: 'Біцепс стегна',  latin: 'Hamstring',            color: '#e879f9' },
      { id: 'calf_l',    name: 'Литки',          latin: 'Gastrocnemius',        color: '#a3e635' },
      { id: 'calf_r',    name: 'Литки',          latin: 'Gastrocnemius',        color: '#a3e635' },
    ];

    return React.createElement('div', { className: 'body-viewer-wrap' },
      React.createElement('h2', { style: { fontSize: '20px', fontWeight: 800, marginBottom: '12px' } }, 'М\'язова карта'),
      React.createElement('div', { className: 'body-canvas-container' },
        React.createElement('canvas', {
          ref: bodyCanvasRef,
          className: 'body-canvas',
        }),
        bodyLoading && React.createElement('div', { className: 'body-loading' },
          React.createElement('div', { className: 'body-loading-spinner' }),
          React.createElement('span', null, 'Завантаження...')
        ),
        MUSCLES_LIST.map(m =>
          React.createElement('button', {
            key: m.id,
            className: 'body-hotspot' + (selectedMuscle && selectedMuscle.id === m.id ? ' active' : ''),
            ref: el => { if (el) bodyHotspotsRef.current[m.id] = el; },
            style: { '--hotspot-color': m.color },
            onClick: () => setSelectedMuscle(selectedMuscle && selectedMuscle.id === m.id ? null : m),
          })
        )
      ),
      selectedMuscle
        ? React.createElement('div', { className: 'muscle-info-panel' },
            React.createElement('button', { className: 'muscle-info-close', onClick: () => setSelectedMuscle(null) }, '✕'),
            React.createElement('div', { style: { width: 12, height: 12, borderRadius: '50%', background: selectedMuscle.color, flexShrink: 0 } }),
            React.createElement('div', null,
              React.createElement('div', { style: { fontWeight: 800, fontSize: 16 } }, selectedMuscle.name),
              React.createElement('div', { style: { fontSize: 12, color: 'var(--text3)', marginTop: 2 } }, selectedMuscle.latin)
            )
          )
        : React.createElement('div', { className: 'body-hint' }, '👆 Крути модель і натискай на крапки')
    );
  }

"""

js = js.replace('  function renderSettings(){', body_viewer_fn + '  function renderSettings(){')

# 2d. Add body tab content rendering
js = js.replace(
    "tab==='settings'&&renderSettings(),\n      tab==='analytics'&&renderAnalytics()",
    "tab==='settings'&&renderSettings(),\n      tab==='analytics'&&renderAnalytics(),\n      tab==='body'&&renderBodyViewer()"
)

# 2e. Add body tab button in nav (add after settings tab btn)
old_nav = """        React.createElement('button',{className:'tab-btn'+(tab==='settings'?' active':''),onClick:()=>setTab('settings')},
          React.createElement('span',{className:'tab-icon'},React.createElement(SettingsIcon)),React.createElement('span',null,'Налаштування')
        )"""

new_nav = """        React.createElement('button',{className:'tab-btn'+(tab==='settings'?' active':''),onClick:()=>setTab('settings')},
          React.createElement('span',{className:'tab-icon'},React.createElement(SettingsIcon)),React.createElement('span',null,'Налаштування')
        ),
        React.createElement('button',{className:'tab-btn'+(tab==='body'?' active':''),onClick:()=>setTab('body')},
          React.createElement('span',{className:'tab-icon'},React.createElement(ActivityIcon)),React.createElement('span',null,'М\'язи')
        )"""

js = js.replace(old_nav, new_nav)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("app.js updated.")

# ── 3. styles.css ─────────────────────────────────────────────────────────────
with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

body_viewer_css = """
/* ===== BODY VIEWER ===== */
.body-viewer-wrap { padding-bottom: 20px; }
.body-canvas-container {
  position: relative;
  width: 100%;
  height: 480px;
  border-radius: var(--radius);
  overflow: hidden;
  background: radial-gradient(ellipse at center, #14142a 0%, #0a0a12 100%);
  border: 1px solid var(--border);
  margin-bottom: 12px;
  touch-action: none;
}
.body-canvas {
  width: 100%;
  height: 100%;
  display: block;
}
.body-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: rgba(10,10,18,0.8);
  color: var(--text3);
  font-size: 13px;
  font-weight: 600;
}
.body-loading-spinner {
  width: 32px; height: 32px;
  border: 3px solid var(--border2);
  border-top-color: var(--accent2);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.body-hotspot {
  position: absolute;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid var(--hotspot-color, #a78bfa);
  background: rgba(0,0,0,0.6);
  cursor: pointer;
  transform: translate(-50%, -50%);
  transition: transform 0.15s, background 0.15s;
  box-shadow: 0 0 8px var(--hotspot-color, #a78bfa);
  padding: 0;
}
.body-hotspot::after {
  content: '';
  position: absolute;
  inset: 2px;
  border-radius: 50%;
  background: var(--hotspot-color, #a78bfa);
  opacity: 0.7;
}
.body-hotspot:hover, .body-hotspot.active {
  transform: translate(-50%, -50%) scale(1.6);
  background: rgba(0,0,0,0.8);
}
.body-hotspot.active { box-shadow: 0 0 14px var(--hotspot-color, #a78bfa); }

.muscle-info-panel {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg3);
  border: 1px solid var(--border2);
  border-radius: var(--radius-sm);
  padding: 14px 16px;
  animation: slideUp 0.2s ease-out;
  position: relative;
}
.muscle-info-close {
  position: absolute;
  top: 8px; right: 8px;
  background: none; border: none;
  color: var(--text3); cursor: pointer;
  font-size: 14px; line-height: 1;
}
.body-hint {
  text-align: center;
  color: var(--text3);
  font-size: 13px;
  padding: 10px 0;
}
"""
if '.body-viewer-wrap' not in css:
    css += body_viewer_css

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)

print("styles.css updated.")
