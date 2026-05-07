import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

old_tick = r"""  const playTick = \(\) => \{
    try \{
      const AudioContext = window\.AudioContext \|\| window\.webkitAudioContext;
      if \(!AudioContext\) return;
      const ctx = new AudioContext\(\);
      const osc = ctx\.createOscillator\(\);
      const gain = ctx\.createGain\(\);
      osc\.type = 'sine';
      osc\.frequency\.setValueAtTime\(1000, ctx\.currentTime\);
      gain\.gain\.setValueAtTime\(0\.2, ctx\.currentTime\);
      gain\.gain\.exponentialRampToValueAtTime\(0\.0001, ctx\.currentTime \+ 0\.1\);
      osc\.connect\(gain\);
      gain\.connect\(ctx\.destination\);
      osc\.start\(\);
      osc\.stop\(ctx\.currentTime \+ 0\.1\);
    \} catch\(e\)\{\}
  \};"""

new_tick = r"""  const playTick = () => {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      if (!window.__audioCtx) window.__audioCtx = new AudioContext();
      const ctx = window.__audioCtx;
      if (ctx.state === 'suspended') ctx.resume();
      
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      
      // CS2 bomb tick approx: high pitched square wave, very short, sharp decay
      osc.type = 'square';
      osc.frequency.setValueAtTime(2800, ctx.currentTime); // ~2.8kHz
      
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.06);
      
      // Add slight lowpass filter to remove harsh edge of pure square
      const filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.value = 5000;
      
      osc.connect(filter);
      filter.connect(gain);
      gain.connect(ctx.destination);
      
      osc.start();
      osc.stop(ctx.currentTime + 0.06);
    } catch(e){}
  };"""

js = re.sub(old_tick, new_tick, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Audio tick updated to CS2 style.")
