import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Fix insight box (remove TimerIcon)
js = js.replace("React.createElement(TimerIcon, {size:12, style:{marginRight:'4px'}}), React.createElement('strong',null,'Порада: '), insight.advice", "React.createElement('strong',null,'Порада: '), insight.advice")

# 2. Add 'Відп.' column to the detail table
# Original header:
old_thead = r"""React\.createElement\('tr',null,
                React\.createElement\('th',null,'Сет'\),
                React\.createElement\('th',null,'Вага'\),
                React\.createElement\('th',null,'Повт\.'\),
                React\.createElement\('th',null,'Об\\'єм'\)
              \)"""

new_thead = r"""React.createElement('tr',null,
                React.createElement('th',null,'Сет'),
                React.createElement('th',null,'Вага'),
                React.createElement('th',null,'Повт.'),
                React.createElement('th',null,'Відп.'),
                React.createElement('th',null,'Об\'єм')
              )"""
js = re.sub(old_thead, new_thead, js)

# Original tbody row:
old_tbody_row = r"""React\.createElement\('td',null,s\.bw\?'СВ \('\+s\.weight\+'кг\)':s\.weight\+' кг'\),
                React\.createElement\('td',null,s\.reps\),
                React\.createElement\('td',\{className:'detail-vol'\},Math.round\(\(Number\(s\.reps\)\|\|0\)\*\(Number\(s\.weight\)\|\|0\)\)\+' кг'\)
              \)\)"""

new_tbody_row = r"""React.createElement('td',null,s.bw?'СВ ('+s.weight+'кг)':s.weight+' кг'),
                React.createElement('td',null,s.reps),
                React.createElement('td', {style:{color:'var(--text2)'}}, s.rest ? fmtTimer(s.rest) : '-'),
                React.createElement('td',{className:'detail-vol'},Math.round((Number(s.reps)||0)*(Number(s.weight)||0))+' кг')
              ))"""
js = re.sub(old_tbody_row, new_tbody_row, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Table fixed.")
