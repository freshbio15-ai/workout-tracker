const { useState, useEffect, useCallback, useRef } = React;

const MUSCLES = ['Спина','Груди','Ноги','Плечі','Біцепс','Трицепс','Прес','Кардіо','Весь тіл'];
const STORAGE_KEY = 'gymbook-v2';
const WEEKDAYS = ['Нд','Пн','Вт','Ср','Чт','Пт','Сб'];
const MONTHS = ['Січень','Лютий','Березень','Квітень','Травень','Червень',
                'Липень','Серпень','Вересень','Жовтень','Листопад','Грудень'];

// ── storage ──────────────────────────────────────────────────────────
function load() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; }
  catch { return {}; }
}
function save(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

// ── date helpers ──────────────────────────────────────────────────────
function toKey(date) {
  return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;
}
function todayKey() { return toKey(new Date()); }
function formatFull(key) {
  const [y,m,d] = key.split('-').map(Number);
  const date = new Date(y, m-1, d);
  return date.toLocaleDateString('uk-UA', {weekday:'long', day:'numeric', month:'long'});
}

// ── empty helpers ─────────────────────────────────────────────────────
const mkSet  = () => ({ reps:'', weight:'', isBodyweight:false });
const mkExer = () => ({ name:'', sets:[mkSet()] });
const mkDay  = () => ({ muscle:'', exercises:[mkExer()] });

// ── calendar grid ─────────────────────────────────────────────────────
function buildGrid(year, month) {
  const first = new Date(year, month, 1);
  const startDow = first.getDay(); // 0=Sun
  const days = new Date(year, month+1, 0).getDate();
  const cells = [];
  for (let i=0; i<startDow; i++) cells.push(null);
  for (let d=1; d<=days; d++) cells.push(d);
  return cells;
}

// ══════════════════════════════════════════════════════════════════════
function App() {
  const [data, setData]         = useState(load);           // { 'YYYY-MM-DD': {muscle, exercises} }
  const [calDate, setCalDate]   = useState(new Date());     // month being viewed
  const [selected, setSelected] = useState(todayKey());     // currently selected day key
  const [draft, setDraft]       = useState(null);           // editing draft for selected day
  const [toast, setToast]       = useState(null);
  const toastTimer = useRef(null);

  useEffect(() => { save(data); }, [data]);

  // open day → load existing or blank draft
  useEffect(() => {
    if (!selected) { setDraft(null); return; }
    const existing = data[selected];
    if (existing) {
      setDraft(JSON.parse(JSON.stringify(existing)));
    } else {
      setDraft(mkDay());
    }
  }, [selected]);

  function showToast(msg) {
    clearTimeout(toastTimer.current);
    setToast(msg);
    toastTimer.current = setTimeout(() => setToast(null), 1800);
  }

  // ── calendar nav ──────────────────────────────────────────────────
  function prevMonth() { setCalDate(d => new Date(d.getFullYear(), d.getMonth()-1, 1)); }
  function nextMonth() { setCalDate(d => new Date(d.getFullYear(), d.getMonth()+1, 1)); }

  const year  = calDate.getFullYear();
  const month = calDate.getMonth();
  const grid  = buildGrid(year, month);
  const todayStr = todayKey();

  function selectDay(d) {
    if (!d) return;
    const key = toKey(new Date(year, month, d));
    setSelected(key);
  }

  // ── draft helpers ─────────────────────────────────────────────────
  function setMuscle(m) {
    setDraft(prev => ({ ...prev, muscle: m }));
  }

  function setExName(ei, val) {
    setDraft(prev => {
      const ex = prev.exercises.map((e,i) => i===ei ? {...e, name:val} : e);
      return { ...prev, exercises:ex };
    });
  }

  function setSetField(ei, si, field, val) {
    setDraft(prev => {
      const ex = prev.exercises.map((e,i) => i!==ei ? e : {
        ...e, sets: e.sets.map((s,j) => j!==si ? s : {...s, [field]:val})
      });
      return { ...prev, exercises:ex };
    });
  }

  function addSet(ei) {
    setDraft(prev => {
      const ex = prev.exercises.map((e,i) => i!==ei ? e : {...e, sets:[...e.sets, mkSet()]});
      return { ...prev, exercises:ex };
    });
  }

  function removeSet(ei, si) {
    setDraft(prev => {
      const ex = prev.exercises.map((e,i) => i!==ei ? e : {...e, sets:e.sets.filter((_,j)=>j!==si)});
      return { ...prev, exercises:ex };
    });
  }

  function addExercise() {
    setDraft(prev => ({ ...prev, exercises:[...prev.exercises, mkExer()] }));
  }

  function removeExercise(ei) {
    setDraft(prev => ({ ...prev, exercises:prev.exercises.filter((_,i)=>i!==ei) }));
  }

  // ── save / delete ─────────────────────────────────────────────────
  function saveDay() {
    if (!draft) return;
    const cleaned = {
      muscle: draft.muscle,
      exercises: draft.exercises
        .filter(e => e.name.trim())
        .map(e => ({
          name: e.name.trim(),
          sets: e.sets
            .filter(s => s.reps !== '' || s.weight !== '' || s.isBodyweight)
            .map(s => ({
              reps: s.reps === '' ? 0 : Number(s.reps),
              weight: s.isBodyweight ? 0 : (s.weight === '' ? 0 : Number(s.weight)),
              isBodyweight: !!s.isBodyweight
            }))
        }))
        .filter(e => e.sets.length > 0)
    };
    if (!cleaned.exercises.length) return;
    setData(prev => ({ ...prev, [selected]: cleaned }));
    showToast('✅ Тренування збережено!');
  }

  function deleteDay() {
    setData(prev => { const n={...prev}; delete n[selected]; return n; });
    setDraft(mkDay());
    showToast('🗑 Видалено');
  }

  // ── stats ─────────────────────────────────────────────────────────
  const totalDays = Object.keys(data).length;
  const totalSets = Object.values(data).reduce((a,d) =>
    a + d.exercises.reduce((b,e) => b + e.sets.length, 0), 0);
  const thisWeek = (() => {
    const now = new Date(); const start = new Date(now);
    start.setDate(now.getDate() - now.getDay()); start.setHours(0,0,0,0);
    return Object.keys(data).filter(k => new Date(k+'T00:00:00') >= start).length;
  })();

  // sorted history (newest first)
  const history = Object.entries(data)
    .sort((a,b) => b[0].localeCompare(a[0]))
    .slice(0, 10);

  // ── render helpers ────────────────────────────────────────────────
  function renderDraft() {
    if (!draft) return null;
    const hasData = data[selected];
    return React.createElement('div', { className:'day-panel' },
      // header
      React.createElement('div', { className:'day-panel-header' },
        React.createElement('div', null,
          React.createElement('div', { className:'day-panel-title' },
            selected === todayStr ? '📅 Сьогодні' : '📅 ' + formatFull(selected)
          ),
          React.createElement('div', { className:'day-panel-date' },
            hasData ? '✅ Тренування записано' : 'Нове тренування'
          )
        )
      ),
      // body
      React.createElement('div', { className:'day-panel-body' },
        // muscle chips
        React.createElement('div', { className:'muscle-row' },
          MUSCLES.map(m =>
            React.createElement('button', {
              key:m, className:'muscle-tag'+(draft.muscle===m?' active':''),
              onClick: () => setMuscle(m)
            }, m)
          )
        ),
        // exercises
        draft.exercises.map((ex, ei) =>
          React.createElement('div', { key:ei, className:'exercise-block' },
            React.createElement('div', { className:'ex-name-row' },
              React.createElement('input', {
                className:'ex-name-input',
                placeholder:'Назва вправи…',
                value: ex.name,
                onChange: e => setExName(ei, e.target.value)
              }),
              draft.exercises.length > 1 &&
              React.createElement('button', {
                className:'ex-remove-btn', onClick:()=>removeExercise(ei)
              }, '×')
            ),
            // sets header
            React.createElement('div', { className:'sets-header' },
              React.createElement('span', null, 'Сет'),
              React.createElement('span', null, 'Повт.'),
              React.createElement('span', null, 'Вага кг'),
              React.createElement('span', null, 'СВ'),
              React.createElement('span', null, '')
            ),
            // set rows
            ex.sets.map((s, si) =>
              React.createElement('div', { key:si, className:'set-row' },
                React.createElement('div', { className:'set-badge' }, si+1),
                React.createElement('input', {
                  className:'set-input', type:'number', inputMode:'numeric',
                  placeholder:'12',
                  value:s.reps, onChange:e=>setSetField(ei,si,'reps',e.target.value)
                }),
                React.createElement('input', {
                  className:'set-input', type:'text', inputMode:'decimal',
                  placeholder:'0',
                  value:s.isBodyweight ? 'СВ' : s.weight,
                  onChange:e=>setSetField(ei,si,'weight',e.target.value),
                  disabled: s.isBodyweight,
                  style: s.isBodyweight ? { opacity: 0.7 } : {}
                }),
                React.createElement('button', {
                  className:'bw-btn' + (s.isBodyweight ? ' active' : ''),
                  onClick: () => setSetField(ei, si, 'isBodyweight', !s.isBodyweight)
                }, 'СВ'),
                ex.sets.length > 1 ? React.createElement('button', {
                  className:'set-del-btn', onClick:()=>removeSet(ei,si)
                }, '×') : React.createElement('div', null)
              )
            ),
            React.createElement('button', { className:'add-set-btn', onClick:()=>addSet(ei) },
              '+ Підхід'
            )
          )
        ),
        React.createElement('button', { className:'add-ex-btn', onClick:addExercise },
          '+ Додати вправу'
        ),
        React.createElement('button', { className:'save-btn', onClick:saveDay },
          hasData ? '💾 Оновити тренування' : '✅ Зберегти тренування'
        ),
        hasData && React.createElement('button', { className:'del-day-btn', onClick:deleteDay },
          '🗑 Видалити день'
        )
      )
    );
  }

  function renderHistory() {
    if (!history.length) return React.createElement('div', { className:'empty-hint' },
      React.createElement('div', { className:'e-icon' }, '📔'),
      React.createElement('h3', null, 'Блокнот порожній'),
      React.createElement('p', null, 'Обери день у календарі та запиши перше тренування!')
    );

    return React.createElement('div', null,
      React.createElement('div', { className:'section-label' }, 'Останні тренування'),
      React.createElement('div', { className:'history-list' },
        history.map(([key, w]) =>
          React.createElement('div', {
            key, className:'history-card',
            onClick: () => {
              const [y,m,d] = key.split('-').map(Number);
              setCalDate(new Date(y, m-1, 1));
              setSelected(key);
              window.scrollTo({ top:0, behavior:'smooth' });
            }
          },
            React.createElement('div', { className:'hc-top' },
              React.createElement('div', null,
                React.createElement('div', { className:'hc-title' },
                  key === todayStr ? 'Сьогодні' : formatFull(key)
                ),
                React.createElement('div', { className:'hc-date' }, key)
              ),
              w.muscle && React.createElement('span', { className:'hc-muscle' }, w.muscle)
            ),
            React.createElement('div', { className:'hc-stats' },
              React.createElement('span', { className:'hc-stat' },
                React.createElement('strong', null, w.exercises.length), ' вправ'
              ),
              React.createElement('span', { className:'hc-stat' },
                React.createElement('strong', null, w.exercises.reduce((a,e)=>a+e.sets.length,0)), ' підходів'
              ),
              React.createElement('span', { className:'hc-stat' },
                React.createElement('strong', null,
                  w.exercises.reduce((a,e)=>a+e.sets.reduce((b,s)=>b+(Number(s.reps)||0)*(Number(s.weight)||0),0),0).toFixed(0)
                ), ' кг total'
              )
            )
          )
        )
      )
    );
  }

  // ── MAIN RENDER ───────────────────────────────────────────────────
  return React.createElement('div', { className:'page' },
    // header
    React.createElement('div', { className:'app-header' },
      React.createElement('div', { className:'app-logo' },
        React.createElement('div', { className:'logo-icon' }, '💪'),
        React.createElement('div', { className:'logo-text' },
          React.createElement('h1', null, 'Gym Notebook'),
          React.createElement('p', null, 'Твій щоденник тренувань')
        )
      )
    ),

    // stats
    React.createElement('div', { className:'stats-bar' },
      React.createElement('div', { className:'stat-pill' },
        React.createElement('div', { className:'stat-num' }, totalDays),
        React.createElement('div', { className:'stat-lbl' }, 'Днів')
      ),
      React.createElement('div', { className:'stat-pill' },
        React.createElement('div', { className:'stat-num' }, totalSets),
        React.createElement('div', { className:'stat-lbl' }, 'Підходів')
      ),
      React.createElement('div', { className:'stat-pill' },
        React.createElement('div', { className:'stat-num' }, thisWeek),
        React.createElement('div', { className:'stat-lbl' }, 'Тиждень')
      )
    ),

    // calendar
    React.createElement('div', { className:'calendar-wrap' },
      React.createElement('div', { className:'cal-nav' },
        React.createElement('button', { className:'cal-arrow', onClick:prevMonth }, '‹'),
        React.createElement('span', { className:'cal-month' }, `${MONTHS[month]} ${year}`),
        React.createElement('button', { className:'cal-arrow', onClick:nextMonth }, '›')
      ),
      React.createElement('div', { className:'cal-weekdays' },
        WEEKDAYS.map(w => React.createElement('div', { key:w, className:'cal-wd' }, w))
      ),
      React.createElement('div', { className:'cal-grid' },
        grid.map((d, idx) => {
          if (!d) return React.createElement('div', { key:'e'+idx, className:'cal-day empty' });
          const key = toKey(new Date(year, month, d));
          const isToday   = key === todayStr;
          const hasDat    = !!data[key];
          const isSel     = key === selected;
          let cls = 'cal-day';
          if (isToday)  cls += ' today';
          if (hasDat)   cls += ' has-workout';
          if (isSel)    cls += ' selected';
          return React.createElement('div', { key:d, className:cls, onClick:()=>selectDay(d) },
            d,
            hasDat && React.createElement('div', { className:'day-dot' })
          );
        })
      )
    ),

    // selected day editor
    selected && renderDraft(),

    // history
    renderHistory(),

    // toast
    toast && React.createElement('div', { key:toast, className:'toast' }, toast)
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(App));
