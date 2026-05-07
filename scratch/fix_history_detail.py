import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Add openInsights state
state_pattern = r"const \[historyDetail,setHistoryDetail\]=useState\(null\); // key of workout to show detail\n"
new_state = r"""const [historyDetail,setHistoryDetail]=useState(null); // key of workout to show detail
  const [openInsights, setOpenInsights] = useState({});
"""
js = js.replace("const [historyDetail,setHistoryDetail]=useState(null); // key of workout to show detail\n", new_state)

# 2. Add Lightbulb icon SVG component near the top (if it doesn't exist)
# I'll add it near HistoryIcon definition.
bulb_svg = r"""const LightbulbIcon=({size=24,className=''})=>React.createElement('svg',{xmlns:'http://www.w3.org/2000/svg',width:size,height:size,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor',strokeWidth:'2',strokeLinecap:'round',strokeLinejoin:'round',className:className},React.createElement('path',{d:'M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.9 1.2 1.5 1.5 2.5'}),React.createElement('path',{d:'M9 18h6'}),React.createElement('path',{d:'M10 22h4'}));
const BookIcon"""
js = js.replace("const BookIcon", bulb_svg)

# 3. Modify renderHistoryDetail insight rendering
old_insight_render = r"""            React.createElement('tbody',null,
              ex.sets.map\(\(s,j\)=>React.createElement\('tr',\{key:j\},
                React.createElement\('td',null,React.createElement\('span',\{className:'set-badge'\},j\+1\)\),
                React.createElement\('td',null,s\.bw\?'СВ \('\+s\.weight\+'кг\)':s\.weight\+' кг'\),
                React.createElement\('td',null,s\.reps\),
                React.createElement\('td',\{className:'detail-vol'\},Math.round\(\(Number\(s\.reps\)\|\|0\)\*\(Number\(s\.weight\)\|\|0\)\)\+' кг'\)
              \)\)
            \)
          \),
          insight&&React.createElement\('div',\{className:'insight-box',style:\{borderColor:insight\.border,background:insight\.bg\}\},
            React.createElement\('div',\{className:'insight-icon',style:\{color:insight\.color\}\},'💡'\),
            React.createElement\('div',\{className:'insight-content'\},
              React.createElement\('h4',\{className:'insight-title',style:\{color:insight\.color\}\},'Аналіз витривалості'\),
              React.createElement\('p',\{className:'insight-text'\},'Повторення впали на ',React.createElement\('strong',\{style:\{color:insight\.color\}\},insight\.pct\+'%'\),' \(з ',insight\.max,' до ',insight\.min,'\).',React.createElement\('br',null\),insight\.msg\),
              React.createElement\('p',\{className:'insight-text',style:\{marginTop:'8px',paddingTop:'8px',borderTop:'1px solid '\+insight\.border\}\},'⏱️',React.createElement\('strong',null,'Порада: '),insight\.advice\)
            \)
          \)
        \);"""

# The above regex might fail due to strict formatting variations, so I'll just use string replacement on a larger block.
# Actually, let's just find the `insight&&React.createElement` block.

js = re.sub(r"insight&&React\.createElement\('div',\{className:'insight-box'[\s\S]*?\)\n        \);", 
r"""insight&&React.createElement('div', {style:{marginTop:'12px', display:'flex', flexDirection:'column', gap:'8px'}},
            React.createElement('button', {
              onClick: () => setOpenInsights(prev => ({...prev, [i]: !prev[i]})),
              style: {
                background: openInsights[i] ? insight.bg : 'transparent',
                border: '1px solid ' + (openInsights[i] ? insight.border : 'var(--border)'),
                color: openInsights[i] ? insight.color : 'var(--text2)',
                padding: '8px 12px', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '8px',
                cursor: 'pointer', fontSize: '13px', fontWeight: '600', transition: 'all 0.2s', alignSelf: 'flex-start'
              }
            }, React.createElement(LightbulbIcon, {size:16}), openInsights[i] ? 'Приховати аналіз' : 'Аналіз витривалості'),
            
            openInsights[i] && React.createElement('div',{className:'insight-box',style:{borderColor:insight.border,background:insight.bg, marginTop:0}},
              React.createElement('div',{className:'insight-content'},
                React.createElement('p',{className:'insight-text'},'Повторення впали на ',React.createElement('strong',{style:{color:insight.color}},insight.pct+'%'),' (з ',insight.max,' до ',insight.min,').',React.createElement('br',null),insight.msg),
                React.createElement('p',{className:'insight-text',style:{marginTop:'8px',paddingTop:'8px',borderTop:'1px solid '+insight.border}},'⏱️',React.createElement('strong',null,'Порада: '),insight.advice)
              )
            )
          )
        );""", js)


# Also, let's fix the detail table alignment in styles.css
css_updates = """
.detail-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 4px;
}
.detail-table th {
  font-size: 10px;
  font-weight: 700;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 8px 6px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}
.detail-table th:last-child {
  text-align: right;
}
.detail-table td {
  padding: 10px 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text1);
  border-bottom: 1px solid rgba(255,255,255,0.03);
}
.detail-table tr:last-child td {
  border-bottom: none;
}
.detail-table td:first-child {
  width: 40px;
}
.detail-table td:last-child {
  text-align: right;
}
"""

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

# Replace old detail-table styles
css = re.sub(r"\.detail-table\{width:100%;border-collapse:collapse\}[\s\S]*?\.detail-vol\{color:var\(--green2\);font-weight:600\}", css_updates, css)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)
    
with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)

print("Detail view updated.")
