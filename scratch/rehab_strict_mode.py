import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Define Rehab exercises at the top of the file
rehab_ex_def = r"""const REHAB_EXERCISES = [
  'Диафрагмальне дихання (хвилин)',
  'Прогулянка (хвилин/кроків)',
  'Нахили тазу (Pelvic Tilts)',
  'Вправа "Кішка-Корова" (Cat-Cow)',
  'Сідничний місток (Glute Bridge)',
  'Вправа "Мертвий жук" (Dead Bug)',
  'Стаціонарний велосипед (низький опір)',
  'Робота з гумками (Light Resistance Band)'
];"""

js = js.replace("const MONTHS = ['Січень'", rehab_ex_def + "\nconst MONTHS = ['Січень'")

# 2. Modify the exercise name input (around line 453)
old_name_input = r"React\.createElement\('input',\{className:'ex-name-input',placeholder:'Назва вправи…',value:ex\.name,onChange:e=>setExName\(ei,e\.target\.value\)\}\),"

new_name_input = r"""settings.rehab?.active ? React.createElement('select', {
                className: 'ex-name-input',
                value: ex.name,
                onChange: e => setExName(ei, e.target.value),
                style: { appearance: 'none', background: 'var(--bg3)', color: 'var(--accent2)', fontWeight: 'bold' }
              }, 
                React.createElement('option', {value: '', disabled: true}, 'Оберіть вправу...'),
                REHAB_EXERCISES.map(re => React.createElement('option', {key: re, value: re}, re))
              ) : React.createElement('input',{className:'ex-name-input',placeholder:'Назва вправи…',value:ex.name,onChange:e=>setExName(ei,e.target.value)}),"""

js = re.sub(old_name_input, new_name_input, js)

# 3. Add Warning Banner and Modify Sets Header
# Find sets-header
old_sets_header = r"React\.createElement\('div',\{className:'sets-header'\},[\s\S]*?React\.createElement\('span',null,'Вага'\),"

new_sets_header = r"""settings.rehab?.active && React.createElement('div', {className: 'rehab-warning'}, '⚠️ Увага: працюй на 50% сили. Жодних потуг та затримок дихання!'),
            React.createElement('div',{className:'sets-header'},
              React.createElement('span', {style:{color:'var(--text2)', whiteSpace:'nowrap', overflow:'visible', position:'relative', zIndex:5, textTransform:'uppercase'}}, (() => {
                const mg = MUSCLES.find(m => m.id === ex.muscle);
                return mg ? mg.label : 'Сет';
              })()),
              React.createElement('span',null, settings.rehab?.active ? 'Час/Інтенс.' : 'Вага'),"""

js = re.sub(old_sets_header, new_sets_header, js)

# 4. Modify Set Input (weight column)
old_set_input = r"React\.createElement\('input',\{className:'set-input',type:s\.bw\?'text':'number',inputMode:'decimal',placeholder:s\.prevWeight\|\|'кг',value:s\.bw\?s\.weight\+' кг':s\.weight,disabled:s\.bw,onChange:e=>\{setField\(ei,si,'weight',e\.target\.value\);setField\(ei,si,'bw',false\)\}\}\),"

new_set_input = r"""React.createElement('input',{className:'set-input',type:(s.bw || settings.rehab?.active)?'text':'number',inputMode:settings.rehab?.active?'text':'decimal',placeholder:settings.rehab?.active?'хв/інт':(s.prevWeight||'кг'),value:s.bw?s.weight+' кг':s.weight,disabled:s.bw,onChange:e=>{setField(ei,si,'weight',e.target.value);setField(ei,si,'bw',false)}}),"""

js = re.sub(old_set_input, new_set_input, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Strict mode implemented.")
