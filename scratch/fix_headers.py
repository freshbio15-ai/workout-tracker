import re

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

# Fix sets-header grid alignment
old_header_css = ".sets-header{display:grid;grid-template-columns:40px 1fr 1fr 40px;gap:8px;padding:0 4px;margin-bottom:8px;font-size:11px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:1px}"
new_header_css = ".sets-header{display:grid;grid-template-columns:30px 1fr 1fr 28px;gap:5px;margin-bottom:8px;font-size:11px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:1px;text-align:center}\n.sets-header span:first-child{text-align:center; display:flex; align-items:center; justify-content:center}"

if old_header_css in css:
    css = css.replace(old_header_css, new_header_css)
else:
    print("Failed to find sets-header in css")

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)


with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

old_js_header = """            React.createElement('div',{className:'sets-header'},
              React.createElement('span',null,'Сет'),React.createElement('span',null,'Вага'),React.createElement('span',null,'Повт.'),React.createElement('span',null,'')
            ),"""

new_js_header = """            React.createElement('div',{className:'sets-header'},
              React.createElement('span', {style:{color:'var(--text2)'}}, (() => {
                const mg = MUSCLES.find(m => m.id === ex.muscle);
                return mg ? mg.label : 'Сет';
              })()),
              React.createElement('span',null,'Вага'),
              React.createElement('span',null,'Повт.'),
              React.createElement('span',null,'')
            ),"""

if old_js_header in js:
    js = js.replace(old_js_header, new_js_header)
else:
    print("Failed to find sets-header in js")

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Headers updated")
