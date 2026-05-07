import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Pattern for the map function inside weightChartData
# We need to be careful with the lines we view previously.
# Line 826 start.

old_code = r"""            weightChartData\.map\(\(d, i\) => \{
              const h = Math\.max\(5, Math\.round\(\(\(d\.weight - wBase\) / \(wMax - wBase \+ wRange\*0\.2\)\) \* 100\)\);
              const prev = i > 0 \? weightChartData\[i-1\]\.weight : d\.weight;
              const isDrop = d\.weight < prev;
              const barColor = isDrop \? 'linear-gradient\(to top, var\(--green\), var\(--red\)\)' : 'linear-gradient\(to top, rgba\(16,185,129,0.4\), var\(--green2\)\)';
              const glowColor = isDrop \? 'rgba\(239,68,68,0.3\)' : 'rgba\(16,185,129,0.3\)';
              const valColor = isDrop \? 'var\(--red\)' : 'var\(--green2\)';
              
              return React\.createElement\('div', \{key: i, className: 'chart-col', style:\{cursor:'pointer'\}, onClick:\(\)=>\{"""

new_code = r"""            weightChartData.map((d, i) => {
              const h = Math.max(5, Math.round(((d.weight - wBase) / (wMax - wBase + wRange*0.2)) * 100));
              const prev = i > 0 ? weightChartData[i-1].weight : d.weight;
              const isDrop = d.weight < prev;
              const isGain = d.weight > prev;
              
              const barColor = isDrop ? 'linear-gradient(to top, var(--green), var(--red))' : 
                               (isGain ? 'linear-gradient(to top, var(--red), var(--green2))' : 
                               'linear-gradient(to top, rgba(16,185,129,0.4), var(--green2))');
                               
              const glowColor = isDrop ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)';
              const valColor = isDrop ? 'var(--red)' : (isGain ? 'var(--green2)' : 'var(--text3)');
              const displayWeight = d.weight % 1 === 0 ? d.weight : parseFloat(d.weight.toFixed(2));
              
              return React.createElement('div', {key: i, className: 'chart-col', style:{cursor:'pointer'}, onClick:()=>{"""

# Also replace the value rendering line
old_val = r"""React\.createElement\('div', \{className: 'chart-value', style:\{color:valColor\}\}, d\.weight % 1 === 0 \? d\.weight : d\.weight\.toFixed\(3\)\)"""
new_val = r"""React.createElement('div', {className: 'chart-value', style:{color:valColor, fontSize:'9px', top:'-18px', whiteSpace:'nowrap'}}, displayWeight)"""

js = re.sub(old_code, new_code, js)
js = re.sub(old_val, new_val, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Chart refined.")
