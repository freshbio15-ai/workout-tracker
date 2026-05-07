import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Remove the Debug button
debug_pattern = r"React\.createElement\('span', \{style: \{cursor: 'pointer', textDecoration: 'underline'\}, onClick: \(\) => \{\s*const nd = prompt\('Змінити дату \(DEBUG\):', settings\.rehab\.startDate\);\s*if \(nd\) setSettings\(s => \(\{\.\.\.s, rehab: \{\.\.\.s\.rehab, startDate: nd\}\}\)\);\s*\}\}, 'Змінити день \(Debug\)'\),\s*"
js = re.sub(debug_pattern, "", js)

# 2. Hide muscle icons in Rehab Mode
muscle_pattern = r"React\.createElement\('div',\{className:'emoji-muscle-row'\},"
new_muscle = r"!settings.rehab?.active && React.createElement('div',{className:'emoji-muscle-row'},"
js = js.replace(muscle_pattern, new_muscle)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Rehab UI tweaked.")
