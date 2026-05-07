import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Replace customization and desktop card with the combined card
old_block = r"""        React\.createElement\('div',\{className:'settings-card'\},
          React\.createElement\('h3',null,'🎨 Кастомізація'\),
          React\.createElement\('p',null,'Вибери іконку додатку для робочого столу'\),
          React\.createElement\('div',\{style:\{display:'flex',gap:'12px',marginTop:'12px',overflowX:'auto',paddingBottom:'8px'\}\},
            \['icon_book\.png', 'icon_neon\.png', 'icon_wave\.png'\]\.map\(icon => 
              React\.createElement\('div',\{
                key:icon,
                onClick:\(\)=>\{
                  setSettings\(s=>\(\{\.\.\.s,appIcon:icon\}\)\);
                  const linkApple = document\.getElementById\('dynamic-apple-icon'\);
                  const linkIcon = document\.getElementById\('dynamic-icon'\);
                  if\(linkApple\) linkApple\.href = `assets/\$\{icon\}`;
                  if\(linkIcon\) linkIcon\.href = `assets/\$\{icon\}`;
                  flash\('Іконку змінено'\);
                \},
                style:\{
                  minWidth:'60px',width:'60px',height:'60px',borderRadius:'16px',
                  border:settings\.appIcon===icon\?'2px solid var\(--green2\)':'2px solid transparent',
                  background:`url\(assets/\$\{icon\}\) center/cover`,
                  cursor:'pointer',
                  opacity:\(settings\.appIcon===icon \|\| \(!settings\.appIcon && icon==='icon_book\.png'\)\)\?1:0\.6,
                  transition:'all \.2s'
                \}
              \}\)
            \)
          \)
        \),
        React\.createElement\('div',\{className:'settings-card'\},
          React\.createElement\('h3',null,React\.createElement\('div', \{style:\{display:'flex',alignItems:'center',gap:'8px'\}\}, React\.createElement\('div',\{style:\{display:'flex',alignItems:'center',marginTop:'-1px'\}\},React\.createElement\(SmartphoneIcon\)\), 'Як зберегти на робочий стіл'\)\),
          React\.createElement\('p',\{style:\{lineHeight:'1\.6', marginBottom:0, marginTop:'8px'\}\},
            'У Safari натисни кнопку «Поділитися» \(квадрат зі стрілкою\) → «На початковий екран»\. Апка буде працювати як повноцінний додаток з відповідною іконкою'
          \)
        \),"""

new_block = r"""        React.createElement('div',{className:'settings-card', style:{display:'flex',gap:'16px',alignItems:'center'}},
          React.createElement('div', {style:{flex:1}},
            React.createElement('h3',null,React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'8px'}}, React.createElement('div',{style:{display:'flex',alignItems:'center',marginTop:'-1px'}},React.createElement(SmartphoneIcon)), 'На робочий стіл')),
            React.createElement('p',{style:{lineHeight:'1.5', marginBottom:0, marginTop:'8px', fontSize:'13px'}},
              'У Safari натисни «Поділитися» (квадрат зі стрілкою) → «На початковий екран». Апка працюватиме як повноцінний додаток з цією іконкою.'
            )
          ),
          React.createElement('img', {src:'assets/icon_book.png', style:{width:'64px',height:'64px',borderRadius:'16px',boxShadow:'0 4px 12px rgba(0,0,0,0.3)', flexShrink:0}})
        ),"""

js = re.sub(old_block, new_block, js)

# 2. Remove the dynamic icon useEffect
old_effect = r"""  React\.useEffect\(\(\)=>\{if\(toast\)setTimeout\(\(\)=>setToast\(null\),2000\)\},\[toast\]\);
  React\.useEffect\(\(\)=>\{
    if\(settings\.appIcon\) \{
      const linkApple = document\.getElementById\('dynamic-apple-icon'\);
      const linkIcon = document\.getElementById\('dynamic-icon'\);
      if\(linkApple\) linkApple\.href = `assets/\$\{settings\.appIcon\}`;
      if\(linkIcon\) linkIcon\.href = `assets/\$\{settings\.appIcon\}`;
    \}
  \}, \[settings\.appIcon\]\);"""

new_effect = r"  React.useEffect(()=>{if(toast)setTimeout(()=>setToast(null),2000)},[toast]);"

js = re.sub(old_effect, new_effect, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Settings updated.")
