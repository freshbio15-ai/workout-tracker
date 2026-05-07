import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Fix the specific syntax errors introduced
# Search for the broken block and replace it with a fixed one
pattern = r"React\.createElement\('div', \{style:\{display:'flex', alignItems:'center', gap:'8px'\},\s*`Динаміка власної ваги \(\$\{bwUnit\}\)`,\s*allWeightKeys\.length > 10 && React\.createElement\('div', \{style:\{display:'flex', gap:'4px'\},\s*React\.createElement\('button', \{onClick:\(\)=>setWeightPage\(p=>Math\.min\(p\+1, totalWPages-1\)\), disabled: weightPage >= totalWPages-1, style:\{background:'var\(--bg4\)', border:'1px solid var\(--border\)', color: weightPage >= totalWPages-1 \? 'var\(--text3\)' : 'var\(--text1\)', padding:'2px 6px', borderRadius:'4px', cursor:'pointer'\}, React\.createElement\(ArrowLeftIcon, \{size:12\}\)\),\s*React\.createElement\('button', \{onClick:\(\)=>setWeightPage\(p=>Math\.max\(0, p-1\)\), disabled: weightPage === 0, style:\{background:'var\(--bg4\)', border:'1px solid var\(--border\)', color: weightPage === 0 \? 'var\(--text3\)' : 'var\(--text1\)', padding:'2px 6px', borderRadius:'4px', cursor:'pointer'\}, React\.createElement\(ArrowRightIcon, \{size:12\}\)\)\s*\)\s*\),"

fixed_code = """React.createElement('div', {style:{display:'flex', alignItems:'center', gap:'8px'}},
                `Динаміка власної ваги (${bwUnit})`,
                allWeightKeys.length > 10 && React.createElement('div', {style:{display:'flex', gap:'4px'}},
                  React.createElement('button', {onClick:()=>setWeightPage(p=>Math.min(p+1, totalWPages-1)), disabled: weightPage >= totalWPages-1, style:{background:'var(--bg4)', border:'1px solid var(--border)', color: weightPage >= totalWPages-1 ? 'var(--text3)' : 'var(--text1)', padding:'2px 6px', borderRadius:'4px', cursor:'pointer'}}, React.createElement(ArrowLeftIcon, {size:12})),
                  React.createElement('button', {onClick:()=>setWeightPage(p=>Math.max(0, p-1)), disabled: weightPage === 0, style:{background:'var(--bg4)', border:'1px solid var(--border)', color: weightPage === 0 ? 'var(--text3)' : 'var(--text1)', padding:'2px 6px', borderRadius:'4px', cursor:'pointer'}}, React.createElement(ArrowRightIcon, {size:12}))
                )
              ),"""

new_js = re.sub(pattern, fixed_code, js)

if js == new_js:
    # try a less strict match
    print("Warning: Strict pattern failed. Trying line-based fix.")
    lines = js.split('\n')
    start = -1
    for i, l in enumerate(lines):
        if 'Динаміка власної ваги' in l and 'React.createElement' in lines[i-1]:
            start = i-1
            break
    if start != -1:
        # replace the lines manually
        lines[start] = "              React.createElement('div', {style:{display:'flex', alignItems:'center', gap:'8px'}},"
        lines[start+1] = f"                `Динаміка власної ваги (${{bwUnit}})`,"
        lines[start+2] = "                allWeightKeys.length > 10 && React.createElement('div', {style:{display:'flex', gap:'4px'}},"
        lines[start+3] = "                  React.createElement('button', {onClick:()=>setWeightPage(p=>Math.min(p+1, totalWPages-1)), disabled: weightPage >= totalWPages-1, style:{background:'var(--bg4)', border:'1px solid var(--border)', color: weightPage >= totalWPages-1 ? 'var(--text3)' : 'var(--text1)', padding:'2px 6px', borderRadius:'4px', cursor:'pointer'}}, React.createElement(ArrowLeftIcon, {size:12})),"
        lines[start+4] = "                  React.createElement('button', {onClick:()=>setWeightPage(p=>Math.max(0, p-1)), disabled: weightPage === 0, style:{background:'var(--bg4)', border:'1px solid var(--border)', color: weightPage === 0 ? 'var(--text3)' : 'var(--text1)', padding:'2px 6px', borderRadius:'4px', cursor:'pointer'}}, React.createElement(ArrowRightIcon, {size:12}))"
        lines[start+5] = "                )"
        lines[start+6] = "              ),"
        new_js = '\n'.join(lines)
        with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
            f.write(new_js)
        print("Fixed via lines.")
    else:
        print("Error: Could not find broken block.")
else:
    with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
        f.write(new_js)
    print("Fixed via regex.")

