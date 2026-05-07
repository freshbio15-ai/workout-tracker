import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Remove arrows from title
# Find the block we added in fix_syntax.py and revert to simpler title
pattern_title = r"React\.createElement\('div', \{style:\{display:'flex', alignItems:'center', gap:'8px'\}\},\s*`Динаміка власної ваги \(\$\{bwUnit\}\)`,\s*allWeightKeys\.length > 10 && React\.createElement\('div', \{style:\{display:'flex', gap:'4px'\}\},\s*React\.createElement\('button', \{onClick:\(\)=>setWeightPage\(p=>Math\.min\(p\+1, totalWPages-1\)\), disabled: weightPage >= totalWPages-1, style:\{background:'var\(--bg4\)', border:'1px solid var\(--border\)', color: weightPage >= totalWPages-1 \? 'var\(--text3\)' : 'var\(--text1\)', padding:'2px 6px', borderRadius:'4px', cursor:'pointer'\}, React\.createElement\(ArrowLeftIcon, \{size:12\}\)\),\s*React\.createElement\('button', \{onClick:\(\)=>setWeightPage\(p=>Math\.max\(0, p-1\)\), disabled: weightPage === 0, style:\{background:'var\(--bg4\)', border:'1px solid var\(--border\)', color: weightPage === 0 \? 'var\(--text3\)' : 'var\(--text1\)', padding:'2px 6px', borderRadius:'4px', cursor:'pointer'\}, React\.createElement\(ArrowRightIcon, \{size:12\}\)\)\s*\)\s*\),"

reverted_title = f"`Динаміка власної ваги (${{bwUnit}})`,"

js = re.sub(pattern_title, reverted_title, js)

# 2. Add arrows below the chart
# Find the end of weightChartData.map
# It's inside weightChartData.length > 0 ? ... : ...

# Let's find the specific block
search_map_end = r"                React\.createElement\('div', \{className: 'chart-label'\}, fmtShort\(d\.date\)\)\s*\);\s*\}\)\s*\)\s*: React\.createElement"

# We want to insert after weightChartData.map(...) but before the ":" (else branch)
# Actually, it's better to put it inside a fragment or just wrap the chart-container in a div.

# Let's try this:
# Replace weightChartData.length > 0 ? React.createElement('div', {className: 'chart-container', ...}, map...)
# with weightChartData.length > 0 ? React.createElement(React.Fragment, null, React.createElement('div', ...), Pagination)

old_chart_block = r"weightChartData\.length > 0 \? React\.createElement\('div', \{className: 'chart-container', style:\{height:'140px'\}\},"

new_chart_block = r"weightChartData.length > 0 ? React.createElement(React.Fragment, null, React.createElement('div', {className: 'chart-container', style:{height:'140px', marginBottom:'12px'}},"

js = re.sub(old_chart_block, new_chart_block, js)

# Now find the end of the map and append the pagination
map_end_pattern = r"fmtShort\(d\.date\)\)\s*\);\s*\}\)\s*\)"
map_end_replacement = r"""fmtShort(d.date))
              );
            }),
            allWeightKeys.length > 10 && React.createElement('div', {style:{display:'flex', justifyContent:'center', gap:'16px', marginTop:'8px'}},
              React.createElement('button', {onClick:()=>setWeightPage(p=>Math.min(p+1, totalWPages-1)), disabled: weightPage >= totalWPages-1, style:{background:'var(--bg3)', border:'1px solid var(--border)', color: weightPage >= totalWPages-1 ? 'var(--text3)' : 'var(--text1)', padding:'6px 20px', borderRadius:'20px', cursor:'pointer', display:'flex', alignItems:'center', gap:'6px', fontSize:'12px', fontWeight:'600'}}, React.createElement(ArrowLeftIcon, {size:14}), 'Назад'),
              React.createElement('button', {onClick:()=>setWeightPage(p=>Math.max(0, p-1)), disabled: weightPage === 0, style:{background:'var(--bg3)', border:'1px solid var(--border)', color: weightPage === 0 ? 'var(--text3)' : 'var(--text1)', padding:'6px 20px', borderRadius:'20px', cursor:'pointer', display:'flex', alignItems:'center', gap:'6px', fontSize:'12px', fontWeight:'600'}}, 'Вперед', React.createElement(ArrowRightIcon, {size:14}))
            )
          )"""

js = re.sub(map_end_pattern, map_end_replacement, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Arrows moved successfully.")
