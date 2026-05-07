import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Modify the set-row mapping in JS
old_set_row = r"""                React\.createElement\('input',\{className:'set-input',type:s\.bw\?'text':'number',inputMode:'decimal',placeholder:s\.prevWeight\|\|'кг',value:s\.bw\?s\.weight\+' кг':s\.weight,disabled:s\.bw,onChange:e=>\{setField\(ei,si,'weight',e\.target\.value\);setField\(ei,si,'bw',false\)\}\}\),
                React\.createElement\('input',\{className:'set-input',type:'number',inputMode:'numeric',placeholder:s\.prevReps\|\|'12',value:s\.reps,onChange:e=>setField\(ei,si,'reps',e\.target\.value\)\}\),
                si>0\?React\.createElement\('button',\{className:'timer-btn-inline',onClick:\(\)=>setShowTimerPopup\(\{ei,si\}\)\},React\.createElement\(TimerIcon,\{size:14\}\)\):null,
                ex\.sets\.length>1\?React\.createElement\('button',\{className:'set-del-btn',onClick:\(\)=>rmSet\(ei,si\)\},React\.createElement\(XIcon\)\):React\.createElement\('div'\)"""

new_set_row = r"""                React.createElement('input',{className:'set-input',type:s.bw?'text':'number',inputMode:'decimal',placeholder:s.prevWeight||'кг',value:s.bw?s.weight+' кг':s.weight,disabled:s.bw,onChange:e=>{setField(ei,si,'weight',e.target.value);setField(ei,si,'bw',false)}}),
                React.createElement('div', {style:{color:'var(--text3)', fontSize:'12px', fontWeight:'700', textAlign:'center', marginTop:'2px'}}, '✕'),
                React.createElement('input',{className:'set-input',type:'number',inputMode:'numeric',placeholder:s.prevReps||'12',value:s.reps,onChange:e=>setField(ei,si,'reps',e.target.value)}),
                si>0?React.createElement('button',{className:'timer-btn-inline',onClick:()=>setShowTimerPopup({ei,si})},React.createElement(TimerIcon,{size:14})):React.createElement('div'),
                si>0?React.createElement('button',{className:'set-del-btn',onClick:()=>rmSet(ei,si)},React.createElement(XIcon)):React.createElement('div')"""

js = re.sub(old_set_row, new_set_row, js)

# Also fix sets-header to align correctly.
# Currently: React.createElement('span',null,'Вага'), React.createElement('span',null,'Повтори'), React.createElement('span',null,'')
# But it's styled with .sets-header which is grid. Let's find it in CSS first.
with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

# Replace set-row grid
old_css_set_row = r"\.set-row\{display:grid;grid-template-columns:30px 1fr 1fr 32px 28px;gap:5px;margin-bottom:5px;align-items:center\}\n\.set-row\.set-row-first\{grid-template-columns:30px 1fr 1fr 28px\}"
new_css_set_row = r".set-row{display:grid;grid-template-columns:30px 1fr 16px 1fr 32px 28px;gap:5px;margin-bottom:5px;align-items:center}\n.set-row.set-row-first{grid-template-columns:30px 1fr 16px 1fr 32px 28px}"
css = re.sub(old_css_set_row, new_css_set_row, css)

# Replace sets-header grid
old_css_header = r"\.sets-header\{display:grid;grid-template-columns:30px 1fr 1fr 28px;gap:5px;margin-bottom:8px;font-size:10px;font-weight:700;color:var\(--text3\);text-transform:uppercase;letter-spacing:0\.5px;padding-left:4px\}"
new_css_header = r".sets-header{display:grid;grid-template-columns:30px 1fr 16px 1fr 32px 28px;gap:5px;margin-bottom:8px;font-size:10px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;padding-left:4px}"
css = re.sub(old_css_header, new_css_header, css)

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)

print("Updates applied.")
