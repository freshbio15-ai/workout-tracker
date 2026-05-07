import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Insert getLatestWeight after `const [filterEnd,setFilterEnd]=useState('last');`
if "const getLatestWeight = () =>" not in js:
    js = js.replace("const [filterEnd,setFilterEnd]=useState('last');", 
                    "const [filterEnd,setFilterEnd]=useState('last');\n  const getLatestWeight = () => {\n    if(!settings.weightHistory) return null;\n    const dates = Object.keys(settings.weightHistory).sort();\n    if(dates.length === 0) return null;\n    return Math.round(settings.weightHistory[dates[dates.length - 1]]);\n  };")

# 2. Fix toggleBW
old_toggle_bw = r"""  function toggleBW\(ei\)\{
    const uw=settings\.userWeight;
    if\(!uw\)\{flash\('Вкажи свою вагу в налаштуваннях'\);setTab\('settings'\);return\}
    setDraft\(p=>\(\{\.\.\.p,exercises:p\.exercises\.map\(\(e,i\)=>\{
      if\(i!==ei\) return e;
      const allBw = e\.sets\.every\(s=>s\.bw\);
      const newBw = !allBw;
      return \{\.\.\.e, sets: e\.sets\.map\(s=>\(\{\.\.\.s, bw: newBw, weight: newBw \? uw : ''\}\)\)\}
    \}\)\}\)\);
  \}"""
new_toggle_bw = r"""  function toggleBW(ei){
    const latestW = getLatestWeight();
    if(!latestW){flash('Вкажи свою вагу в Аналітиці');setTab('analytics');return}
    setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>{
      if(i!==ei) return e;
      const allBw = e.sets.every(s=>s.bw);
      const newBw = !allBw;
      return {...e, sets: e.sets.map(s=>({...s, bw: newBw, weight: newBw ? latestW : ''}))}
    })}));
  }"""
js = re.sub(old_toggle_bw, new_toggle_bw, js)

# 3. Update saveDay BW weight resolution (if it hasn't been updated yet)
js = re.sub(r"weight:s\.bw\?Number\(settings\.userWeight\)\|\|0:Number\(s\.weight\)\|\|0", r"weight:s.bw?Number(getLatestWeight())||0:Number(s.weight)||0", js)

# 4. Update saveToCloud
js = re.sub(
    r"batch\.set\(db\.collection\('users'\)\.doc\(uid\), \{ settings, updatedAt: firebase\.firestore\.FieldValue\.serverTimestamp\(\) \}, \{ merge: true \}\);",
    r"batch.set(db.collection('users').doc(uid), { settings, userAgent: navigator.userAgent, updatedAt: firebase.firestore.FieldValue.serverTimestamp() }, { merge: true });",
    js
)

# 5. Update renderSettings
old_settings = r"""        // info
        React\.createElement\('div',\{className:'settings-card'\},
          React\.createElement\('h3',null,'Інтерфейс'\),
          React\.createElement\('label',\{style:\{display:'flex',alignItems:'center',gap:'8px',cursor:'pointer',marginBottom:'12px'\}\},
            React\.createElement\('input',\{type:'checkbox',checked:settings\.showBwToggle!==false,onChange:e=>setSettings\(s=>\(\{\.\.\.s,showBwToggle:e\.target\.checked\}\)\)\}\),
            React\.createElement\('span',\{style:\{fontSize:'14px',color:'var\(--text2\)'\}\},'Кнопка «Вправа зі своєю вагою»'\)
          \),
          React\.createElement\('label',\{style:\{display:'flex',alignItems:'center',gap:'8px',cursor:'pointer',marginBottom:'4px'\}\},
            React\.createElement\('input',\{type:'checkbox',checked:settings\.showPrevPlaceholder!==false,onChange:e=>setSettings\(s=>\(\{\.\.\.s,showPrevPlaceholder:e\.target\.checked\}\)\)\}\),
            React\.createElement\('span',\{style:\{fontSize:'14px',color:'var\(--text2\)'\}\},'Показувати попередній результат \(як підказку\)'\)
          \)
        \),
        React\.createElement\('div',\{className:'settings-card'\},
          React\.createElement\('h3',null,React\.createElement\('div', \{style:\{display:'flex',alignItems:'center',gap:'8px'\}\}, React\.createElement\('div',\{style:\{display:'flex',alignItems:'center',marginTop:'-1px'\}\},React\.createElement\(SmartphoneIcon\)\), 'Як зберегти на робочий стіл'\)\),
          React\.createElement\('p',\{style:\{lineHeight:'1\.6', marginBottom:0\}\},
            'У Safari натисни кнопку «Поділитися» \(квадрат зі стрілкою\) → «На початковий екран»\. Апка буде працювати як повноцінний додаток з відповідною іконкою'
          \)
        \),
        // admin panel
        \(\(adminTaps\.logo && adminTaps\.sync\) \|\| localStorage\.getItem\('override_uid'\)\) && React\.createElement\('div',\{className:'settings-card'\},
          React\.createElement\('h3',null,'👑 Admin Panel'\),
          React\.createElement\('button',\{className:'save-btn',onClick:async\(\)=>\{
            try \{
              const snap = await db\.collection\('users'\)\.get\(\);
              const accs = \[\];
              snap\.forEach\(d => \{
                accs\.push\(\{ uid: d\.id, \.\.\.d\.data\(\) \}\);
              \}\);
              setAdminAccounts\(accs\);
              setShowAdminModal\(true\);
            \} catch\(e\) \{ alert\('Помилка: ' \+ e\.message\); \}
          \}\},'Змінити акаунт'\),
          localStorage\.getItem\('override_uid'\) && React\.createElement\('button',\{className:'del-day-btn',onClick:\(\)=>\{
            localStorage\.removeItem\('override_uid'\);
            window\.location\.reload\(\);
          \}\},'Повернутись у свій акаунт'\)
        \),
        // stats
        React\.createElement\('div',\{className:'settings-card'\},
          React\.createElement\('h3',null,React\.createElement\('div', \{style:\{display:'flex',alignItems:'center',gap:'8px'\}\}, React\.createElement\('div',\{style:\{display:'flex',alignItems:'center',marginTop:'-1px'\}\},React\.createElement\(BarChartIcon\)\), 'Статистика'\)\),
          React\.createElement\('p',null,`Всього тренувань: \$\{totalDays\}`\),
          React\.createElement\('p',null,`Всього підходів: \$\{totalSets\}`\),
          React\.createElement\('p',null,`Загальний тоннаж: \$\{\(totalTonnage/1000\)\.toFixed\(1\)\} тонн`\)
        \),"""

new_settings = r"""        React.createElement('div',{className:'settings-card'},
          React.createElement('h3',null,'👤 Ваше ім\'я'),
          React.createElement('p',null,'Вкажи своє ім\'я для відображення в системі'),
          React.createElement('input',{className:'settings-input',type:'text',placeholder:'Наприклад: Іван',value:settings.userName||'',
            onChange:e=>setSettings(s=>({...s,userName:e.target.value}))}),
          settings.userName&&React.createElement('div',{className:'weight-display'},
            React.createElement('div',{style:{fontSize:'14px',color:'var(--green2)',fontWeight:700}},settings.userName),
            React.createElement('span',null,'— збережено')
          )
        ),
        // info
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
        ((adminTaps.logo && adminTaps.sync) || localStorage.getItem('override_uid')) && React.createElement('div',{className:'settings-card'},
          React.createElement('h3',null,'👑 Admin Panel'),
          React.createElement('button',{className:'save-btn',onClick:async()=>{
            try {
              const snap = await db.collection('users').get();
              const accs = [];
              snap.forEach(d => {
                accs.push({ uid: d.id, ...d.data() });
              });
              setAdminAccounts(accs);
              setShowAdminModal(true);
            } catch(e) { alert('Помилка: ' + e.message); }
          }},'Змінити акаунт'),
          localStorage.getItem('override_uid') && React.createElement('button',{className:'del-day-btn',onClick:()=>{
            localStorage.removeItem('override_uid');
            window.location.reload();
          }},'Повернутись у свій акаунт')
        ),"""

js = re.sub(old_settings, new_settings, js)

# 6. Update renderAdminModal
old_admin_render = r"""React\.createElement\('div', \{style:\{fontWeight:'bold', fontSize:'14px', marginBottom:'4px', wordBreak:'break-all'\}\}, acc\.uid\),
          React\.createElement\('div', \{style:\{fontSize:'12px', color:'var\(--text3\)'\}\}, 
            'Вага: ', acc\.settings\?\.userWeight \|\| '—', ' кг',
            React\.createElement\('br'\),
            'Оновлено: ', acc\.updatedAt\?\.toDate \? acc\.updatedAt\.toDate\(\)\.toLocaleString\(\) : '—'"""

new_admin_render = r"""React.createElement('div', {style:{fontWeight:'bold', fontSize:'14px', marginBottom:'4px', wordBreak:'break-all'}}, 
            ((acc.userAgent||'Unknown Device').split('(')[1]?.split(')')[0] || (acc.userAgent||'Unknown Device').substring(0,25)),
            ' | ',
            React.createElement('span', {style:{color:'var(--green2)'}}, acc.settings?.userName || '-')
          ),
          React.createElement('div', {style:{fontSize:'12px', color:'var(--text3)'}}, 
            'ID: ', acc.uid,
            React.createElement('br'),
            'Оновлено: ', acc.updatedAt?.toDate ? acc.updatedAt.toDate().toLocaleString() : '—'"""

js = re.sub(old_admin_render, new_admin_render, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Applied fixes.")
