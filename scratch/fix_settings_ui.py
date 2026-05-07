import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Update the UserName input and remove the green text
old_name_block = r"""          React\.createElement\('input',\{className:'settings-input',type:'text',placeholder:'Наприклад: Іван',value:settings\.userName\|\|'',
            onChange:e=>setSettings\(s=>\(\{\.\.\.s,userName:e\.target\.value\}\)\)\}\),
          settings\.userName&&React\.createElement\('div',\{className:'weight-display'\},
            React\.createElement\('div',\{style:\{fontSize:'14px',color:'var\(--green2\)',fontWeight:700\}\},settings\.userName\),
            React\.createElement\('span',null,'— збережено'\)
          \)"""

new_name_block = r"""          React.createElement('input',{className:'settings-input',type:'text',placeholder:'Наприклад: Іван',value:settings.userName||'',
            onChange:e=>setSettings(s=>({...s,userName:e.target.value})),
            onBlur:()=>flash('Ім\'я збережено')})"""

js = re.sub(old_name_block, new_name_block, js)

# 2. Update the Desktop hint styling (add marginTop)
old_p_desktop = r"React\.createElement\('p',\{style:\{lineHeight:'1\.6', marginBottom:0\}\},"
new_p_desktop = r"React.createElement('p',{style:{lineHeight:'1.6', marginBottom:0, marginTop:'8px'}},"

js = re.sub(old_p_desktop, new_p_desktop, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Settings UI updated.")
