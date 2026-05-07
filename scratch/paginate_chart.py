import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Add state
js = js.replace("const [bwPickerYear, setBwPickerYear] = useState(new Date().getFullYear());",
                "const [bwPickerYear, setBwPickerYear] = useState(new Date().getFullYear());\n  const [weightPage, setWeightPage] = useState(0);")

# 2. Update renderAnalytics logic
# Search for Weight Tracker logic
old_logic = r"""    const weightHistory = settings\.weightHistory \|\| \{\};
    const weightKeys = Object\.keys\(weightHistory\)\.sort\(\)\.slice\(-15\);
    const weightChartData = weightKeys\.map\(k => \(\{ date: k, weight: bwUnit === 'lbs' \? \(weightHistory\[k\] / 0\.453592\) : weightHistory\[k\] \}\)\);"""

new_logic = r"""    const weightHistory = settings.weightHistory || {};
    const allWeightKeys = Object.keys(weightHistory).sort();
    const totalWPages = Math.ceil(allWeightKeys.length / 10);
    const wStart = Math.max(0, allWeightKeys.length - (weightPage + 1) * 10);
    const wEnd = allWeightKeys.length - weightPage * 10;
    const weightKeys = allWeightKeys.slice(wStart, wEnd);
    const weightChartData = weightKeys.map(k => ({ date: k, weight: bwUnit === 'lbs' ? (weightHistory[k] / 0.453592) : weightHistory[k] }));"""

js = re.sub(old_logic, new_logic, js)

# 3. Add pagination buttons to the UI
# Search for chart-title of weight tracker
old_header = r"""              `Динаміка власної ваги \(\$\{bwUnit\}\)`,
              React\.createElement\('button', \{onClick:()=>\{if\(confirm\('Видалити всю історію ваги\?'\)\)\{setSettings\(s=>\(\{\.\.\.s, weightHistory:\{\}\}\)\); flash\('Історію очищено'\);\}\}, style:\{background:'none',border:'none',color:'var\(--red\)',fontSize:'12px',cursor:'pointer'\}\}, 'Стерти все'\)
            \),"""

new_header = r"""              React.createElement('div', {style:{display:'flex', alignItems:'center', gap:'8px'}},
                `Вага (${bwUnit})`,
                allWeightKeys.length > 10 && React.createElement('div', {style:{display:'flex', gap:'4px'}},
                  React.createElement('button', {onClick:()=>setWeightPage(p=>Math.min(p+1, totalWPages-1)), disabled: weightPage >= totalWPages-1, style:{background:'var(--bg4)', border:'1px solid var(--border)', color: weightPage >= totalWPages-1 ? 'var(--text3)' : 'var(--text1)', padding:'2px 6px', borderRadius:'4px', cursor:'pointer'}}, React.createElement(ArrowLeftIcon, {size:12})),
                  React.createElement('button', {onClick:()=>setWeightPage(p=>Math.max(0, p-1)), disabled: weightPage === 0, style:{background:'var(--bg4)', border:'1px solid var(--border)', color: weightPage === 0 ? 'var(--text3)' : 'var(--text1)', padding:'2px 6px', borderRadius:'4px', cursor:'pointer'}}, React.createElement(ArrowRightIcon, {size:12}))
                )
              ),
              React.createElement('button', {onClick:()=>{if(confirm('Видалити всю історію ваги?')){setSettings(s=>({...s, weightHistory:{}})); setWeightPage(0); flash('Історію очищено');}}, style:{background:'none',border:'none',color:'var(--red)',fontSize:'12px',cursor:'pointer'}}, 'Стерти все')
            ),"""

js = re.sub(old_header, new_header, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Pagination added.")
