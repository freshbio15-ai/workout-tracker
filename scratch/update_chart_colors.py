import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Pattern to find the map call for weightChartData
old_code = r"""weightChartData\.map\(\(d, i\) => \{
              const h = Math\.max\(5, Math\.round\(\(\(d\.weight - wBase\) / \(wMax - wBase \+ wRange\*0\.2\)\) \* 100\)\);
              return React\.createElement\('div', \{key: i, className: 'chart-col', style:\{cursor:'pointer'\}, onClick:\(\)=>\{
                const nw = prompt\(`Змінити вагу за \$\{fmtShort\(d\.date\)\} \(\$\{bwUnit\}\)\?\\nВведіть нове значення \(або залиште порожнім щоб видалити\):`, d\.weight % 1 === 0 \? d\.weight : d\.weight\.toFixed\(3\)\);
                if \(nw !== null\) \{
                  if \(nw\.trim\(\) === ''\) \{
                    setSettings\(s => \{ const ns = \{\.\.\.s, weightHistory: \{\.\.\.\(s\.weightHistory\|\|\{\)\}\}; delete ns\.weightHistory\[d\.date\]; return ns; \}\);
                    flash\('Запис видалено'\);
                  \} else \{
                    let val = Number\(nw\);
                    if \(!isNaN\(val\) && val > 0\) \{
                      if \(bwUnit === 'lbs'\) val = val \* 0\.453592;
                      setSettings\(s => \(\{\.\.\.s, weightHistory: \{\.\.\.\(s\.weightHistory\|\|\{\)\, \[d\.date\]: val\}\}\)\);
                      flash\('Запис оновлено'\);
                    \}
                  \}
                \}
              \}\,
                React\.createElement\('div', \{className: 'chart-value', style:\{color:'var\(--green2\)'\}\}, d\.weight % 1 === 0 \? d\.weight : d\.weight\.toFixed\(3\)\),
                React\.createElement\('div', \{className: 'chart-bar', style: \{height: '100%'\}\},
                  React\.createElement\('div', \{className: 'chart-bar-fill', style: \{height: h \+ '%', background:'linear-gradient\(to top, var\(--green\), var\(--green2\)\)', boxShadow:'0 0 10px rgba\(16,185,129,0.3\)'\}\}\)
                \),
                React\.createElement\('div', \{className: 'chart-label'\}, fmtShort\(d\.date\)\)
              \);
            \}\)"""

new_code = r"""weightChartData.map((d, i) => {
              const h = Math.max(5, Math.round(((d.weight - wBase) / (wMax - wBase + wRange*0.2)) * 100));
              const prev = i > 0 ? weightChartData[i-1].weight : d.weight;
              const isDrop = d.weight < prev;
              const barColor = isDrop ? 'linear-gradient(to top, var(--green), var(--red))' : 'linear-gradient(to top, rgba(16,185,129,0.4), var(--green2))';
              const glowColor = isDrop ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)';
              const valColor = isDrop ? 'var(--red)' : 'var(--green2)';
              
              return React.createElement('div', {key: i, className: 'chart-col', style:{cursor:'pointer'}, onClick:()=>{
                const nw = prompt(`Змінити вагу за ${fmtShort(d.date)} (${bwUnit})?\nВведіть нове значення (або залиште порожнім щоб видалити):`, d.weight % 1 === 0 ? d.weight : d.weight.toFixed(3));
                if (nw !== null) {
                  if (nw.trim() === '') {
                    setSettings(s => { const ns = {...s, weightHistory: {...(s.weightHistory||{})}}; delete ns.weightHistory[d.date]; return ns; });
                    flash('Запис видалено');
                  } else {
                    let val = Number(nw);
                    if (!isNaN(val) && val > 0) {
                      if (bwUnit === 'lbs') val = val * 0.453592;
                      setSettings(s => ({...s, weightHistory: {...(s.weightHistory||{}), [d.date]: val}}));
                      flash('Запис оновлено');
                    }
                  }
                }
              }},
                React.createElement('div', {className: 'chart-value', style:{color:valColor}}, d.weight % 1 === 0 ? d.weight : d.weight.toFixed(3)),
                React.createElement('div', {className: 'chart-bar', style: {height: '100%'}},
                  React.createElement('div', {className: 'chart-bar-fill', style: {height: h + '%', background: barColor, boxShadow: `0 0 10px ${glowColor}`}})
                ),
                React.createElement('div', {className: 'chart-label'}, fmtShort(d.date))
              );
            })"""

new_js = re.sub(old_code, new_code, js)

if js == new_js:
    print("Warning: Pattern not found!")
else:
    with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
        f.write(new_js)
    print("Chart colors updated successfully.")
