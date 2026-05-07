import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Update startTimer logic
old_startTimer = r"""  function startTimer\(sec\) \{
    setTimerEnd\(Date\.now\(\) \+ sec \* 1000\);
    setTimeLeft\(sec\);
    setShowTimerPopup\(false\);
  \}"""
new_startTimer = r"""  function startTimer(sec) {
    if (showTimerPopup && showTimerPopup.ei !== undefined) {
      setField(showTimerPopup.ei, showTimerPopup.si, 'rest', sec);
    }
    setTimerEnd(Date.now() + sec * 1000);
    setTimeLeft(sec);
    setShowTimerPopup(false);
  }"""
js = re.sub(old_startTimer, new_startTimer, js)

# 2. Update timer button in draft editor
old_timer_btn = r"si>0\?React\.createElement\('button',\{className:'timer-btn-inline',onClick:\(\)=>setShowTimerPopup\(true\)\},React\.createElement\(TimerIcon,\{size:14\}\)\):null,"
new_timer_btn = r"si>0?React.createElement('button',{className:'timer-btn-inline',onClick:()=>setShowTimerPopup({ei,si})},React.createElement(TimerIcon,{size:14})):null,"
js = re.sub(old_timer_btn, new_timer_btn, js)

# 3. Update saveDay to include 'rest'
old_saveDay_map = r"sets:e\.sets\.filter\(s=>s\.reps!==''\|\|s\.weight!==''\|\|s\.bw\)\.map\(s=>\(\{reps:Number\(s\.reps\)\|\|0,weight:s\.bw\?Number\(settings\.userWeight\)\|\|0:Number\(s\.weight\)\|\|0,bw:!!s\.bw\}\)\)"
new_saveDay_map = r"sets:e.sets.filter(s=>s.reps!==''||s.weight!==''||s.bw).map(s=>({reps:Number(s.reps)||0,weight:s.bw?Number(settings.userWeight)||0:Number(s.weight)||0,bw:!!s.bw,rest:Number(s.rest)||0}))"
js = re.sub(old_saveDay_map, new_saveDay_map, js)

# 4. Fix table layout in renderHistoryDetail
# The old tbody row mapping:
old_tbody_tr = r"""              ex\.sets\.map\(\(s,j\)=>React\.createElement\('tr',\{key:j\},
                React\.createElement\('td',null,React\.createElement\('span',\{className:'set-badge'\},j\+1\)\),
                React\.createElement\('td',null,s\.bw\?'СВ \('\+s\.weight\+'кг\)':s\.weight\+' кг'\),
                React\.createElement\('td',null,s\.reps\),
                React\.createElement\('td', \{style:\{color:'var\(--text2\)'\}\}, s\.rest \? fmtTimer\(s\.rest\) : '-'\),
                React\.createElement\('td',\{className:'detail-vol'\},Math\.round\(\(Number\(s\.reps\)\|\|0\)\*\(Number\(s\.weight\)\|\|0\)\)\+' кг'\)
              \)\)"""

# Wait, my previous regex replace failed, so the current js STILL HAS the 4-column layout!
# Let's find exactly what is there:
#                React.createElement('td',null,s.bw?'СВ ('+s.weight+'кг)':s.weight+' кг'),
#                React.createElement('td',null,s.reps),
#                React.createElement('td',{className:'detail-vol'},(Number(s.reps)||0)*(Number(s.weight)||0)+' кг')

current_tbody_tr = r"""              ex\.sets\.map\(\(s,j\)=>React\.createElement\('tr',\{key:j\},
                React\.createElement\('td',null,React\.createElement\('span',\{className:'set-badge'\},j\+1\)\),
                React\.createElement\('td',null,s\.bw\?'СВ \('\+s\.weight\+'кг\)':s\.weight\+' кг'\),
                React\.createElement\('td',null,s\.reps\),
                React\.createElement\('td',\{className:'detail-vol'\},Math\.round\(\(Number\(s\.reps\)\|\|0\)\*\(Number\(s\.weight\)\|\|0\)\)\+' кг'\)
              \)\)"""
# Wait, `Math.round` might not be there. Let's use a very broad replacement.
# Let's locate the tbody start
start_tbody = r"React\.createElement\('tbody',null,"
end_tbody = r"\)\n            \)\n          \),"

new_tbody = r"""React.createElement('tbody',null,
              ex.sets.map((s,j)=>React.createElement('tr',{key:j},
                React.createElement('td',null,React.createElement('span',{className:'set-badge'},j+1)),
                React.createElement('td',null,s.bw?'СВ ('+s.weight+'кг)':s.weight+' кг'),
                React.createElement('td',null,s.reps),
                React.createElement('td',{style:{color:'var(--text2)'}},s.rest?fmtTimer(s.rest):'-'),
                React.createElement('td',{className:'detail-vol'},Math.round((Number(s.reps)||0)*(Number(s.weight)||0))+' кг')
              ))
            )
          ),"""

js = re.sub(r"React\.createElement\('tbody',null,[\s\S]*?\)\n            \)\n          \),", new_tbody, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Rest timer and layout fixed.")
