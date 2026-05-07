with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if 'weightChartData.map((d, i) => {' in line:
        start_idx = i
    if start_idx != -1 and '})' in line and i > start_idx:
        # Looking for the closing of the map function
        # The map function ends at line 850 in the previous view_file
        # which is React.createElement(...) structure
        # Let's be more precise
        if i >= 849: # Based on the view_file output
             end_idx = i
             break

if start_idx != -1 and end_idx != -1:
    new_lines = lines[:start_idx]
    new_lines.append("            weightChartData.map((d, i) => {\n")
    new_lines.append("              const h = Math.max(5, Math.round(((d.weight - wBase) / (wMax - wBase + wRange*0.2)) * 100));\n")
    new_lines.append("              const prev = i > 0 ? weightChartData[i-1].weight : d.weight;\n")
    new_lines.append("              const isDrop = d.weight < prev;\n")
    new_lines.append("              const barColor = isDrop ? 'linear-gradient(to top, var(--green), var(--red))' : 'linear-gradient(to top, rgba(16,185,129,0.4), var(--green2))';\n")
    new_lines.append("              const glowColor = isDrop ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)';\n")
    new_lines.append("              const valColor = isDrop ? 'var(--red)' : 'var(--green2)';\n")
    new_lines.append("              \n")
    new_lines.append("              return React.createElement('div', {key: i, className: 'chart-col', style:{cursor:'pointer'}, onClick:()=>{\n")
    new_lines.append("                const nw = prompt(`Змінити вагу за ${fmtShort(d.date)} (${bwUnit})?\\nВведіть нове значення (або залиште порожнім щоб видалити):`, d.weight % 1 === 0 ? d.weight : d.weight.toFixed(3));\n")
    new_lines.append("                if (nw !== null) {\n")
    new_lines.append("                  if (nw.trim() === '') {\n")
    new_lines.append("                    setSettings(s => { const ns = {...s, weightHistory: {...(s.weightHistory||{})}}; delete ns.weightHistory[d.date]; return ns; });\n")
    new_lines.append("                    flash('Запис видалено');\n")
    new_lines.append("                  } else {\n")
    new_lines.append("                    let val = Number(nw);\n")
    new_lines.append("                    if (!isNaN(val) && val > 0) {\n")
    new_lines.append("                      if (bwUnit === 'lbs') val = val * 0.453592;\n")
    new_lines.append("                      setSettings(s => ({...s, weightHistory: {...(s.weightHistory||{}), [d.date]: val}}));\n")
    new_lines.append("                      flash('Запис оновлено');\n")
    new_lines.append("                    }\n")
    new_lines.append("                  }\n")
    new_lines.append("                }\n")
    new_lines.append("              }},\n")
    new_lines.append("                React.createElement('div', {className: 'chart-value', style:{color:valColor}}, d.weight % 1 === 0 ? d.weight : d.weight.toFixed(3)),\n")
    new_lines.append("                React.createElement('div', {className: 'chart-bar', style: {height: '100%'}},\n")
    new_lines.append("                  React.createElement('div', {className: 'chart-bar-fill', style: {height: h + '%', background: barColor, boxShadow: `0 0 10px ${glowColor}`}})\n")
    new_lines.append("                ),\n")
    new_lines.append("                React.createElement('div', {className: 'chart-label'}, fmtShort(d.date))\n")
    new_lines.append("              );\n")
    new_lines.append("            })\n")
    new_lines.extend(lines[end_idx+1:])
    
    with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
        f.writelines(new_lines)
    print("Success")
else:
    print(f"Error: Indices not found ({start_idx}, {end_idx})")
