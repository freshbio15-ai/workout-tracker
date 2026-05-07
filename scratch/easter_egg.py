import re

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

# Make header symmetrical
css = css.replace("justify-content:center;", "justify-content:space-between;")
with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. 'Повт.' -> 'Повтори' in sets header
old_header = """              React.createElement('span',null,'Вага'),
              React.createElement('span',null,'Повт.'),
              React.createElement('span',null,'')"""
new_header = """              React.createElement('span',null,'Вага'),
              React.createElement('span',null,'Повтори'),
              React.createElement('span',null,'')"""
js = js.replace(old_header, new_header)

# 2. Add BW toggle setting
old_bw = "React.createElement('button',{className:'bw-toggle-btn'+(ex.sets[0].bw?' active':'')"
new_bw = "settings.showBwToggle !== false && React.createElement('button',{className:'bw-toggle-btn'+(ex.sets[0].bw?' active':'')"
js = js.replace(old_bw, new_bw)

old_settings = "React.createElement('h3',null,React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'8px'}}, React.createElement(SmartphoneIcon), 'Як зберегти на робочий стіл')),"
new_settings = """React.createElement('h3',null,'Інтерфейс'),
          React.createElement('label',{style:{display:'flex',alignItems:'center',gap:'8px',cursor:'pointer',marginBottom:'16px'}},
            React.createElement('input',{type:'checkbox',checked:settings.showBwToggle!==false,onChange:e=>setSettings(s=>({...s,showBwToggle:e.target.checked}))}),
            React.createElement('span',{style:{fontSize:'14px',color:'var(--text2)'}},'Кнопка «Вправа зі своєю вагою»')
          ),
          React.createElement('h3',null,React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'8px'}}, React.createElement(SmartphoneIcon), 'Як зберегти на робочий стіл')),"""
js = js.replace(old_settings, new_settings)

# 3. Add showEasterEgg state
old_state = "const [showBwPicker, setShowBwPicker] = useState(false);"
new_state = "const [showBwPicker, setShowBwPicker] = useState(false);\n  const [showEasterEgg, setShowEasterEgg] = useState(false);"
js = js.replace(old_state, new_state)

# 4. Make logo clickable
old_logo = "React.createElement('div',{className:'logo-icon'},React.createElement(ActivityIcon, {size: 20})),"
new_logo = "React.createElement('div',{className:'logo-icon', onClick:()=>setShowEasterEgg(true), style:{cursor:'pointer'}},React.createElement(ActivityIcon, {size: 20})),"
js = js.replace(old_logo, new_logo)

# 5. Render Easter Egg modal
old_render = "showTimerPopup && React.createElement('div',{className:'cc-overlay',onClick:()=>setShowTimerPopup(false)},"
new_render = """showEasterEgg && React.createElement('div',{className:'cc-overlay',onClick:()=>setShowEasterEgg(false)},
        React.createElement('img',{src:'assets/easter_egg.jpg', style:{maxWidth:'90%',maxHeight:'90vh',borderRadius:'12px',objectFit:'contain'}, onClick:e=>e.stopPropagation()})
      ),
      showTimerPopup && React.createElement('div',{className:'cc-overlay',onClick:()=>setShowTimerPopup(false)},"""
js = js.replace(old_render, new_render)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Updates done")

