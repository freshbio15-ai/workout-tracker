with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'Динаміка власної ваги (${bwUnit})' in line:
        # found the line
        indent = line[:line.find('`')]
        new_block = [
            f"{indent}React.createElement('div', {{style:{{display:'flex', alignItems:'center', gap:'8px'}},\n",
            f"{indent}  `Динаміка власної ваги (${{bwUnit}})`,\n",
            f"{indent}  allWeightKeys.length > 10 && React.createElement('div', {{style:{{display:'flex', gap:'4px'}},\n",
            f"{indent}    React.createElement('button', {{onClick:()=>setWeightPage(p=>Math.min(p+1, totalWPages-1)), disabled: weightPage >= totalWPages-1, style:{{background:'var(--bg4)', border:'1px solid var(--border)', color: weightPage >= totalWPages-1 ? 'var(--text3)' : 'var(--text1)', padding:'2px 6px', borderRadius:'4px', cursor:'pointer'}}, React.createElement(ArrowLeftIcon, {{size:12}})),\n",
            f"{indent}    React.createElement('button', {{onClick:()=>setWeightPage(p=>Math.max(0, p-1)), disabled: weightPage === 0, style:{{background:'var(--bg4)', border:'1px solid var(--border)', color: weightPage === 0 ? 'var(--text3)' : 'var(--text1)', padding:'2px 6px', borderRadius:'4px', cursor:'pointer'}}, React.createElement(ArrowRightIcon, {{size:12}}))\n",
            f"{indent}  )\n",
            f"{indent}),\n"
        ]
        lines[i] = "".join(new_block)
        break

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.writelines(lines)

print("UI Pagination fixed.")
