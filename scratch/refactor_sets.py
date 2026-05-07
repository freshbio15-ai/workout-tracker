import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    text = f.read()

changes = 0

# ═══ CHANGE 1: mkSet — remove rest field ═══
old = "const mkSet=()=>({reps:'',weight:'',rest:'',bw:false});"
new = "const mkSet=()=>({reps:'',weight:'',bw:false});"
text = text.replace(old, new); changes += 1

# ═══ CHANGE 2: prevReps mapping — remove rest ═══
old = "sets: ex.sets.map(s=>({reps:'', weight:'', rest:'', bw:s.bw, prevReps:s.reps, prevWeight:s.weight}))"
new = "sets: ex.sets.map(s=>({reps:'', weight:'', bw:s.bw, prevReps:s.reps, prevWeight:s.weight}))"
text = text.replace(old, new); changes += 1

# ═══ CHANGE 3: toggleBW — change from per-set to per-exercise ═══
old = """  function toggleBW(ei,si){
    const uw=settings.userWeight;
    if(!uw){flash('Вкажи свою вагу в налаштуваннях');setTab('settings');return}
    setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>i!==ei?e:{...e,sets:e.sets.map((s,j)=>{
      if(j!==si)return s;
      const nb=!s.bw;
      return{...s,bw:nb,weight:nb?uw:''};
    })})}));
  }"""
new = """  function toggleBW(ei){
    const uw=settings.userWeight;
    if(!uw){flash('Вкажи свою вагу в налаштуваннях');setTab('settings');return}
    setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>{
      if(i!==ei) return e;
      const newBw = !e.sets[0].bw;
      return {...e, sets: e.sets.map(s=>({...s, bw: newBw, weight: newBw ? uw : ''}))};
    })}));
  }"""
text = text.replace(old, new); changes += 1

# ═══ CHANGE 4: saveDay — remove rest from saved data ═══
old = "const cl={muscle:draft.muscle,exercises:draft.exercises.filter(e=>e.name.trim()).map(e=>({name:e.name.trim(),muscle:e.muscle||'',sets:e.sets.filter(s=>s.reps!==''||s.weight!==''||s.bw).map(s=>({reps:Number(s.reps)||0,weight:s.bw?Number(settings.userWeight)||0:Number(s.weight)||0,rest:Number(s.rest)||0,bw:!!s.bw}))})).filter(e=>e.sets.length>0)};"
new = "const cl={muscle:draft.muscle,exercises:draft.exercises.filter(e=>e.name.trim()).map(e=>({name:e.name.trim(),muscle:e.muscle||'',sets:e.sets.filter(s=>s.reps!==''||s.weight!==''||s.bw).map(s=>({reps:Number(s.reps)||0,weight:s.bw?Number(settings.userWeight)||0:Number(s.weight)||0,bw:!!s.bw}))})).filter(e=>e.sets.length>0)};"
text = text.replace(old, new); changes += 1

# ═══ CHANGE 5: startTimer — remove rest write to draft ═══
old = """  function startTimer(sec) {
    setTimerEnd(Date.now() + sec * 1000);
    setTimeLeft(sec);
    setShowTimerPopup(false);
    
    setDraft(p => {
      if(!p) return p;
      const d = JSON.parse(JSON.stringify(p));
      let found = false;
      for (let i = d.exercises.length - 1; i >= 0; i--) {
        const ex = d.exercises[i];
        for (let j = ex.sets.length - 1; j >= 0; j--) {
          if (ex.sets[j].reps !== '') {
            ex.sets[j].rest = sec;
            found = true;
            break;
          }
        }
        if(found) break;
      }
      return d;
    });
  }"""
new = """  function startTimer(sec) {
    setTimerEnd(Date.now() + sec * 1000);
    setTimeLeft(sec);
    setShowTimerPopup(false);
  }"""
text = text.replace(old, new); changes += 1

# ═══ CHANGE 6: Sets header — remove Відп(с) and СВ columns ═══
old = """            React.createElement('div',{className:'sets-header'},
              React.createElement('span',null,'Сет'),React.createElement('span',null,'Вага'),React.createElement('span',null,'Повт.'),React.createElement('span',null,'Відп(с)'),React.createElement('span',null,'СВ'),React.createElement('span',null,'')
            ),"""
new = """            React.createElement('div',{className:'sets-header'},
              React.createElement('span',null,'Сет'),React.createElement('span',null,'Вага'),React.createElement('span',null,'Повт.'),React.createElement('span',null,'')
            ),"""
text = text.replace(old, new); changes += 1

# ═══ CHANGE 7: Entire set row rendering — major restructure ═══
old = """            ex.sets.map((s,si)=>{
              const isPR = !s.bw && s.weight && checkPR(ex.name, Number(s.weight), selected);
              return React.createElement('div',{key:si,className:'set-row'},
                React.createElement('div',{className:'set-badge', style: isPR ? {boxShadow: '0 0 8px #10b981', color: '#10b981'} : {}}, si+1),
                React.createElement('input',{className:'set-input',type:s.bw?'text':'number',inputMode:'decimal',placeholder:s.prevWeight||'кг',value:s.bw?s.weight+' кг':s.weight,disabled:s.bw,onChange:e=>{setField(ei,si,'weight',e.target.value);setField(ei,si,'bw',false)}}),
                React.createElement('input',{className:'set-input',type:'number',inputMode:'numeric',placeholder:s.prevReps||'12',value:s.reps,onChange:e=>setField(ei,si,'reps',e.target.value)}),
                React.createElement('input',{className:'set-input',type:'number',inputMode:'numeric',placeholder:'-',value:s.rest||'',onChange:e=>setField(ei,si,'rest',e.target.value)}),
                React.createElement('button',{className:'bw-btn'+(s.bw?' active':''),onClick:()=>toggleBW(ei,si)},'СВ'),
                ex.sets.length>1?React.createElement('button',{className:'set-del-btn',onClick:()=>rmSet(ei,si)},React.createElement(XIcon)):React.createElement('div')
              );
            }),
            React.createElement('div',{className:'add-set-row'},
              React.createElement('button',{className:'add-set-btn',onClick:()=>addSet(ei)},React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'}}, React.createElement(PlusIcon), 'Підхід')),
              React.createElement('button',{className:'timer-btn',onClick:()=>setShowTimerPopup(true)},React.createElement(TimerIcon))
            )"""
new = """            // "Минулого разу" hint
            (()=>{const ps=ex.sets.find(s=>s.prevWeight||s.prevReps);return ps?React.createElement('div',{style:{fontSize:'11px',color:'var(--text3)',fontStyle:'italic',marginBottom:'6px',paddingLeft:'2px'}},`Минулого разу: ${ps.prevWeight||'?'} кг × ${ps.prevReps||'?'}`):null})(),
            // BW toggle at exercise level
            React.createElement('button',{className:'bw-toggle-btn'+(ex.sets[0].bw?' active':''),onClick:()=>toggleBW(ei),style:{marginBottom:'8px',width:'100%',padding:'8px 12px',borderRadius:'10px',border:'1px solid '+(ex.sets[0].bw?'rgba(16,185,129,.3)':'var(--border)'),background:ex.sets[0].bw?'rgba(16,185,129,.12)':'var(--bg3)',color:ex.sets[0].bw?'var(--green2)':'var(--text3)',fontSize:'12px',fontWeight:'700',cursor:'pointer',display:'flex',alignItems:'center',justifyContent:'center',gap:'6px',transition:'all .15s',fontFamily:'inherit'}},
              React.createElement('span',null,'🏃'),ex.sets[0].bw?'Своя вага (увімкнено)':'Вправа зі своєю вагою'),
            ex.sets.map((s,si)=>{
              const isPR = !s.bw && s.weight && checkPR(ex.name, Number(s.weight), selected);
              return React.createElement('div',{key:si,className: si===0?'set-row set-row-first':'set-row'},
                React.createElement('div',{className:'set-badge', style: isPR ? {boxShadow: '0 0 8px #10b981', color: '#10b981'} : {}}, si+1),
                React.createElement('input',{className:'set-input',type:s.bw?'text':'number',inputMode:'decimal',placeholder:s.prevWeight||'кг',value:s.bw?s.weight+' кг':s.weight,disabled:s.bw,onChange:e=>{setField(ei,si,'weight',e.target.value);setField(ei,si,'bw',false)}}),
                React.createElement('input',{className:'set-input',type:'number',inputMode:'numeric',placeholder:s.prevReps||'12',value:s.reps,onChange:e=>setField(ei,si,'reps',e.target.value)}),
                si>0?React.createElement('button',{className:'timer-btn-inline',onClick:()=>setShowTimerPopup(true)},React.createElement(TimerIcon,{size:14})):null,
                ex.sets.length>1?React.createElement('button',{className:'set-del-btn',onClick:()=>rmSet(ei,si)},React.createElement(XIcon)):React.createElement('div')
              );
            }),
            React.createElement('div',{className:'add-set-row'},
              React.createElement('button',{className:'add-set-btn',onClick:()=>addSet(ei)},React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'}}, React.createElement(PlusIcon), 'Підхід'))
            )"""
text = text.replace(old, new); changes += 1

# ═══ CHANGE 8: History table — remove Відп. column ═══
old = """                React.createElement('th',null,'Вага'),
                React.createElement('th',null,'Повт.'),
                React.createElement('th',null,'Відп.'),
                React.createElement('th',null,'Об\\'єм')"""
new = """                React.createElement('th',null,'Вага'),
                React.createElement('th',null,'Повт.'),
                React.createElement('th',null,'Об\\'єм')"""
text = text.replace(old, new); changes += 1

# ═══ CHANGE 9: History table body — remove rest cell ═══
old = """                React.createElement('td',null,s.bw?'СВ ('+s.weight+'кг)':s.weight+' кг'),
                React.createElement('td',null,s.reps),
                React.createElement('td',null,s.rest ? s.rest + ' с' : '-'),
                React.createElement('td',{className:'detail-vol'},(Number(s.reps)||0)*(Number(s.weight)||0)+' кг')"""
new = """                React.createElement('td',null,s.bw?'СВ ('+s.weight+'кг)':s.weight+' кг'),
                React.createElement('td',null,s.reps),
                React.createElement('td',{className:'detail-vol'},(Number(s.reps)||0)*(Number(s.weight)||0)+' кг')"""
text = text.replace(old, new); changes += 1

# ═══ CHANGE 10: analyzeDrops — remove rest references ═══
old = "            const restTime = Number(sets[i].rest) || 0;"
new = "            const restTime = 0; // rest field removed from sets"
text = text.replace(old, new); changes += 1

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(text)

print(f"Applied {changes} changes successfully.")
