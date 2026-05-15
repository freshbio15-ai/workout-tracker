import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Replace the broken loader callback with pivot approach
old_loader = """      const loader = new THREE.GLTFLoader();
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
      );"""

new_loader = """      const loader = new THREE.GLTFLoader();
      loader.load('assets/dalbaeb.glb',
        (gltf) => {
          if (cancelled) return;
          const model = gltf.scene;

          // Compute bounding box in world space (before adding to scene)
          const box = new THREE.Box3().setFromObject(model);
          const center = box.getCenter(new THREE.Vector3());
          const size   = box.getSize(new THREE.Vector3());
          const maxDim = Math.max(size.x, size.y, size.z);
          const scale  = 2.5 / maxDim;

          console.log('[Body] GLB bounds:', { center, size, maxDim, scale });

          // Pivot approach: move model so its bbox center is at pivot origin, then scale pivot
          model.position.sub(center);
          const pivot = new THREE.Group();
          pivot.scale.setScalar(scale);
          pivot.add(model);
          scene.add(pivot);

          // Store bounds in scaled space (pivot is now the reference)
          const scaledSize = size.clone().multiplyScalar(scale);
          const scaledMin  = new THREE.Vector3(
            (box.min.x - center.x) * scale,
            (box.min.y - center.y) * scale,
            (box.min.z - center.z) * scale
          );
          modelBounds = { min: scaledMin, size: scaledSize };

          setBodyLoading(false);
          console.log('[Body] Model loaded. modelBounds:', modelBounds);
        },
        (xhr) => { /* progress */ },
        (err) => { console.error('[Body] GLB load error:', err); setBodyLoading(false); }
      );"""

js = js.replace(old_loader, new_loader)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Model centering fixed.")
