const { useState, useEffect, useRef } = React;

const MUSCLES = ['Спина','Груди','Ноги','Плечі','Біцепс','Трицепс','Прес','Кардіо'];
const STORAGE = 'gymbook-data';
const SETTINGS_KEY = 'gymbook-settings';
const WEEKDAYS = ['Нд','Пн','Вт','Ср','Чт','Пт','Сб'];
const MONTHS = ['Січень','Лютий','Березень','Квітень','Травень','Червень','Липень','Серпень','Вересень','Жовтень','Листопад','Грудень'];

function load(k,def){try{return JSON.parse(localStorage.getItem(k))||def}catch{return def}}
function persist(k,v){localStorage.setItem(k,JSON.stringify(v))}
function toKey(d){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}
function todayKey(){return toKey(new Date())}
function fmtFull(k){const[y,m,d]=k.split('-').map(Number);return new Date(y,m-1,d).toLocaleDateString('uk-UA',{weekday:'long',day:'numeric',month:'long'})}
function fmtShort(k){const[y,m,d]=k.split('-').map(Number);return new Date(y,m-1,d).toLocaleDateString('uk-UA',{day:'numeric',month:'short'})}
const mkSet=()=>({reps:'',weight:'',bw:false});
const mkEx=()=>({name:'',sets:[mkSet()]});
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
  const [settings,setSettings]=useState(()=>load(SETTINGS_KEY,{userWeight:''}));
  const [tab,setTab]=useState('calendar');
  const [calDate,setCalDate]=useState(new Date());
  const [selected,setSelected]=useState(todayKey());
  const [draft,setDraft]=useState(null);
  const [toast,setToast]=useState(null);
  const tRef=useRef(null);

  useEffect(()=>{persist(STORAGE,data)},[data]);
  useEffect(()=>{persist(SETTINGS_KEY,settings)},[settings]);

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
  function setMuscle(m){setDraft(p=>({...p,muscle:m}))}
  function setExName(ei,v){setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>i===ei?{...e,name:v}:e)}))}
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
    const cl={muscle:draft.muscle,exercises:draft.exercises.filter(e=>e.name.trim()).map(e=>({name:e.name.trim(),sets:e.sets.filter(s=>s.reps!==''||s.weight!==''||s.bw).map(s=>({reps:Number(s.reps)||0,weight:s.bw?Number(settings.userWeight)||0:Number(s.weight)||0,bw:!!s.bw}))})).filter(e=>e.sets.length>0)};
    if(!cl.exercises.length)return;
    setData(p=>({...p,[selected]:cl}));
    flash('✅ Збережено!');
  }

  function deleteDay(){setData(p=>{const n={...p};delete n[selected];return n});setDraft(mkDay());flash('🗑 Видалено')}

  // stats
  const allKeys=Object.keys(data);
  const totalDays=allKeys.length;
  const totalSets=Object.values(data).reduce((a,d)=>a+d.exercises.reduce((b,e)=>b+e.sets.length,0),0);
  const weekStart=(()=>{const n=new Date();const s=new Date(n);s.setDate(n.getDate()-n.getDay());s.setHours(0,0,0,0);return s})();
  const thisWeek=allKeys.filter(k=>new Date(k+'T00:00:00')>=weekStart).length;
  const totalTonnage=Object.values(data).reduce((a,w)=>a+calcTonnage(w),0);
  const history=Object.entries(data).sort((a,b)=>b[0].localeCompare(a[0]));

  // ─── CALENDAR TAB ───────────────────────────────────────────────
  function renderCalendar(){
    const hasData=data[selected];
    return React.createElement(React.Fragment,null,
      // stats
      React.createElement('div',{className:'stats-bar'},
        React.createElement('div',{className:'stat-pill'},React.createElement('div',{className:'stat-num'},totalDays),React.createElement('div',{className:'stat-lbl'},'Днів')),
        React.createElement('div',{className:'stat-pill'},React.createElement('div',{className:'stat-num'},totalSets),React.createElement('div',{className:'stat-lbl'},'Підходів')),
        React.createElement('div',{className:'stat-pill'},React.createElement('div',{className:'stat-num'},thisWeek),React.createElement('div',{className:'stat-lbl'},'Тиждень'))
      ),
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
          React.createElement('div',{className:'muscle-row'},MUSCLES.map(m=>React.createElement('button',{key:m,className:'muscle-tag'+(draft.muscle===m?' active':''),onClick:()=>setMuscle(m)},m))),
          draft.exercises.map((ex,ei)=>React.createElement('div',{key:ei,className:'exercise-block'},
            React.createElement('div',{className:'ex-name-row'},
              React.createElement('input',{className:'ex-name-input',placeholder:'Назва вправи…',value:ex.name,onChange:e=>setExName(ei,e.target.value)}),
              draft.exercises.length>1&&React.createElement('button',{className:'ex-remove-btn',onClick:()=>rmEx(ei)},'×')
            ),
            React.createElement('div',{className:'sets-header'},
              React.createElement('span',null,'Сет'),React.createElement('span',null,'Повт.'),React.createElement('span',null,'Вага'),React.createElement('span',null,'СВ'),React.createElement('span',null,'')
            ),
            ex.sets.map((s,si)=>React.createElement('div',{key:si,className:'set-row'},
              React.createElement('div',{className:'set-badge'},si+1),
              React.createElement('input',{className:'set-input',type:'number',inputMode:'numeric',placeholder:'12',value:s.reps,onChange:e=>setField(ei,si,'reps',e.target.value)}),
              React.createElement('input',{className:'set-input',type:s.bw?'text':'number',inputMode:'decimal',placeholder:'кг',value:s.bw?s.weight+' кг':s.weight,disabled:s.bw,onChange:e=>{setField(ei,si,'weight',e.target.value);setField(ei,si,'bw',false)}}),
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
  function renderHistory(){
    return React.createElement(React.Fragment,null,
      React.createElement('div',{className:'history-header'},React.createElement('h2',null,'📊 Історія')),
      // tonnage card
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
          React.createElement('div',{className:'section-label'},'Всі тренування ('+history.length+')'),
          React.createElement('div',{className:'history-list'},history.map(([k,w])=>{
            const ton=calcTonnage(w);
            return React.createElement('div',{key:k,className:'history-card',onClick:()=>{
              const[y,m]=k.split('-').map(Number);setCalDate(new Date(y,m-1,1));setSelected(k);setTab('calendar');
            }},
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
              React.createElement('div',{className:'hc-exercises'},w.exercises.map((ex,i)=>React.createElement('div',{key:i,className:'hc-ex'},
                React.createElement('strong',null,ex.name),` — ${ex.sets.length} підх.`+(ex.sets[0]&&ex.sets[0].bw?' (СВ)':'')
              )))
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
    toast&&React.createElement('div',{key:toast,className:'toast'},toast)
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(App));
