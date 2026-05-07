import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Remove calculation block
calc_pattern = r"// Calculate total volume per day for last 10 days[\s\S]*?const maxVol = Math\.max\(\.\.\.chartData\.map\(d => d\.vol\), 1\); // prevent div by 0\s*"
js = re.sub(calc_pattern, "", js)

# 2. Remove rendering block
# Note: we also want to remove the marginTop from the next div
render_pattern = r"React\.createElement\('div', \{className: 'chart-wrapper'\},[\s\S]*?React\.createElement\('div', \{style:\{textAlign:'center',color:'var\(--text3\)'\}\}, 'Немає даних'\)\s*\),\s*"
js = re.sub(render_pattern, "", js)

# 3. Remove marginTop from weight tracker
js = js.replace("React.createElement('div', {className: 'chart-wrapper', style:{marginTop:'24px'}}",
                "React.createElement('div', {className: 'chart-wrapper'}")

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Tonnage chart removed.")
