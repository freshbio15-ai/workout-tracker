import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Remove Easter Egg State and add adminTaps
js = re.sub(
    r"const \[showEasterEgg, setShowEasterEgg\] = React\.useState\(false\);",
    r"const [adminTaps, setAdminTaps] = React.useState({logo: false, sync: false});",
    js
)

# Remove Easter Egg render block
easter_egg_render = r"showEasterEgg && React\.createElement\('div',\{className:'cc-overlay',onClick:\(\)=>setShowEasterEgg\(false\)\},\s*React\.createElement\('img',\{src:'assets/easter_egg\.jpg', style:\{maxWidth:'90%',maxHeight:'90%',borderRadius:'10px'\}\}\)\s*\)"
js = re.sub(easter_egg_render, r"null", js)

# Logo onClick update
logo_click = r"className:'logo-icon', onClick:\(\)=>setShowEasterEgg\(true\)"
new_logo_click = r"className:'logo-icon', onClick:()=>setAdminTaps(p=>({...p, logo: true}))"
js = re.sub(logo_click, new_logo_click, js)

# Sync onClick update
cloud_status = r"React\.createElement\('div',\{className:'cloud-status'\}"
new_cloud_status = r"React.createElement('div',{className:'cloud-status', style:{cursor:tab==='settings'?'pointer':'default'}, onClick:()=>{if(tab==='settings'&&adminTaps.logo)setAdminTaps(p=>({...p,sync:true}))}}"
js = re.sub(cloud_status, new_cloud_status, js)


# 2. Add getLatestWeight helper inside App component (right after useStates)
get_latest_w = r"""  function getLatestWeight() {
    if(!settings.weightHistory) return null;
    const dates = Object.keys(settings.weightHistory).sort();
    if(dates.length === 0) return null;
    return settings.weightHistory[dates[dates.length - 1]];
  }"""
js = js.replace("const [showAdminModal, setShowAdminModal] = React.useState(false);", "const [showAdminModal, setShowAdminModal] = React.useState(false);\n" + get_latest_w)


# 3. Update toggleBW logic
old_toggle_bw = r"""  function toggleBW\(ei\)\{
    setDraft\(p=>\(\{\.\.\.p,exercises:p\.exercises\.map\(\(e,i\)=>\{
      if\(i!==ei\) return e;
      const allBw = e\.sets\.every\(s=>s\.bw\);
      const newBw = !allBw;
      return \{\.\.\.e, sets: e\.sets\.map\(s=>\(\{\.\.\.s, bw: newBw, weight: newBw \? \(settings\.userWeight\|\|''\) : ''\}\)\)\}
    \}\)\}\)\);
  \}"""
new_toggle_bw = r"""  function toggleBW(ei){
    const latestW = getLatestWeight();
    if(!latestW){
      flash('Вкажи свою вагу в Аналітиці');
      setTab('analytics');
      return;
    }
    setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>{
      if(i!==ei) return e;
      const allBw = e.sets.every(s=>s.bw);
      const newBw = !allBw;
      return {...e, sets: e.sets.map(s=>({...s, bw: newBw, weight: newBw ? latestW : ''}))}
    })}));
  }"""
js = re.sub(old_toggle_bw, new_toggle_bw, js)


# 4. Update saveDay BW weight resolution
old_save_bw = r"weight:s\.bw\?Number\(settings\.userWeight\)\|\|0:Number\(s\.weight\)\|\|0"
new_save_bw = r"weight:s.bw?Number(getLatestWeight())||0:Number(s.weight)||0"
js = re.sub(old_save_bw, new_save_bw, js)


# 5. Remove "Минулого разу" text
old_prev_hint = r"\(\(\)=>\{const ps=ex\.sets\.find\(s=>s\.prevWeight\|\|s\.prevReps\);return ps\?React\.createElement\('div',\{style:\{fontSize:'12px',color:'var\(--text3\)',fontStyle:'italic',marginBottom:'12px',paddingLeft:'4px'\}\},`Минулого разу: \$\{ps\.prevWeight\|\|'\?'\} кг × \$\{ps\.prevReps\|\|'\?'\}`\):null\}\)\(\),"
js = re.sub(old_prev_hint, r"", js)


# 6. Update Placeholders with showPrevPlaceholder logic
old_ph_w = r"placeholder:s\.prevWeight\|\|'кг'"
new_ph_w = r"placeholder:(settings.showPrevPlaceholder !== false && s.prevWeight) ? s.prevWeight : 'кг'"
js = re.sub(old_ph_w, new_ph_w, js)

old_ph_r = r"placeholder:s\.prevReps\|\|'12'"
new_ph_r = r"placeholder:(settings.showPrevPlaceholder !== false && s.prevReps) ? s.prevReps : '12'"
js = re.sub(old_ph_r, new_ph_r, js)


# 7. Rewrite renderSettings (Remove Власна вага, update Інтерфейс, move Desktop hint, update admin block condition)
old_render_settings = r"""        // weight card
        React\.createElement\('div',\{className:'settings-card'\},
          React\.createElement\('h3',null,React\.createElement\('div', \{style:\{display:'flex',alignItems:'center',gap:'8px'\}\}, React\.createElement\('div',\{style:\{display:'flex',alignItems:'center',marginTop:'-1px'\}\},React\.createElement\(WeightIcon\)\), 'Власна вага'\)\),
          React\.createElement\('p',null,'Ця вага буде автоматично підставлена, коли ти натиснеш кнопку «СВ» біля підходу'\),
          React\.createElement\('input',\{className:'settings-input',type:'number',inputMode:'decimal',placeholder:'Наприклад 75',value:settings\.userWeight,
            onChange:e=>setSettings\(s=>\(\{\.\.\.s,userWeight:e\.target\.value\}\)\)\}\),
          settings\.userWeight&&React\.createElement\('div',\{className:'weight-display'\},
            React\.createElement\('div',\{style:\{fontSize:'14px',color:'var\(--green2\)',fontWeight:700\}\},settings\.userWeight\+' кг'\),
            React\.createElement\('span',null,'— збережено'\)
          \)
        \),
        // info
        React\.createElement\('div',\{className:'settings-card'\},
          React\.createElement\('h3',null,'Інтерфейс'\),
          React\.createElement\('label',\{style:\{display:'flex',alignItems:'center',gap:'8px',cursor:'pointer',marginBottom:'16px'\}\},
            React\.createElement\('input',\{type:'checkbox',checked:settings\.showBwToggle!==false,onChange:e=>setSettings\(s=>\(\{\.\.\.s,showBwToggle:e\.target\.checked\}\)\)\}\),
            React\.createElement\('span',\{style:\{fontSize:'14px',color:'var\(--text2\)'\}\},'Кнопка «Вправа зі своєю вагою»'\)
          \),
          React\.createElement\('h3',null,React\.createElement\('div', \{style:\{display:'flex',alignItems:'center',gap:'8px'\}\}, React\.createElement\('div',\{style:\{display:'flex',alignItems:'center',marginTop:'-1px'\}\},React\.createElement\(SmartphoneIcon\)\), 'Як зберегти на робочий стіл'\)\),
          React\.createElement\('p',\{style:\{lineHeight:'1\.6'\}\},
            'У Safari натисни кнопку «Поділитися» \(квадрат зі стрілкою\) → «На початковий екран»\. Апка буде працювати як повноцінний додаток з відповідною іконкою'
          \)
        \),
        // admin panel
        \(settings\.userWeight === '175' \|\| localStorage\.getItem\('override_uid'\)\) && React\.createElement\('div',\{className:'settings-card'\},"""

new_render_settings = r"""        // info
        React.createElement('div',{className:'settings-card'},
          React.createElement('h3',null,'Інтерфейс'),
          React.createElement('label',{style:{display:'flex',alignItems:'center',gap:'8px',cursor:'pointer',marginBottom:'12px'}},
            React.createElement('input',{type:'checkbox',checked:settings.showBwToggle!==false,onChange:e=>setSettings(s=>({...s,showBwToggle:e.target.checked}))}),
            React.createElement('span',{style:{fontSize:'14px',color:'var(--text2)'}},'Кнопка «Вправа зі своєю вагою»')
          ),
          React.createElement('label',{style:{display:'flex',alignItems:'center',gap:'8px',cursor:'pointer',marginBottom:'4px'}},
            React.createElement('input',{type:'checkbox',checked:settings.showPrevPlaceholder!==false,onChange:e=>setSettings(s=>({...s,showPrevPlaceholder:e.target.checked}))}),
            React.createElement('span',{style:{fontSize:'14px',color:'var(--text2)'}},'Показувати попередній результат (як підказку)')
          )
        ),
        React.createElement('div',{className:'settings-card'},
          React.createElement('h3',null,React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'8px'}}, React.createElement('div',{style:{display:'flex',alignItems:'center',marginTop:'-1px'}},React.createElement(SmartphoneIcon)), 'Як зберегти на робочий стіл')),
          React.createElement('p',{style:{lineHeight:'1.6', marginBottom:0}},
            'У Safari натисни кнопку «Поділитися» (квадрат зі стрілкою) → «На початковий екран». Апка буде працювати як повноцінний додаток з відповідною іконкою'
          )
        ),
        // admin panel
        ((adminTaps.logo && adminTaps.sync) || localStorage.getItem('override_uid')) && React.createElement('div',{className:'settings-card'},"""

js = re.sub(old_render_settings, new_render_settings, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Refactor complete.")
