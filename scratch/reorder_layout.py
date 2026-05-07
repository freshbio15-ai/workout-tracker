import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# We need to extract the 4 blocks: sets-header, hint, bw-toggle, and reorder them.
# Let's locate the exact strings.

old_chunk = """            React.createElement('div',{className:'sets-header'},
              React.createElement('span', {style:{color:'var(--text2)'}}, (() => {
                const mg = MUSCLES.find(m => m.id === ex.muscle);
                return mg ? mg.label : 'Сет';
              })()),
              React.createElement('span',null,'Вага'),
              React.createElement('span',null,'Повт.'),
              React.createElement('span',null,'')
            ),
            // "Минулого разу" hint
            (()=>{const ps=ex.sets.find(s=>s.prevWeight||s.prevReps);return ps?React.createElement('div',{style:{fontSize:'11px',color:'var(--text3)',fontStyle:'italic',marginBottom:'6px',paddingLeft:'2px'}},`Минулого разу: ${ps.prevWeight||'?'} кг × ${ps.prevReps||'?'}`):null})(),
            // BW toggle at exercise level
            React.createElement('button',{className:'bw-toggle-btn'+(ex.sets[0].bw?' active':''),onClick:()=>toggleBW(ei),style:{marginBottom:'8px',width:'100%',padding:'8px 12px',borderRadius:'10px',border:'1px solid '+(ex.sets[0].bw?'rgba(16,185,129,.3)':'var(--border)'),background:ex.sets[0].bw?'rgba(16,185,129,.12)':'var(--bg3)',color:ex.sets[0].bw?'var(--green2)':'var(--text3)',fontSize:'12px',fontWeight:'700',cursor:'pointer',display:'flex',alignItems:'center',justifyContent:'center',gap:'6px',transition:'all .15s',fontFamily:'inherit'}},
              React.createElement(ActivityIcon,{size:14}), 'Вправа зі своєю вагою'
            ),"""

new_chunk = """            // "Минулого разу" hint
            (()=>{const ps=ex.sets.find(s=>s.prevWeight||s.prevReps);return ps?React.createElement('div',{style:{fontSize:'12px',color:'var(--text3)',fontStyle:'italic',marginBottom:'12px',paddingLeft:'4px'}},`Минулого разу: ${ps.prevWeight||'?'} кг × ${ps.prevReps||'?'}`):null})(),
            // BW toggle at exercise level
            React.createElement('button',{className:'bw-toggle-btn'+(ex.sets[0].bw?' active':''),onClick:()=>toggleBW(ei),style:{marginBottom:'12px',width:'100%',padding:'8px 12px',borderRadius:'10px',border:'1px solid '+(ex.sets[0].bw?'rgba(16,185,129,.3)':'var(--border)'),background:ex.sets[0].bw?'rgba(16,185,129,.12)':'var(--bg3)',color:ex.sets[0].bw?'var(--green2)':'var(--text3)',fontSize:'12px',fontWeight:'700',cursor:'pointer',display:'flex',alignItems:'center',justifyContent:'center',gap:'6px',transition:'all .15s',fontFamily:'inherit'}},
              React.createElement(ActivityIcon,{size:14}), 'Вправа зі своєю вагою'
            ),
            React.createElement('div',{className:'sets-header'},
              React.createElement('span', {style:{color:'var(--text2)', whiteSpace:'nowrap', overflow:'visible', position:'relative', zIndex:5}}, (() => {
                const mg = MUSCLES.find(m => m.id === ex.muscle);
                return mg ? mg.label : 'Сет';
              })()),
              React.createElement('span',null,'Вага'),
              React.createElement('span',null,'Повт.'),
              React.createElement('span',null,'')
            ),"""

if old_chunk in js:
    js = js.replace(old_chunk, new_chunk)
    with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
        f.write(js)
    print("Reordered successfully.")
else:
    print("Could not find the chunk to replace. Searching for alternative...")
    # fallback search
