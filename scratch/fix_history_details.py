import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Add playTick sound to timer interval
# Let's insert the playTick function right above the `useEffect` for timer
playTick_fn = r"""
  const playTick = () => {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      const ctx = new AudioContext();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(1000, ctx.currentTime);
      gain.gain.setValueAtTime(0.1, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.1);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.1);
    } catch(e){}
  };

  useEffect(()=>{"""
js = js.replace("  useEffect(()=>{", playTick_fn, 1) # Only replace the first occurrence (which should be the timer one if we target it better, let's be safer)

# Safer way to target the timer useEffect:
js = js.replace(playTick_fn, "  useEffect(()=>{") # Revert if already applied just in case
old_timer_effect = r"""  // ── Timer Logic ──────────────────────────────────────────────────
  useEffect\(\(\)=>\{
    if\(!timerEnd\) return;
    const tick = \(\) => \{
      const remaining = Math\.ceil\(\(timerEnd - Date\.now\(\)\) / 1000\);
      if \(remaining <= 0\) \{
        setTimeLeft\(0\);
        setTimerEnd\(null\);
        if \('vibrate' in navigator\) navigator\.vibrate\(\[500, 200, 500, 200, 1000\]\);
      \} else \{
        setTimeLeft\(remaining\);
      \}
    \};"""

new_timer_effect = r"""  // ── Timer Logic ──────────────────────────────────────────────────
  const playTick = () => {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      const ctx = new AudioContext();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(1000, ctx.currentTime);
      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.1);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.1);
    } catch(e){}
  };

  useEffect(()=>{
    if(!timerEnd) return;
    const tick = () => {
      const remaining = Math.ceil((timerEnd - Date.now()) / 1000);
      if (remaining <= 0) {
        setTimeLeft(0);
        setTimerEnd(null);
        if ('vibrate' in navigator) navigator.vibrate([500, 200, 500, 200, 1000]);
      } else {
        setTimeLeft(remaining);
        if (remaining <= 10) playTick();
      }
    };"""
js = re.sub(old_timer_effect, new_timer_effect, js)

# 2. Remove "Тоннаж по вправах" and "Деталі вправ" labels
js = js.replace("React.createElement('div',{className:'section-label'},'Тоннаж по вправах'),", "")
js = js.replace("React.createElement('div',{className:'section-label'},'Деталі вправ'),", "")

# 3. Update muscle breakdown bars layout in JS
old_mb_layout = r"""React\.createElement\('div',\{className:'muscle-breakdown',style:\{marginBottom:'14px'\}\},
        exTons\.map\(\(ex,i\)=>
          React\.createElement\('div',\{key:i,className:'mb-row'\},
            React\.createElement\('div',\{className:'mb-label',style:\{width:'90px',fontSize:'11px'\}\},ex\.name\),
            React\.createElement\('div',\{className:'mb-bar-wrap'\},
              React\.createElement\('div',\{className:'mb-bar c'\+i%8,style:\{width:Math\.max\(Math\.round\(ex\.ton/maxExTon\*100\),3\)\+'%'\}\}\)
            \),
            React\.createElement\('div',\{className:'mb-val',style:\{width:'50px'\}\},ex\.ton>1000\?\(ex\.ton/1000\)\.toFixed\(1\)\+'т':ex\.ton\+'кг'\)
          \)
        \)
      \)"""

new_mb_layout = r"""React.createElement('div',{className:'muscle-breakdown',style:{marginBottom:'24px'}},
        exTons.map((ex,i)=>
          React.createElement('div',{key:i,className:'mb-row'},
            React.createElement('div',{className:'mb-label'},ex.name),
            React.createElement('div',{className:'mb-bar-wrap'},
              React.createElement('div',{className:'mb-bar c'+i%8,style:{width:Math.max(Math.round(ex.ton/maxExTon*100),3)+'%'}})
            ),
            React.createElement('div',{className:'mb-val'},ex.ton>1000?(ex.ton/1000).toFixed(1)+'т':ex.ton+'кг')
          )
        )
      )"""
js = re.sub(old_mb_layout, new_mb_layout, js)

# 4. Remove rest time for first set (j===0)
# Locate: React.createElement('td',{style:{color:'var(--text2)'}},s.rest?fmtTimer(s.rest):'-'),
old_td_rest = r"React\.createElement\('td',\{style:\{color:'var\(--text2\)'\}\},s\.rest\?fmtTimer\(s\.rest\):'-'\),"
new_td_rest = r"React.createElement('td',{style:{color:'var(--text2)'}},j===0 ? '' : (s.rest?fmtTimer(s.rest):'-')),"
js = re.sub(old_td_rest, new_td_rest, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

# 5. Add CSS for mb-row to styles.css
css_mb = """
/* ===== EXERCISE TONNAGE BARS ===== */
.mb-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.mb-row:last-child {
  margin-bottom: 0;
}
.mb-label {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: var(--text2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mb-bar-wrap {
  flex: 2;
  height: 12px;
  background: var(--bg3);
  border-radius: 6px;
  overflow: hidden;
}
.mb-bar {
  height: 100%;
  border-radius: 6px;
  transition: width 0.8s ease-out;
}
.mb-bar.c0 { background: linear-gradient(90deg, #8b5cf6, #c084fc); }
.mb-bar.c1 { background: linear-gradient(90deg, #06b6d4, #22d3ee); }
.mb-bar.c2 { background: linear-gradient(90deg, #10b981, #34d399); }
.mb-bar.c3 { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.mb-bar.c4 { background: linear-gradient(90deg, #ef4444, #f87171); }
.mb-bar.c5 { background: linear-gradient(90deg, #ec4899, #f472b6); }
.mb-bar.c6 { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.mb-bar.c7 { background: linear-gradient(90deg, #8b5cf6, #c084fc); }

.mb-val {
  font-size: 13px;
  font-weight: 700;
  color: var(--text1);
  text-align: right;
  min-width: 48px;
}
"""

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'a') as f:
    f.write(css_mb)

print("Updates applied.")
