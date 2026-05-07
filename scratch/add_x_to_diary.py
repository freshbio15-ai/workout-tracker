import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Add empty th between Вага and Повт.
old_thead = r"""React\.createElement\('th',null,'Вага'\),
                React\.createElement\('th',null,'Повт\.'\),"""
new_thead = r"""React.createElement('th',null,'Вага'),
                React.createElement('th',null,''),
                React.createElement('th',null,'Повт.'),"""
js = re.sub(old_thead, new_thead, js)

# 2. Add '✕' td between Вага and Повт.
old_tbody = r"""React\.createElement\('td',null,s\.bw\?'СВ \('\+s\.weight\+'кг\)':s\.weight\+' кг'\),
                React\.createElement\('td',null,s\.reps\),"""
new_tbody = r"""React.createElement('td',null,s.bw?'СВ ('+s.weight+'кг)':s.weight+' кг'),
                React.createElement('td',{style:{color:'var(--text3)', fontSize:'11px', textAlign:'center', fontWeight:'700', padding:'0'}},'✕'),
                React.createElement('td',null,s.reps),"""
js = re.sub(old_tbody, new_tbody, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Diary detail table updated.")
