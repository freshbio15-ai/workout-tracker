const { useState, useEffect, useRef, useCallback } = React;

// muscles are image-based, assigned per exercise
const MUSCLE_EMOJIS = [
  {id:'chest',icon:'assets/icon_chest.png',label:'Груди'},
  {id:'back',icon:'assets/icon_back.png',label:'Спина'},
  {id:'legs',icon:'assets/icon_legs.png',label:'Ноги'},
  {id:'shoulders',icon:'assets/icon_shoulders.png',label:'Плечі'},
  {id:'biceps',icon:'assets/icon_biceps.png',label:'Біцепс'},
  {id:'triceps',icon:'assets/icon_triceps.png',label:'Трицепс'},
  {id:'abs',icon:'assets/icon_abs.png',label:'Прес'},
  {id:'cardio',icon:'assets/icon_cardio.png',label:'Кардіо'},
];
const STORAGE = 'gymbook-data';
const SETTINGS_KEY = 'gymbook-settings';
const WEEKDAYS = ['Нд','Пн','Вт','Ср','Чт','Пт','Сб'];
const MONTHS = ['Січень','Лютий','Березень','Квітень','Травень','Червень','Липень','Серпень','Вересень','Жовтень','Листопад','Грудень'];

// ── Firebase init ────────────────────────────────────────────────────
const firebaseConfig = {
  apiKey: "AIzaSyDZE65pb7oiBc6oa8NbTlHPf1QB55I9RXA",
  authDomain: "gym-notebook-74450.firebaseapp.com",
  projectId: "gym-notebook-74450",
  storageBucket: "gym-notebook-74450.firebasestorage.app",
  messagingSenderId: "980458996682",
  appId: "1:980458996682:web:4d80b560fd8a9f65c78533"
};
const fbApp = firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();

// ── localStorage (offline cache) ─────────────────────────────────────
function load(k,def){try{return JSON.parse(localStorage.getItem(k))||def}catch{return def}}
function persist(k,v){localStorage.setItem(k,JSON.stringify(v))}

// ── Firestore helpers ────────────────────────────────────────────────
function userDoc(uid, collection) {
  return db.collection('users').doc(uid).collection(collection);
}

async function saveToCloud(uid, data, settings) {
  try {
    const batch = db.batch();
    // save settings
    batch.set(db.collection('users').doc(uid), { settings, updatedAt: firebase.firestore.FieldValue.serverTimestamp() }, { merge: true });
    // save each workout day
    const existingSnap = await userDoc(uid, 'workouts').get();
    const existingKeys = new Set();
    existingSnap.forEach(doc => existingKeys.add(doc.id));
    // delete removed days
    existingKeys.forEach(key => {
      if (!data[key]) batch.delete(userDoc(uid, 'workouts').doc(key));
    });
    // set current days
    Object.entries(data).forEach(([key, val]) => {
      batch.set(userDoc(uid, 'workouts').doc(key), val);
    });
    await batch.commit();
  } catch (e) {
    console.error('Cloud save error:', e);
  }
}

async function loadFromCloud(uid) {
  try {
    const [userSnap, workoutsSnap] = await Promise.all([
      db.collection('users').doc(uid).get(),
      userDoc(uid, 'workouts').get()
    ]);
    const settings = userSnap.exists && userSnap.data().settings ? userSnap.data().settings : null;
    const data = {};
    workoutsSnap.forEach(doc => { data[doc.id] = doc.data(); });
    return { data, settings };
  } catch (e) {
    console.error('Cloud load error:', e);
    return null;
  }
}
function toKey(d){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}
function todayKey(){return toKey(new Date())}
function fmtFull(k){const[y,m,d]=k.split('-').map(Number);return new Date(y,m-1,d).toLocaleDateString('uk-UA',{weekday:'long',day:'numeric',month:'long'})}
function fmtShort(k){const[y,m,d]=k.split('-').map(Number);return new Date(y,m-1,d).toLocaleDateString('uk-UA',{day:'numeric',month:'short'})}
const mkSet=()=>({reps:'',weight:'',bw:false});
const mkEx=()=>({name:'',muscle:'',sets:[mkSet()]});
const mkDay=()=>({muscle:'',exercises:[mkEx()]});

function buildGrid(y,m){const f=new Date(y,m,1);const dow=f.getDay();const days=new Date(y,m+1,0).getDate();const c=[];for(let i=0;i<dow;i++)c.push(null);for(let d=1;d<=days;d++)c.push(d);return c}

function calcTonnage(workout){
  return workout.exercises.reduce((a,ex)=>a+ex.sets.reduce((b,s)=>{
    const w=s.bw?Number(s.weight)||0:Number(s.weight)||0;
    return b+(Number(s.reps)||0)*w;
  },0),0);
}

// ══════════════════════════════════════════════════════════════════
function App(){
  const [data,setData]=useState(()=>load(STORAGE,{}));
  const [settings,setSettings]=useState(()=>load(SETTINGS_KEY,{userWeight:'',muscles:[]}));
  const [newMuscle,setNewMuscle]=useState('');
  const [tab,setTab]=useState('calendar');
  const [calDate,setCalDate]=useState(new Date());
  const [selected,setSelected]=useState(todayKey());
  const [draft,setDraft]=useState(null);
  const [toast,setToast]=useState(null);
  const [showStats,setShowStats]=useState(false);
  const [historyDetail,setHistoryDetail]=useState(null); // key of workout to show detail
  const [filterStart,setFilterStart]=useState('');
  const [filterEnd,setFilterEnd]=useState('');
  const [showPicker,setShowPicker]=useState(false);
  const [pickerYear,setPickerYear]=useState(new Date().getFullYear());
  const [pickerMonth,setPickerMonth]=useState(new Date().getMonth());
  const [pickerStart,setPickerStart]=useState('');
  const [pickerEnd,setPickerEnd]=useState('');
  const [uid,setUid]=useState(null);
  const [cloudStatus,setCloudStatus]=useState('connecting'); // connecting | synced | saving | offline
  const tRef=useRef(null);
  const saveTimer=useRef(null);
  const isFirstLoad=useRef(true);

  // ── Firebase anonymous auth ──────────────────────────────────────
  useEffect(()=>{
    const unsub = auth.onAuthStateChanged(async (user)=>{
      if(user){
        setUid(user.uid);
        // load from cloud on first auth
        setCloudStatus('connecting');
        const cloud = await loadFromCloud(user.uid);
        if(cloud){
          const localKeys = Object.keys(load(STORAGE,{}));
          const cloudKeys = Object.keys(cloud.data);
          // merge: cloud wins if it has more data, otherwise keep local
          if(cloudKeys.length >= localKeys.length){
            setData(cloud.data);
            persist(STORAGE, cloud.data);
          }
          if(cloud.settings){
            setSettings(cloud.settings);
            persist(SETTINGS_KEY, cloud.settings);
          }
        }
        setCloudStatus('synced');
        isFirstLoad.current = false;
      } else {
        // sign in anonymously
        try { await auth.signInAnonymously(); }
        catch(e){ console.error('Auth error:',e); setCloudStatus('offline'); }
      }
    });
    return ()=>unsub();
  },[]);

  // ── Save to localStorage + debounced cloud save ──────────────────
  useEffect(()=>{persist(STORAGE,data)},[data]);
  useEffect(()=>{persist(SETTINGS_KEY,settings)},[settings]);

  useEffect(()=>{
    if(!uid || isFirstLoad.current) return;
    setCloudStatus('saving');
    clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(async ()=>{
      await saveToCloud(uid, data, settings);
      setCloudStatus('synced');
    }, 1500); // debounce 1.5s to avoid too many writes
  },[data, settings]);

  useEffect(()=>{
    if(!selected){setDraft(null);return}
    const ex=data[selected];
    if(ex) setDraft(JSON.parse(JSON.stringify(ex)));
    else setDraft(mkDay());
  },[selected]);

  function flash(m){clearTimeout(tRef.current);setToast(m);tRef.current=setTimeout(()=>setToast(null),1800)}

  // calendar
  const year=calDate.getFullYear(), month=calDate.getMonth();
  const grid=buildGrid(year,month);
  const tKey=todayKey();
  function selectDay(d){if(!d)return;setSelected(toKey(new Date(year,month,d)))}

  // draft ops
  function setMuscle(m){
    setDraft(p=>{
      const isEmpty = p.exercises.length === 1 && p.exercises[0].name.trim() === '' && p.exercises[0].sets.every(s=>!s.reps&&!s.weight&&!s.bw);
      if(isEmpty){
        const lastW = Object.entries(data).sort((a,b)=>b[0].localeCompare(a[0])).find(([k,w])=>k!==selected && w.muscle===m);
        if(lastW){
          const newExs = lastW[1].exercises.map(ex=>({
            name: ex.name, muscle: ex.muscle||'', sets: ex.sets.map(s=>({reps:'', weight:'', bw:s.bw, prevReps:s.reps, prevWeight:s.weight}))
          }));
          return {...p, muscle:m, exercises:newExs};
        }
      }
      return {...p, muscle:m};
    });
  }
  function setExName(ei,v){setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>i===ei?{...e,name:v}:e)}))}
  function setExMuscle(ei,m){setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>i===ei?{...e,muscle:e.muscle===m?'':m}:e)}))}
  function setField(ei,si,f,v){setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>i!==ei?e:{...e,sets:e.sets.map((s,j)=>j!==si?s:{...s,[f]:v})})}))}
  function addSet(ei){setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>i!==ei?e:{...e,sets:[...e.sets,mkSet()]})}))}
  function rmSet(ei,si){setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>i!==ei?e:{...e,sets:e.sets.filter((_,j)=>j!==si)})}))}
  function addEx(){setDraft(p=>({...p,exercises:[...p.exercises,mkEx()]}))}
  function rmEx(ei){setDraft(p=>({...p,exercises:p.exercises.filter((_,i)=>i!==ei)}))}

  function toggleBW(ei,si){
    const uw=settings.userWeight;
    if(!uw){flash('⚙️ Вкажи свою вагу в налаштуваннях');setTab('settings');return}
    setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>i!==ei?e:{...e,sets:e.sets.map((s,j)=>{
      if(j!==si)return s;
      const nb=!s.bw;
      return{...s,bw:nb,weight:nb?uw:''};
    })})}));
  }

  function saveDay(){
    if(!draft)return;
    const cl={muscle:draft.muscle,exercises:draft.exercises.filter(e=>e.name.trim()).map(e=>({name:e.name.trim(),muscle:e.muscle||'',sets:e.sets.filter(s=>s.reps!==''||s.weight!==''||s.bw).map(s=>({reps:Number(s.reps)||0,weight:s.bw?Number(settings.userWeight)||0:Number(s.weight)||0,bw:!!s.bw}))})).filter(e=>e.sets.length>0)};
    if(!cl.exercises.length)return;
    setData(p=>({...p,[selected]:cl}));
    flash('✅ Збережено!');
  }

  function deleteDay(){setData(p=>{const n={...p};delete n[selected];return n});setDraft(mkDay());flash('🗑 Видалено')}

  // stats
  const filteredDataEntries = Object.entries(data).filter(([k])=>{
    if(filterStart && k < filterStart) return false;
    if(filterEnd && k > filterEnd) return false;
    return true;
  });
  const filteredData = Object.fromEntries(filteredDataEntries);

  const allKeys=Object.keys(filteredData);
  const totalDays=allKeys.length;
  const totalSets=Object.values(filteredData).reduce((a,d)=>a+d.exercises.reduce((b,e)=>b+e.sets.length,0),0);
  const totalReps=Object.values(filteredData).reduce((a,d)=>a+d.exercises.reduce((b,e)=>b+e.sets.reduce((c,s)=>c+(Number(s.reps)||0),0),0),0);
  const weekStart=(()=>{const n=new Date();const s=new Date(n);s.setDate(n.getDate()-n.getDay());s.setHours(0,0,0,0);return s})();
  const thisWeek=allKeys.filter(k=>new Date(k+'T00:00:00')>=weekStart).length;
  const totalTonnage=Object.values(filteredData).reduce((a,w)=>a+calcTonnage(w),0);
  const history=filteredDataEntries.sort((a,b)=>b[0].localeCompare(a[0]));

  // muscle breakdown — from exercise-level muscles
  const muscleStats=(()=>{
    const map={};
    Object.values(filteredData).forEach(w=>{
      w.exercises.forEach(ex=>{
        const m = ex.muscle || '';
        if(!m) return;
        const mg = MUSCLE_EMOJIS.find(e=>e.id===m);
        if(!mg) return; // skip old text-based data
        const key = mg.id;
        if(!map[key]) map[key]={icon:mg.icon,label:mg.label,days:0,sets:0,reps:0,tonnage:0};
        map[key].sets += ex.sets.length;
        ex.sets.forEach(s=>{
          map[key].reps += Number(s.reps)||0;
          map[key].tonnage += (Number(s.reps)||0)*(Number(s.weight)||0);
        });
      });
    });
    // count unique days per muscle
    Object.values(filteredData).forEach(w=>{
      const seen = new Set();
      w.exercises.forEach(ex=>{
        const m = ex.muscle || '';
        if(!m) return;
        const mg = MUSCLE_EMOJIS.find(e=>e.id===m);
        if(!mg) return;
        if(!seen.has(mg.id)){ seen.add(mg.id); if(map[mg.id]) map[mg.id].days++; }
      });
    });
    return Object.entries(map).sort((a,b)=>b[1].sets-a[1].sets);
  })();
  const maxMuscleSets=muscleStats.length?muscleStats[0][1].sets:1;

  // streak
  const streak=(()=>{
    let count=0;const today=new Date();today.setHours(0,0,0,0);
    for(let i=0;i<365;i++){
      const d=new Date(today);d.setDate(today.getDate()-i);
      if(data[toKey(d)])count++;else if(i>0)break;
    }
    return count;
  })();

  // avg sets per workout
  const avgSets=totalDays?Math.round(totalSets/totalDays):0;
  // fav muscle
  const favMuscle=muscleStats.length?React.createElement('div',{style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'}},React.createElement('img',{src:muscleStats[0][1].icon,className:'inline-muscle-icon'}),muscleStats[0][1].label):'—';

  // ─── CALENDAR TAB ───────────────────────────────────────────────
  function renderCalendar(){
    const hasData=data[selected];
    return React.createElement(React.Fragment,null,
      // stats (clickable)
      React.createElement('div',{className:'stats-bar',onClick:()=>setShowStats(true)},
        React.createElement('div',{className:'stat-pill'},React.createElement('div',{className:'stat-num'},totalDays),React.createElement('div',{className:'stat-lbl'},'Днів')),
        React.createElement('div',{className:'stat-pill'},React.createElement('div',{className:'stat-num'},totalSets),React.createElement('div',{className:'stat-lbl'},'Підходів')),
        React.createElement('div',{className:'stat-pill'},React.createElement('div',{className:'stat-num'},thisWeek),React.createElement('div',{className:'stat-lbl'},'Тиждень'))
      ),
      React.createElement('div',{className:'stats-hint'},'натисни для детальної статистики ↑'),
      // calendar
      React.createElement('div',{className:'calendar-wrap'},
        React.createElement('div',{className:'cal-nav'},
          React.createElement('button',{className:'cal-arrow',onClick:()=>setCalDate(d=>new Date(d.getFullYear(),d.getMonth()-1,1))},'‹'),
          React.createElement('span',{className:'cal-month'},`${MONTHS[month]} ${year}`),
          React.createElement('button',{className:'cal-arrow',onClick:()=>setCalDate(d=>new Date(d.getFullYear(),d.getMonth()+1,1))},'›')
        ),
        React.createElement('div',{className:'cal-weekdays'},WEEKDAYS.map(w=>React.createElement('div',{key:w,className:'cal-wd'},w))),
        React.createElement('div',{className:'cal-grid'},grid.map((d,idx)=>{
          if(!d)return React.createElement('div',{key:'e'+idx,className:'cal-day empty'});
          const k=toKey(new Date(year,month,d));
          let cls='cal-day';
          if(k===tKey)cls+=' today';
          if(data[k])cls+=' has-workout';
          if(k===selected)cls+=' selected';
          return React.createElement('div',{key:d,className:cls,onClick:()=>selectDay(d)},d,data[k]&&React.createElement('div',{className:'day-dot'}));
        }))
      ),
      // day editor
      selected&&draft&&React.createElement('div',{className:'day-panel'},
        React.createElement('div',{className:'day-panel-header'},
          React.createElement('div',null,
            React.createElement('div',{className:'day-panel-title'},selected===tKey?'📅 Сьогодні':'📅 '+fmtFull(selected)),
            React.createElement('div',{className:'day-panel-date'},hasData?'✏️ Редагування':'Нове тренування')
          )
        ),
        React.createElement('div',{className:'day-panel-body'},
          React.createElement('div',{className:'muscle-row'},
            (settings.muscles||[]).map(m=>React.createElement('button',{key:m,className:'muscle-tag'+(draft.muscle===m?' active':''),onClick:()=>setMuscle(m)},
              m,
              React.createElement('span',{className:'chip-del',onClick:e=>{e.stopPropagation();setSettings(s=>({...s,muscles:s.muscles.filter(x=>x!==m)}));if(draft.muscle===m)setMuscle('')}},'×')
            )),
            React.createElement('div',{className:'add-muscle-wrap'},
              React.createElement('input',{className:'add-muscle-input',placeholder:'Нова група…',value:newMuscle,onChange:e=>setNewMuscle(e.target.value),
                onKeyDown:e=>{if(e.key==='Enter'&&newMuscle.trim()){setSettings(s=>({...s,muscles:[...(s.muscles||[]),newMuscle.trim()]}));setNewMuscle('')}}
              }),
              React.createElement('button',{className:'add-muscle-btn',onClick:()=>{if(newMuscle.trim()){setSettings(s=>({...s,muscles:[...(s.muscles||[]),newMuscle.trim()]}));setNewMuscle('')}}},'+'))
          ),
          draft.exercises.map((ex,ei)=>React.createElement('div',{key:ei,className:'exercise-block'},
            React.createElement('div',{className:'ex-name-row'},
              React.createElement('input',{className:'ex-name-input',placeholder:'Назва вправи…',value:ex.name,onChange:e=>setExName(ei,e.target.value)}),
              draft.exercises.length>1&&React.createElement('button',{className:'ex-remove-btn',onClick:()=>rmEx(ei)},'×')
            ),
            // emoji muscle selector per exercise
            React.createElement('div',{className:'emoji-muscle-row'},
              MUSCLE_EMOJIS.map(mg=>React.createElement('button',{
                key:mg.id,
                className:'emoji-muscle-btn'+(ex.muscle===mg.id?' active':''),
                onClick:()=>setExMuscle(ei,mg.id),
                title:mg.label
              },React.createElement('img',{src:mg.icon,className:'muscle-btn-icon',alt:mg.label})))
            ),
            React.createElement('div',{className:'sets-header'},
              React.createElement('span',null,'Сет'),React.createElement('span',null,'Вага'),React.createElement('span',null,'Повт.'),React.createElement('span',null,'СВ'),React.createElement('span',null,'')
            ),
            ex.sets.map((s,si)=>React.createElement('div',{key:si,className:'set-row'},
              React.createElement('div',{className:'set-badge'},si+1),
              React.createElement('input',{className:'set-input',type:s.bw?'text':'number',inputMode:'decimal',placeholder:s.prevWeight||'кг',value:s.bw?s.weight+' кг':s.weight,disabled:s.bw,onChange:e=>{setField(ei,si,'weight',e.target.value);setField(ei,si,'bw',false)}}),
              React.createElement('input',{className:'set-input',type:'number',inputMode:'numeric',placeholder:s.prevReps||'12',value:s.reps,onChange:e=>setField(ei,si,'reps',e.target.value)}),
              React.createElement('button',{className:'bw-btn'+(s.bw?' active':''),onClick:()=>toggleBW(ei,si)},'СВ'),
              ex.sets.length>1?React.createElement('button',{className:'set-del-btn',onClick:()=>rmSet(ei,si)},'×'):React.createElement('div')
            )),
            React.createElement('button',{className:'add-set-btn',onClick:()=>addSet(ei)},'+ Підхід')
          )),
          React.createElement('button',{className:'add-ex-btn',onClick:addEx},'+ Додати вправу'),
          React.createElement('button',{className:'save-btn',onClick:saveDay},hasData?'💾 Оновити':'✅ Зберегти тренування'),
          hasData&&React.createElement('button',{className:'del-day-btn',onClick:deleteDay},'🗑 Видалити')
        )
      )
    );
  }

  // ─── HISTORY TAB ────────────────────────────────────────────────
  function calcExTonnage(ex){
    return ex.sets.reduce((a,s)=>(Number(s.reps)||0)*(Number(s.weight)||0)+a,0);
  }

  function renderHistoryDetail(){
    const k=historyDetail;
    const w=data[k];
    if(!w)return null;
    const ton=calcTonnage(w);
    const exTons=w.exercises.map(ex=>({name:ex.name,ton:calcExTonnage(ex),sets:ex.sets}));
    const maxExTon=Math.max(...exTons.map(e=>e.ton),1);

    return React.createElement(React.Fragment,null,
      // back button
      React.createElement('div',{style:{display:'flex',alignItems:'center',gap:'12px',marginBottom:'16px'}},
        React.createElement('button',{className:'cal-arrow',onClick:()=>setHistoryDetail(null)},'‹'),
        React.createElement('div',null,
          React.createElement('div',{style:{fontSize:'16px',fontWeight:800}},k===tKey?'Сьогодні':fmtFull(k)),
          React.createElement('div',{style:{fontSize:'12px',color:'var(--text3)',marginTop:'2px'}},w.muscle?'🎯 '+w.muscle:k)
        )
      ),
      // total tonnage for this day
      React.createElement('div',{className:'tonnage-card'},
        React.createElement('div',{className:'tonnage-value'},ton>1000?(ton/1000).toFixed(1)+' т':ton+' кг'),
        React.createElement('div',{className:'tonnage-label'},'Тоннаж за день'),
        React.createElement('div',{className:'tonnage-row'},
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},w.exercises.length),React.createElement('div',{className:'tonnage-item-lbl'},'Вправ')),
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},w.exercises.reduce((a,e)=>a+e.sets.length,0)),React.createElement('div',{className:'tonnage-item-lbl'},'Підходів')),
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},w.exercises.reduce((a,e)=>a+e.sets.reduce((b,s)=>b+(Number(s.reps)||0),0),0)),React.createElement('div',{className:'tonnage-item-lbl'},'Повторень'))
        )
      ),
      // per-exercise tonnage chart
      React.createElement('div',{className:'section-label'},'Тоннаж по вправах'),
      React.createElement('div',{className:'muscle-breakdown',style:{marginBottom:'14px'}},
        exTons.map((ex,i)=>
          React.createElement('div',{key:i,className:'mb-row'},
            React.createElement('div',{className:'mb-label',style:{width:'90px',fontSize:'11px'}},ex.name),
            React.createElement('div',{className:'mb-bar-wrap'},
              React.createElement('div',{className:'mb-bar c'+i%8,style:{width:Math.max(Math.round(ex.ton/maxExTon*100),3)+'%'}})
            ),
            React.createElement('div',{className:'mb-val',style:{width:'50px'}},ex.ton>1000?(ex.ton/1000).toFixed(1)+'т':ex.ton+'кг')
          )
        )
      ),
      // detailed exercises
      React.createElement('div',{className:'section-label'},'Деталі вправ'),
      w.exercises.map((ex,i)=>{
        const exTon=calcExTonnage(ex);
        return React.createElement('div',{key:i,className:'detail-ex-card'},
          React.createElement('div',{className:'detail-ex-header'},
            React.createElement('div',{className:'detail-ex-name',style:{display:'flex',alignItems:'center',gap:'6px'}},(()=>{const mg=MUSCLE_EMOJIS.find(e=>e.id===(ex.muscle||''));return mg?React.createElement('img',{src:mg.icon,className:'inline-muscle-icon'}):null})(),ex.name),
            React.createElement('div',{className:'detail-ex-ton'},exTon>1000?(exTon/1000).toFixed(1)+' т':exTon+' кг')
          ),
          React.createElement('table',{className:'detail-table'},
            React.createElement('thead',null,
              React.createElement('tr',null,
                React.createElement('th',null,'Сет'),
                React.createElement('th',null,'Вага'),
                React.createElement('th',null,'Повт.'),
                React.createElement('th',null,'Об\'єм')
              )
            ),
            React.createElement('tbody',null,
              ex.sets.map((s,j)=>React.createElement('tr',{key:j},
                React.createElement('td',null,React.createElement('span',{className:'set-badge'},j+1)),
                React.createElement('td',null,s.bw?'СВ ('+s.weight+'кг)':s.weight+' кг'),
                React.createElement('td',null,s.reps),
                React.createElement('td',{className:'detail-vol'},(Number(s.reps)||0)*(Number(s.weight)||0)+' кг')
              ))
            )
          )
        );
      }),
      // edit button
      React.createElement('button',{className:'save-btn',style:{marginTop:'16px',background:'var(--bg4)',boxShadow:'none',border:'1px solid var(--border)'},onClick:()=>{
        const[y,m]=k.split('-').map(Number);setCalDate(new Date(y,m-1,1));setSelected(k);setTab('calendar');setHistoryDetail(null);
      }},'✏️ Редагувати тренування')
    );
  }

  function renderHistory(){
    if(historyDetail) return renderHistoryDetail();
    
    let filterText = 'За весь час';
    if(filterStart && filterEnd) {
      if(filterStart === filterEnd) filterText = fmtShort(filterStart);
      else filterText = fmtShort(filterStart) + ' - ' + fmtShort(filterEnd);
    } else if(filterStart) filterText = 'З ' + fmtShort(filterStart);
    else if(filterEnd) filterText = 'До ' + fmtShort(filterEnd);

    return React.createElement(React.Fragment,null,
      React.createElement('div',{className:'history-header'},
        React.createElement('h2',null,'📊 Історія'),
        React.createElement('div',{className:'history-filters'},
          React.createElement('div',{className:'h-filter-label'},filterText),
          React.createElement('button',{className:'h-filter-btn',onClick:()=>{
            setPickerStart(filterStart); setPickerEnd(filterEnd);
            setPickerYear(new Date().getFullYear()); setPickerMonth(new Date().getMonth());
            setShowPicker(true);
          }},'📅')
        )
      ),
      React.createElement('div',{className:'tonnage-card'},
        React.createElement('div',{className:'tonnage-value'},(totalTonnage/1000).toFixed(1)+' т'),
        React.createElement('div',{className:'tonnage-label'},'Загальний тоннаж'),
        React.createElement('div',{className:'tonnage-row'},
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},totalDays),React.createElement('div',{className:'tonnage-item-lbl'},'Тренувань')),
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},totalSets),React.createElement('div',{className:'tonnage-item-lbl'},'Підходів')),
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},thisWeek),React.createElement('div',{className:'tonnage-item-lbl'},'Цей тижд.'))
        )
      ),
      history.length===0
        ?React.createElement('div',{className:'empty-state'},React.createElement('div',{className:'e-icon'},'📔'),React.createElement('h3',null,'Поки пусто'),React.createElement('p',null,'Записуй тренування в календарі'))
        :React.createElement(React.Fragment,null,
          // per-muscle tonnage
          muscleStats.length>0&&React.createElement(React.Fragment,null,
            React.createElement('div',{className:'section-label'},'Тоннаж по групах м\'язів'),
            React.createElement('div',{className:'muscle-tonnage-grid'},
              muscleStats.map(([key,stat],i)=>{
                const t=stat.tonnage;
                return React.createElement('div',{key:key,className:'mt-card'},
                  React.createElement('div',{className:'mt-emoji'},React.createElement('img',{src:stat.icon,className:'mt-icon',alt:stat.label})),
                  React.createElement('div',{className:'mt-info'},
                    React.createElement('div',{className:'mt-name'},stat.label),
                    React.createElement('div',{className:'mt-tonnage'},t>1000?(t/1000).toFixed(1)+' т':t+' кг'),
                    React.createElement('div',{className:'mt-details'},stat.sets+' підх. · '+stat.reps+' повт. · '+stat.days+' дн.')
                  )
                );
              })
            )
          ),
          React.createElement('div',{className:'section-label'},'Всі тренування ('+history.length+')'),
          React.createElement('div',{className:'history-list'},history.map(([k,w])=>{
            const ton=calcTonnage(w);
            return React.createElement('div',{key:k,className:'history-card',onClick:()=>setHistoryDetail(k)},
              React.createElement('div',{className:'hc-top'},
                React.createElement('div',null,
                  React.createElement('div',{className:'hc-title'},k===tKey?'Сьогодні':fmtFull(k)),
                  React.createElement('div',{className:'hc-date'},k)
                ),
                w.muscle&&React.createElement('span',{className:'hc-muscle'},w.muscle)
              ),
              React.createElement('div',{className:'hc-stats'},
                React.createElement('span',{className:'hc-stat'},React.createElement('strong',null,w.exercises.length),' вправ'),
                React.createElement('span',{className:'hc-stat'},React.createElement('strong',null,w.exercises.reduce((a,e)=>a+e.sets.length,0)),' підх.'),
                React.createElement('span',{className:'hc-stat'},React.createElement('strong',null,ton>1000?(ton/1000).toFixed(1)+'т':ton+'кг'),' тоннаж')
              ),
              React.createElement('div',{className:'hc-exercises'},w.exercises.map((ex,i)=>{
                const et=calcExTonnage(ex);
                return React.createElement('div',{key:i,className:'hc-ex'},
                  React.createElement('strong',{style:{display:'inline-flex',alignItems:'center',gap:'4px'}},(()=>{const mg=MUSCLE_EMOJIS.find(e=>e.id===(ex.muscle||''));return mg?React.createElement('img',{src:mg.icon,className:'inline-muscle-icon'}):null})(),ex.name),
                  ` — ${ex.sets.length} підх. · ${et>1000?(et/1000).toFixed(1)+'т':et+'кг'}`+(ex.sets[0]&&ex.sets[0].bw?' (СВ)':'')
                );
              }))
            );
          }))
        )
    );
  }

  // ─── SETTINGS TAB ──────────────────────────────────────────────
  function renderSettings(){
    return React.createElement(React.Fragment,null,
      React.createElement('div',{className:'settings-section'},
        React.createElement('h2',null,'⚙️ Налаштування'),
        // weight card
        React.createElement('div',{className:'settings-card'},
          React.createElement('h3',null,'🏋️ Власна вага'),
          React.createElement('p',null,'Ця вага буде автоматично підставлена, коли ти натиснеш кнопку «СВ» біля підходу'),
          React.createElement('input',{className:'settings-input',type:'number',inputMode:'decimal',placeholder:'Наприклад 75',value:settings.userWeight,
            onChange:e=>setSettings(s=>({...s,userWeight:e.target.value}))}),
          settings.userWeight&&React.createElement('div',{className:'weight-display'},
            React.createElement('div',{style:{fontSize:'14px',color:'var(--green2)',fontWeight:700}},settings.userWeight+' кг'),
            React.createElement('span',null,'— збережено')
          )
        ),
        // info
        React.createElement('div',{className:'settings-card'},
          React.createElement('h3',null,'📱 Як зберегти на робочий стіл'),
          React.createElement('p',{style:{lineHeight:'1.6'}},
            'У Safari натисни кнопку «Поділитися» (квадрат зі стрілкою) → «На початковий екран». Апка буде працювати як повноцінний додаток з іконкою 💪'
          )
        ),
        // stats
        React.createElement('div',{className:'settings-card'},
          React.createElement('h3',null,'📊 Статистика'),
          React.createElement('p',null,`Всього тренувань: ${totalDays}`),
          React.createElement('p',null,`Всього підходів: ${totalSets}`),
          React.createElement('p',null,`Загальний тоннаж: ${(totalTonnage/1000).toFixed(1)} тонн`)
        ),
        // danger zone
        React.createElement('div',{className:'danger-zone'},
          React.createElement('h3',null,'⚠️ Зона небезпеки'),
          React.createElement('p',null,'Видалити ВСІ дані тренувань без можливості відновлення'),
          React.createElement('button',{className:'danger-btn',onClick:()=>{
            if(confirm('Точно видалити ВСЕ? Цю дію не можна скасувати!')){
              setData({});setDraft(mkDay());flash('🗑 Все видалено');
            }
          }},'Видалити всі дані')
        )
      )
    );
  }

  function renderCustomPicker(){
    if(!showPicker) return null;
    const grid = buildGrid(pickerYear, pickerMonth);
    
    function handleDayClick(d) {
      const k = toKey(new Date(pickerYear, pickerMonth, d));
      if (!pickerStart) {
        setPickerStart(k); setPickerEnd(k);
      } else if (pickerStart && pickerEnd === pickerStart) {
        if (k < pickerStart) { setPickerStart(k); setPickerEnd(pickerStart); }
        else { setPickerEnd(k); }
      } else {
        setPickerStart(k); setPickerEnd(k);
      }
    }

    return React.createElement('div',{className:'cc-overlay',onClick:()=>setShowPicker(false)},
      React.createElement('div',{className:'cc-modal',onClick:e=>e.stopPropagation()},
        React.createElement('div',{className:'cc-header'},
          React.createElement('div',{className:'cc-title'},`${MONTHS[pickerMonth]} ${pickerYear}`),
          React.createElement('div',{className:'cc-nav'},
            React.createElement('button',{className:'cc-btn',onClick:()=>setPickerMonth(m=>{if(m===0){setPickerYear(y=>y-1);return 11}return m-1})},'‹'),
            React.createElement('button',{className:'cc-btn',onClick:()=>setPickerMonth(m=>{if(m===11){setPickerYear(y=>y+1);return 0}return m+1})},'›')
          )
        ),
        React.createElement('div',{className:'cc-grid'},
          WEEKDAYS.map(w=>React.createElement('div',{key:w,className:'cc-wd'},w)),
          grid.map((d,i)=>{
            if(!d) return React.createElement('div',{key:i,className:'cc-day empty'});
            const k = toKey(new Date(pickerYear, pickerMonth, d));
            let cls = 'cc-day';
            if(data[k]) cls += ' has-data';
            if(k === pickerStart || k === pickerEnd) cls += ' selected';
            if(k === pickerStart) cls += ' range-start';
            if(k === pickerEnd) cls += ' range-end';
            if(pickerStart && pickerEnd && k > pickerStart && k < pickerEnd) cls += ' in-range';
            return React.createElement('div',{key:i,className:cls,onClick:()=>handleDayClick(d)},d);
          })
        ),
        React.createElement('div',{className:'cc-footer'},
          React.createElement('button',{className:'cc-action secondary',onClick:()=>{setFilterStart('');setFilterEnd('');setShowPicker(false)}},'Скинути'),
          React.createElement('button',{className:'cc-action primary',onClick:()=>{setFilterStart(pickerStart);setFilterEnd(pickerEnd);setShowPicker(false)}},'Застосувати')
        )
      )
    );
  }

  // ─── MAIN RENDER ───────────────────────────────────────────────
  return React.createElement('div',{id:'app-root'},
    React.createElement('div',{className:'page'},
      React.createElement('div',{className:'app-header'},
        React.createElement('div',{className:'app-logo'},
          React.createElement('div',{className:'logo-icon'},'💪'),
          React.createElement('div',{className:'logo-text'},
            React.createElement('h1',null,'Gym Notebook'),
            React.createElement('p',null,'Твій щоденник тренувань')
          )
        ),
        React.createElement('div',{className:'cloud-status'},
          React.createElement('span',{className:'cloud-dot '+(cloudStatus==='synced'?'green':cloudStatus==='saving'?'yellow':'gray')}),
          React.createElement('span',{className:'cloud-text'},
            cloudStatus==='synced'?'☁️ Синхр.':cloudStatus==='saving'?'⏳ Зберіг...':cloudStatus==='connecting'?'🔄 З\'єдн...':'📴 Офлайн'
          )
        )
      ),
      tab==='calendar'&&renderCalendar(),
      tab==='history'&&renderHistory(),
      tab==='settings'&&renderSettings()
    ),
    // bottom tabs
    React.createElement('div',{className:'tab-bar'},
      React.createElement('div',{className:'tab-bar-inner'},
        React.createElement('button',{className:'tab-btn'+(tab==='calendar'?' active':''),onClick:()=>setTab('calendar')},
          React.createElement('span',{className:'tab-icon'},'📅'),React.createElement('span',null,'Календар')
        ),
        React.createElement('button',{className:'tab-btn'+(tab==='history'?' active':''),onClick:()=>setTab('history')},
          React.createElement('span',{className:'tab-icon'},'📊'),React.createElement('span',null,'Історія')
        ),
        React.createElement('button',{className:'tab-btn'+(tab==='settings'?' active':''),onClick:()=>setTab('settings')},
          React.createElement('span',{className:'tab-icon'},'⚙️'),React.createElement('span',null,'Налаштування')
        )
      )
    ),
    toast&&React.createElement('div',{key:toast,className:'toast'},toast),

    // stats popup
    showStats&&React.createElement('div',{className:'stats-overlay',onClick:e=>{if(e.target===e.currentTarget)setShowStats(false)}},
      React.createElement('div',{className:'stats-popup'},
        React.createElement('div',{className:'stats-popup-header'},
          React.createElement('h2',null,'📈 Детальна статистика'),
          React.createElement('button',{className:'stats-close',onClick:()=>setShowStats(false)},'×')
        ),

        // streak
        React.createElement('div',{className:'streak-card'},
          React.createElement('div',{className:'streak-val'},'🔥 '+streak),
          React.createElement('div',{className:'streak-lbl'},streak===1?'день поспіль':streak<5?'дні поспіль':'днів поспіль')
        ),

        // big stats grid
        React.createElement('div',{className:'big-stats'},
          React.createElement('div',{className:'big-stat'},
            React.createElement('div',{className:'big-stat-icon'},'🏋️'),
            React.createElement('div',{className:'big-stat-val'},(totalTonnage/1000).toFixed(1)+' т'),
            React.createElement('div',{className:'big-stat-lbl'},'Тоннаж')
          ),
          React.createElement('div',{className:'big-stat'},
            React.createElement('div',{className:'big-stat-icon'},'🔄'),
            React.createElement('div',{className:'big-stat-val'},totalReps),
            React.createElement('div',{className:'big-stat-lbl'},'Повторень')
          ),
          React.createElement('div',{className:'big-stat'},
            React.createElement('div',{className:'big-stat-icon'},'📊'),
            React.createElement('div',{className:'big-stat-val'},avgSets),
            React.createElement('div',{className:'big-stat-lbl'},'Підх./трен.')
          ),
          React.createElement('div',{className:'big-stat'},
            React.createElement('div',{className:'big-stat-icon'},'⭐'),
            React.createElement('div',{className:'big-stat-val'},favMuscle),
            React.createElement('div',{className:'big-stat-lbl'},'Улюблена')
          )
        ),

        // muscle breakdown
        muscleStats.length>0&&React.createElement('div',{className:'muscle-breakdown'},
          React.createElement('div',{className:'mb-title'},'Підходи по групах м\'язів'),
          muscleStats.map(([key,stat],i)=>
            React.createElement('div',{key:key,className:'mb-row'},
              React.createElement('div',{className:'mb-label',style:{display:'flex',alignItems:'center',gap:'4px'}},React.createElement('img',{src:stat.icon,className:'inline-muscle-icon'}),stat.label),
              React.createElement('div',{className:'mb-bar-wrap'},
                React.createElement('div',{className:'mb-bar c'+i%8,style:{width:Math.round(stat.sets/maxMuscleSets*100)+'%'}})
              ),
              React.createElement('div',{className:'mb-val'},stat.sets+' підх.')
            )
          )
        )
      ),
      renderCustomPicker()
    )
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(App));
