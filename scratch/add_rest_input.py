import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    text = f.read()

# 1. Update day editor sets rendering
old_sets_header = """            React.createElement('div',{className:'sets-header'},
              React.createElement('span',null,'Сет'),React.createElement('span',null,'Вага'),React.createElement('span',null,'Повт.'),React.createElement('span',null,'СВ'),React.createElement('span',null,'')
            ),"""
new_sets_header = """            React.createElement('div',{className:'sets-header'},
              React.createElement('span',null,'Сет'),React.createElement('span',null,'Вага'),React.createElement('span',null,'Повт.'),React.createElement('span',null,'Відп(с)'),React.createElement('span',null,'СВ'),React.createElement('span',null,'')
            ),"""

old_set_row = """            ex.sets.map((s,si)=>React.createElement('div',{key:si,className:'set-row'},
              React.createElement('div',{className:'set-badge'},si+1),
              React.createElement('input',{className:'set-input',type:s.bw?'text':'number',inputMode:'decimal',placeholder:s.prevWeight||'кг',value:s.bw?s.weight+' кг':s.weight,disabled:s.bw,onChange:e=>{setField(ei,si,'weight',e.target.value);setField(ei,si,'bw',false)}}),
              React.createElement('input',{className:'set-input',type:'number',inputMode:'numeric',placeholder:s.prevReps||'12',value:s.reps,onChange:e=>setField(ei,si,'reps',e.target.value)}),
              React.createElement('button',{className:'bw-btn'+(s.bw?' active':''),onClick:()=>toggleBW(ei,si)},'СВ'),
              ex.sets.length>1?React.createElement('button',{className:'set-del-btn',onClick:()=>rmSet(ei,si)},React.createElement(XIcon)):React.createElement('div')
            )),"""
            
new_set_row = """            ex.sets.map((s,si)=>{
              const isPR = !s.bw && s.weight && checkPR(ex.name, Number(s.weight), selected);
              return React.createElement('div',{key:si,className:'set-row'},
                React.createElement('div',{className:'set-badge', style: isPR ? {boxShadow: '0 0 8px #10b981', color: '#10b981'} : {}}, si+1),
                React.createElement('input',{className:'set-input',type:s.bw?'text':'number',inputMode:'decimal',placeholder:s.prevWeight||'кг',value:s.bw?s.weight+' кг':s.weight,disabled:s.bw,onChange:e=>{setField(ei,si,'weight',e.target.value);setField(ei,si,'bw',false)}}),
                React.createElement('input',{className:'set-input',type:'number',inputMode:'numeric',placeholder:s.prevReps||'12',value:s.reps,onChange:e=>setField(ei,si,'reps',e.target.value)}),
                React.createElement('input',{className:'set-input',type:'number',inputMode:'numeric',placeholder:'-',value:s.rest||'',onChange:e=>setField(ei,si,'rest',e.target.value)}),
                React.createElement('button',{className:'bw-btn'+(s.bw?' active':''),onClick:()=>toggleBW(ei,si)},'СВ'),
                ex.sets.length>1?React.createElement('button',{className:'set-del-btn',onClick:()=>rmSet(ei,si)},React.createElement(XIcon)):React.createElement('div')
              );
            }),"""

if new_sets_header not in text:
    text = text.replace(old_sets_header, new_sets_header)
if "s.rest||''" not in text:
    text = text.replace(old_set_row, new_set_row)

# 2. Update History table
old_th = """                React.createElement('th',null,'Вага'),
                React.createElement('th',null,'Повт.'),
                React.createElement('th',null,'Об\\'єм')"""
new_th = """                React.createElement('th',null,'Вага'),
                React.createElement('th',null,'Повт.'),
                React.createElement('th',null,'Відп.'),
                React.createElement('th',null,'Об\\'єм')"""

old_td = """                React.createElement('td',null,s.bw?'СВ ('+s.weight+'кг)':s.weight+' кг'),
                React.createElement('td',null,s.reps),
                React.createElement('td',{className:'detail-vol'},(Number(s.reps)||0)*(Number(s.weight)||0)+' кг')"""
new_td = """                React.createElement('td',null,s.bw?'СВ ('+s.weight+'кг)':s.weight+' кг'),
                React.createElement('td',null,s.reps),
                React.createElement('td',null,s.rest ? s.rest + ' с' : '-'),
                React.createElement('td',{className:'detail-vol'},(Number(s.reps)||0)*(Number(s.weight)||0)+' кг')"""

if new_th not in text:
    text = text.replace(old_th, new_th)
if "s.rest ? s.rest" not in text:
    text = text.replace(old_td, new_td)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(text)

print("Added rest input")
