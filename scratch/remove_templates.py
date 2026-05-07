import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Pattern to find the specific button element
pattern = r"React\.createElement\('button',\{className:'save-btn',style:\{marginTop:'8px',background:'var\(--bg3\)',color:'var\(--text1\)'\},onClick:\(\)=>\{[\s\S]*?\}\s*\},'Зберегти як шаблон'\),"

new_js = re.sub(pattern, "", js)

if js == new_js:
    print("Warning: Pattern not found!")
else:
    with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
        f.write(new_js)
    print("Template button removed.")
