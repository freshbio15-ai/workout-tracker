import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

old_ui = """            React.createElement('div', {style:{display:'flex', flexDirection:'column', width:'100%', gap:'8px'}},
              React.createElement('div', {style:{display:'flex', gap:'6px'}},
                React.createElement('button', {onClick:()=>setBwUnit('кг'), style:{padding:'4px 10px', fontSize:'11px', borderRadius:'6px', fontWeight:'bold', background: bwUnit==='кг'?'rgba(16,185,129,.15)':'var(--bg3)', color: bwUnit==='кг'?'var(--green2)':'var(--text3)', border:'1px solid '+(bwUnit==='кг'?'rgba(16,185,129,.3)':'var(--border)')}}, 'кг'),
                React.createElement('button', {onClick:()=>setBwUnit('фунт'), style:{padding:'4px 10px', fontSize:'11px', borderRadius:'6px', fontWeight:'bold', background: bwUnit==='фунт'?'rgba(16,185,129,.15)':'var(--bg3)', color: bwUnit==='фунт'?'var(--green2)':'var(--text3)', border:'1px solid '+(bwUnit==='фунт'?'rgba(16,185,129,.3)':'var(--border)')}}, 'фунт')
              ),
              React.createElement('div', {style:{display:'flex', gap:'8px', width:'100%'}},
                React.createElement('button', {className:'h-filter-btn', style:{width:'auto', flex:'1', margin:0, padding:'0 12px', gap:'6px'}, onClick:()=>setShowBwPicker(true)}, React.createElement(CalendarIcon,{size:14}), fmtShort(bwDate)),
                React.createElement('input', {type:'number', step:'0.001', className:'set-input', style:{flex:'1', padding:'6px', margin:0}, placeholder:bwUnit==='кг'?'75.5':'165.0', value:bwValue, onChange:e=>setBwValue(e.target.value)}),
                React.createElement('button', {className:'bw-toggle-btn active', style:{padding:'0 12px', margin:0, borderRadius:'var(--radius-xs)', background:'rgba(16,185,129,.15)', border:'1px solid rgba(16,185,129,.3)', color:'var(--green2)', fontSize:'12px', fontWeight:'700', cursor:'pointer'}, onClick:()=>{
                  let val = Number(bwValue);
                  if(bwDate && val > 0) {
                    if(bwUnit === 'фунт') val = val * 0.453592; // convert lbs to kg
                    setSettings(s => ({...s, weightHistory: {...(s.weightHistory||{}), [bwDate]: val}}));
                    setBwValue('');
                    flash('Вагу збережено');
                  }
                }}, 'Додати')
              )
            )"""

new_ui = """            React.createElement('div', {style:{display:'flex', gap:'8px', width:'100%', alignItems:'flex-end'}},
              React.createElement('button', {className:'h-filter-btn', style:{width:'auto', flex:'1', margin:0, padding:'0 12px', gap:'6px', height:'36px'}, onClick:()=>setShowBwPicker(true)}, React.createElement(CalendarIcon,{size:14}), fmtShort(bwDate)),
              React.createElement('div', {style:{flex:'1', display:'flex', flexDirection:'column', gap:'6px'}},
                React.createElement('div', {style:{display:'flex', gap:'4px', justifyContent:'center'}},
                  React.createElement('button', {onClick:()=>setBwUnit('кг'), style:{padding:'2px 8px', fontSize:'10px', borderRadius:'4px', fontWeight:'bold', background: bwUnit==='кг'?'rgba(16,185,129,.15)':'var(--bg3)', color: bwUnit==='кг'?'var(--green2)':'var(--text3)', border:'1px solid '+(bwUnit==='кг'?'rgba(16,185,129,.3)':'var(--border)')}}, 'кг'),
                  React.createElement('button', {onClick:()=>setBwUnit('фунт'), style:{padding:'2px 8px', fontSize:'10px', borderRadius:'4px', fontWeight:'bold', background: bwUnit==='фунт'?'rgba(16,185,129,.15)':'var(--bg3)', color: bwUnit==='фунт'?'var(--green2)':'var(--text3)', border:'1px solid '+(bwUnit==='фунт'?'rgba(16,185,129,.3)':'var(--border)')}}, 'фунт')
                ),
                React.createElement('input', {type:'number', step:'0.001', className:'set-input', style:{padding:'0', margin:0, height:'36px'}, placeholder:bwUnit==='кг'?'75.5':'165.0', value:bwValue, onChange:e=>setBwValue(e.target.value)})
              ),
              React.createElement('button', {className:'bw-toggle-btn active', style:{padding:'0 12px', margin:0, height:'36px', borderRadius:'var(--radius-xs)', background:'rgba(16,185,129,.15)', border:'1px solid rgba(16,185,129,.3)', color:'var(--green2)', fontSize:'12px', fontWeight:'700', cursor:'pointer'}, onClick:()=>{
                let val = Number(bwValue);
                if(bwDate && val > 0) {
                  if(bwUnit === 'фунт') val = val * 0.453592; // convert lbs to kg
                  setSettings(s => ({...s, weightHistory: {...(s.weightHistory||{}), [bwDate]: val}}));
                  setBwValue('');
                  flash('Вагу збережено');
                }
              }}, 'Додати')
            )"""

if old_ui in js:
    js = js.replace(old_ui, new_ui)
    with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
        f.write(js)
    print("UI adjusted.")
else:
    print("Pattern not found.")
