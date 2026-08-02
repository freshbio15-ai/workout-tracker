const { useState, useEffect, useRef, useCallback } = React;

// ── Текстові бейджики замість іконок ─────────────────────────────────
function _badge(label, s, c) {
  const isSmall = s <= 20;
  return React.createElement('div', {
    style: {
      borderRadius: '6px',
      background: 'rgba(255,255,255,0.07)',
      border: '1px solid rgba(255,255,255,0.13)',
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      fontSize: isSmall ? '9px' : '11px', fontWeight: 700, letterSpacing: '0.03em',
      color: c || 'currentColor', lineHeight: 1,
      fontFamily: 'inherit', userSelect: 'none',
      padding: isSmall ? '3px 5px' : '0 6px', whiteSpace: 'nowrap'
    }
  }, label);
}

const MuscleIcons = {
  chest:     (s=32, c) => _badge('Груди',       s, c),
  back:      (s=32, c) => _badge('Спина',       s, c),
  legs:      (s=32, c) => _badge('Ноги',        s, c),
  shoulders: (s=32, c) => _badge('Дельти',      s, c),
  triceps:   (s=32, c) => _badge('Трицепс',     s, c),
  biceps:    (s=32, c) => _badge('Біцепс',      s, c),
  calves:    (s=32, c) => _badge('Ікри',        s, c),
  traps:     (s=32, c) => _badge('Трапеція',    s, c),
  forearms:  (s=32, c) => _badge('Передпліччя', s, c),
  // додатково для секції вимірювань
  abs:       (s=32, c) => _badge('Прес',        s, c),
  glutes:    (s=32, c) => _badge('Ягодичні',    s, c),
};

const MUSCLES = [
  {id:'chest',     icon:'chest',     label:'Груди'},
  {id:'back',      icon:'back',      label:'Спина'},
  {id:'legs',      icon:'legs',      label:'Ноги'},
  {id:'shoulders', icon:'shoulders', label:'Дельти'},
  {id:'triceps',   icon:'triceps',   label:'Трицепс'},
  {id:'biceps',    icon:'biceps',    label:'Біцепс'},
  {id:'calves',    icon:'calves',    label:'Ікри'},
  {id:'traps',     icon:'traps',     label:'Трапеція'},
];

const STORAGE = 'gymbook-data';
const SETTINGS_KEY = 'gymbook-settings';
const WEEKDAYS = ['Нд','Пн','Вт','Ср','Чт','Пт','Сб'];
const MONTHS = ['Січень','Лютий','Березень','Квітень','Травень','Червень','Липень','Серпень','Вересень','Жовтень','Листопад','Грудень'];
const ADMIN_UID = 'e2SaU3SRA6NncTAfO34Gv5y5M6q1';

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
    batch.set(db.collection('users').doc(uid), { settings, userAgent: navigator.userAgent, updatedAt: firebase.firestore.FieldValue.serverTimestamp() }, { merge: true });
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
  let settings = null;
  let data = {};

  // Load user doc (settings) separately
  try {
    const userSnap = await db.collection('users').doc(uid).get();
    if (userSnap.exists && userSnap.data().settings) {
      settings = userSnap.data().settings;
    }
  } catch (e) {
    console.error('Cloud load settings error:', e);
  }

  // Load workouts separately — may be blocked by rules for non-admin
  try {
    const workoutsSnap = await userDoc(uid, 'workouts').get();
    workoutsSnap.forEach(doc => { data[doc.id] = doc.data(); });
  } catch (e) {
    console.error('Cloud load workouts error:', e);
    // workouts blocked by rules — return null so caller knows
    if (!settings) return null;
    return { data: {}, settings, _workoutsBlocked: true };
  }

  if (!settings && Object.keys(data).length === 0) return null;
  return { data, settings };
}
function toKey(d){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`}
function todayKey(){return toKey(new Date())}
function fmtFull(k){const[y,m,d]=k.split('-').map(Number);return new Date(y,m-1,d).toLocaleDateString('uk-UA',{weekday:'long',day:'numeric',month:'long'})}
function fmtShort(k){const[y,m,d]=k.split('-').map(Number);return new Date(y,m-1,d).toLocaleDateString('uk-UA',{day:'numeric',month:'short'})}

// ── SVGs ─────────────────────────────────────────────────────────────
const CalendarIcon = ({size=24, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('rect', {x: 3, y: 4, width: 18, height: 18, rx: 2, ry: 2}), React.createElement('line', {x1: 16, y1: 2, x2: 16, y2: 6}), React.createElement('line', {x1: 8, y1: 2, x2: 8, y2: 6}), React.createElement('line', {x1: 3, y1: 10, x2: 21, y2: 10}));
const HistoryIcon = ({size=24, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('line', {x1: 18, y1: 20, x2: 18, y2: 10}), React.createElement('line', {x1: 12, y1: 20, x2: 12, y2: 4}), React.createElement('line', {x1: 6, y1: 20, x2: 6, y2: 14}));
const SettingsIcon = ({size=24, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('circle', {cx: 12, cy: 12, r: 3}), React.createElement('path', {d: 'M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z'}));
const TimerIcon = ({size=24, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('circle', {cx: 12, cy: 13, r: 8}), React.createElement('path', {d: 'M12 9v4l2 2'}), React.createElement('line', {x1: 10, y1: 2, x2: 14, y2: 2}));
const TrendingUpIcon = ({size=24, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('polyline', {points: '23 6 13.5 15.5 8.5 10.5 1 18'}), React.createElement('polyline', {points: '17 6 23 6 23 12'}));
const ActivityIcon = ({size=24, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('polyline', {points: '22 12 18 12 15 21 9 3 6 12 2 12'}));
const CheckCircleIcon = ({size=14, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M22 11.08V12a10 10 0 1 1-5.93-9.14'}), React.createElement('polyline', {points: '22 4 12 14.01 9 11.01'}));
const RefreshIcon = ({size=14, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8'}), React.createElement('polyline', {points: '21 3 21 8 16 8'}));
const WifiIcon = ({size=14, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M5 12.55a11 11 0 0 1 14.08 0'}), React.createElement('path', {d: 'M1.42 9a16 16 0 0 1 21.16 0'}), React.createElement('path', {d: 'M8.53 16.11a6 6 0 0 1 6.95 0'}), React.createElement('line', {x1: 12, y1: 20, x2: 12.01, y2: 20}));
const WifiOffIcon = ({size=14, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('line', {x1: 2, y1: 2, x2: 22, y2: 22}), React.createElement('path', {d: 'M8.53 16.11a6 6 0 0 1 6.95 0'}), React.createElement('line', {x1: 12, y1: 20, x2: 12.01, y2: 20}));
const EditIcon = ({size=16, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7'}), React.createElement('path', {d: 'M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z'}));
const TrashIcon = ({size=16, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('polyline', {points: '3 6 5 6 21 6'}), React.createElement('path', {d: 'M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2'}), React.createElement('line', {x1: 10, y1: 11, x2: 10, y2: 17}), React.createElement('line', {x1: 14, y1: 11, x2: 14, y2: 17}));
const SaveIcon = ({size=16, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z'}), React.createElement('polyline', {points: '17 21 17 13 7 13 7 21'}), React.createElement('polyline', {points: '7 3 7 8 15 8'}));
const CheckIcon = ({size=16, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('polyline', {points: '20 6 9 17 4 12'}));
const BookIcon = ({size=48, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M4 19.5A2.5 2.5 0 0 1 6.5 17H20'}), React.createElement('path', {d: 'M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z'}));
const TargetIcon = ({size=16, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('circle', {cx: 12, cy: 12, r: 10}), React.createElement('circle', {cx: 12, cy: 12, r: 6}), React.createElement('circle', {cx: 12, cy: 12, r: 2}));
const LightbulbIcon = ({size=20, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M9 21h6'}), React.createElement('path', {d: 'M10 21v-4c0-1.5-2.5-3-3-5a5 5 0 1 1 10 0c0 2-3 3.5-3 5v4'}));
const WeightIcon = ({size=18, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z'}), React.createElement('line', {x1: 7, y1: 7, x2: 7.01, y2: 7}));
const SmartphoneIcon = ({size=18, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('rect', {x: 5, y: 2, width: 14, height: 20, rx: 2, ry: 2}), React.createElement('line', {x1: 12, y1: 18, x2: 12.01, y2: 18}));
const BarChartIcon = ({size=18, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('line', {x1: 12, y1: 20, x2: 12, y2: 10}), React.createElement('line', {x1: 18, y1: 20, x2: 18, y2: 4}), React.createElement('line', {x1: 6, y1: 20, x2: 6, y2: 16}));
const AlertTriangleIcon = ({size=18, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z'}), React.createElement('line', {x1: 12, y1: 9, x2: 12, y2: 13}), React.createElement('line', {x1: 12, y1: 17, x2: 12.01, y2: 17}));
const HourglassIcon = ({size=24, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M21 21H3'}), React.createElement('path', {d: 'M21 3H3'}), React.createElement('path', {d: 'M7 3v7l5 5 5-5V3'}), React.createElement('path', {d: 'M7 21v-7l5-5 5 5v7'}));
const XIcon = ({size=18, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('line', {x1: 18, y1: 6, x2: 6, y2: 18}), React.createElement('line', {x1: 6, y1: 6, x2: 18, y2: 18}));
const PlusIcon = ({size=16, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('line', {x1: 12, y1: 5, x2: 12, y2: 19}), React.createElement('line', {x1: 5, y1: 12, x2: 19, y2: 12}));
const ArrowLeftIcon = ({size=16, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('line', {x1: 19, y1: 12, x2: 5, y2: 12}), React.createElement('polyline', {points: '12 19 5 12 12 5'}));
const ArrowRightIcon = ({size=16, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('line', {x1: 5, y1: 12, x2: 19, y2: 12}), React.createElement('polyline', {points: '12 5 19 12 12 19'}));

const mkSet=()=>({reps:'',weight:'',bw:false});
const mkEx=()=>({name:'',muscle:'',sets:[mkSet()]});
const mkDay=()=>({muscle:'',exercises:[mkEx()]});

// Захист від побитих даних з Firestore
function sanitizeDraft(w) {
  if(!w || typeof w !== 'object') return mkDay();
  const exercises = Array.isArray(w.exercises) && w.exercises.length > 0
    ? w.exercises.map(ex => ({
        name:   typeof ex.name   === 'string' ? ex.name   : '',
        muscle: typeof ex.muscle === 'string' ? ex.muscle : '',
        sets: Array.isArray(ex.sets) && ex.sets.length > 0
          ? ex.sets.map(s => ({
              reps:   s.reps   !== undefined ? s.reps   : '',
              weight: s.weight !== undefined ? s.weight : '',
              bw:     !!s.bw,
              prevReps:   s.prevReps   || '',
              prevWeight: s.prevWeight || '',
            }))
          : [mkSet()]
      }))
    : [mkEx()];
  return { muscle: w.muscle || '', exercises };
}

function buildGrid(y,m){const f=new Date(y,m,1);const dow=f.getDay();const days=new Date(y,m+1,0).getDate();const c=[];for(let i=0;i<dow;i++)c.push(null);for(let d=1;d<=days;d++)c.push(d);return c}

function calcTonnage(workout){
  return workout.exercises.reduce((a,ex)=>a+ex.sets.reduce((b,s)=>{
    const w=Number(s.weight)||0;
    return b+(Number(s.reps)||0)*w;
  },0),0);
}

const THEMES = [
  { id:'classic', name:'Classic',  accent:'#e4e4e7', dark:'#6d28d9', bg:'#000000' },
  { id:'violet',  name:'Violet',   accent:'#a78bfa', dark:'#5b21b6', bg:'#07050f' },
  { id:'crimson', name:'Crimson',  accent:'#fb7185', dark:'#9f1239', bg:'#0c0508' },
  { id:'ocean',   name:'Ocean',    accent:'#38bdf8', dark:'#0369a1', bg:'#020b12' },
  { id:'forest',  name:'Forest',   accent:'#4ade80', dark:'#15803d', bg:'#030b06' },
];

// ══════════════════════════════════════════════════════════════════
function App(){

  const [data,setData]=useState(()=>load(STORAGE,{}));
  const [settings,setSettings]=useState(()=>load(SETTINGS_KEY,{userWeight:'',muscles:[]}));
  const [showThemePicker, setShowThemePicker] = useState(false);
  const [newMuscle,setNewMuscle]=useState('');
  const [tab,setTab]=useState('calendar');
  const [calDate,setCalDate]=useState(new Date());
  const [selected,setSelected]=useState(todayKey());
  const [draft,setDraft]=useState(null);
  const [toast,setToast]=useState(null);
  const [historyDetail,setHistoryDetail]=useState(null); // key of workout to show detail
  const [openInsights, setOpenInsights] = useState({});
  const [filterStart,setFilterStart]=useState('last');
  const [filterEnd,setFilterEnd]=useState('last');
  const getLatestWeight = () => {
    if(!settings.weightHistory) return null;
    const dates = Object.keys(settings.weightHistory).sort();
    if(dates.length === 0) return null;
    return Math.round(settings.weightHistory[dates[dates.length - 1]]);
  };
  const [showPicker,setShowPicker]=useState(false);
  const [pickerYear,setPickerYear]=useState(new Date().getFullYear());
  const [pickerMonth,setPickerMonth]=useState(new Date().getMonth());
  const [pickerStart,setPickerStart]=useState('');
  const [pickerEnd,setPickerEnd]=useState('');
  const [bwDate,setBwDate]=useState(todayKey());
  const [bwValue,setBwValue]=useState('');
  const [showBwPicker, setShowBwPicker] = useState(false);
  const [adminTaps, setAdminTaps] = useState({logo: false, sync: false});
  const [adminUidInput, setAdminUidInput] = useState('');
  const [bwUnit, setBwUnit] = useState('кг');
  const [bwPickerYear, setBwPickerYear] = useState(new Date().getFullYear());
  const [weightPage, setWeightPage] = useState(0);
  const [bwPickerMonth, setBwPickerMonth] = useState(new Date().getMonth());
  const [uid,setUid]=useState(null);
  const [showAdminModal, setShowAdminModal] = useState(false);
  const [adminAccounts, setAdminAccounts] = useState([]);
  const [measDate, setMeasDate] = useState(todayKey());
  const [measValue, setMeasValue] = useState('');
  const [measUnit, setMeasUnit] = useState('см');
  const [showMeasPicker, setShowMeasPicker] = useState(false);
  const [measPickerYear, setMeasPickerYear] = useState(new Date().getFullYear());
  const [measPickerMonth, setMeasPickerMonth] = useState(new Date().getMonth());
  const [measMuscleName, setMeasMuscleName] = useState('Груди');
  const [showMuscleModal, setShowMuscleModal] = useState(false);
  const [compareModal, setCompareModal] = useState(null); // {keyA, keyB} or null

  const MUSCLE_MEASUREMENTS = [
    {label:'Груди',          icon:'chest'},
    {label:'Спина',          icon:'back'},
    {label:'Талія',          icon:'abs'},
    {label:'Квадри лівий',   icon:'legs'},
    {label:'Квадри правий',  icon:'legs'},
    {label:'Ягодичні',       icon:'glutes'},
    {label:'Плечі',          icon:'shoulders'},
    {label:'Біц правий',     icon:'biceps'},
    {label:'Біц лівий',      icon:'biceps'},
    {label:'Ікри лівий',     icon:'calves'},
    {label:'Ікри правий',    icon:'calves'},
  ];

  const [confirmAction, setConfirmAction] = useState(null); // {title, onConfirm}
  const [editItem, setEditItem] = useState(null); // {type:'weight'|'meas', key, val, date, originalIndex}
  const [editVal, setEditVal] = useState('');

  const [cloudStatus,setCloudStatus]=useState('connecting'); // connecting | synced | saving | offline
  const [showCalendarPopup,setShowCalendarPopup]=useState(false);
  const tRef=useRef(null);
  const saveTimer=useRef(null);
  const isFirstLoad=useRef(true);
  const [hintSet, setHintSet] = useState(null); // {ei, si, field:'weight'|'reps'}

  // Check if a given weight is a PR for an exercise up to a certain date
  const checkPR = useCallback((exName, currentWeight, dateKey) => {
    if(!exName || !currentWeight || currentWeight <= 0) return false;
    let isPR = true;
    let hasPrevious = false;
    for(let d in data) {
      if(d < dateKey) {
        data[d].exercises.forEach(ex => {
          if(ex.name.toLowerCase().trim() === exName.toLowerCase().trim()) {
            ex.sets.forEach(s => {
              if(!s.bw && s.weight >= currentWeight) isPR = false;
              if(!s.bw && s.weight > 0) hasPrevious = true;
            });
          }
        });
      }
    }
    return isPR && hasPrevious; // Only highlight if it beats previous records (and there were previous records)
  }, [data]);


  // ── Firebase anonymous auth ──────────────────────────────────────
  useEffect(()=>{
    const unsub = auth.onAuthStateChanged(async (user)=>{
      if(user){
        const override = localStorage.getItem('override_uid');
        const activeUid = override || user.uid;
        setUid(activeUid);
        // load from cloud on first auth
        setCloudStatus('connecting');
        const cloud = await loadFromCloud(activeUid);
        if(cloud){
          const localKeys = Object.keys(load(STORAGE,{}));
          const cloudKeys = Object.keys(cloud.data);
          // merge: cloud wins if it has more data, otherwise keep local
          if(cloudKeys.length >= localKeys.length){
            setData(cloud.data);
            persist(STORAGE, cloud.data);
          }
          if(cloud.settings){
            const localS = load(SETTINGS_KEY, null);
            // Merge/Overwrite logic: only overwrite if local is missing or cloud is newer
            if(!localS || !localS.lastUpdated || (cloud.settings.lastUpdated && cloud.settings.lastUpdated > localS.lastUpdated)){
              setSettings(cloud.settings);
              persist(SETTINGS_KEY, cloud.settings);
            }
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
    if(ex) setDraft(sanitizeDraft(ex));
    else setDraft(mkDay());
  },[selected]);

  // Apply theme class to body
  useEffect(()=>{
    const t = settings.theme || 'classic';
    document.body.className = document.body.className.replace(/theme-\w+/g,'').trim();
    document.body.classList.add('theme-'+t);
  },[settings.theme]);

  // Show theme picker for new users (no theme set yet)
  useEffect(()=>{
    if(settings.theme === undefined) setShowThemePicker(true);
  },[]);
  function flash(m, actionText=null, actionFn=null, duration=1800){
    clearTimeout(tRef.current);
    const id = Date.now();
    setToast({m, actionText, actionFn, id, duration});
    tRef.current=setTimeout(()=>setToast(null), duration);
  }

  // ── Timer Logic Removed ────────────────────────────────────────

  // calendar
  const year=calDate.getFullYear(), month=calDate.getMonth();
  const grid=buildGrid(year,month);
  const tKey=todayKey();
  function selectDay(d){if(!d)return;setSelected(toKey(new Date(year,month,d)));setShowCalendarPopup(false)}

  // draft ops
  function setExName(ei,v){setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>i===ei?{...e,name:v}:e)}))}
  function setExMuscle(ei,m){
    setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>i===ei?{...e,muscle:e.muscle===m?'':m}:e)}));
    // Restore hint to weight field after muscle click (blur from name input clears it)
    setHintSet({ei, si:0, field:'weight'});
  }
  function setField(ei,si,f,v){setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>i!==ei?e:{...e,sets:e.sets.map((s,j)=>j!==si?s:{...s,[f]:v})})}))}
  function addSet(ei){
    setDraft(p=>{
      const updated = p.exercises.map((e,i)=>i!==ei?e:{...e,sets:[...e.sets,mkSet()]});
      const newSi = updated[ei].sets.length - 1;
      setHintSet({ei, si:newSi, field:'weight'});
      return {...p, exercises:updated};
    });
  }
  function rmSet(ei,si){setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>i!==ei?e:{...e,sets:e.sets.filter((_,j)=>j!==si)})}))}
  function addEx(){setDraft(p=>({...p,exercises:[...p.exercises,mkEx()]}))}
  function rmEx(ei){setDraft(p=>({...p,exercises:p.exercises.filter((_,i)=>i!==ei)}))}

  function toggleBW(ei){
    const ex = draft.exercises[ei];
    const allBw = ex.sets.every(s=>s.bw);
    const newBw = !allBw;
    
    if (newBw) {
      const latestW = getLatestWeight();
      if(!latestW){flash('Вкажи свою вагу в Аналітиці');setTab('analytics');return}
      setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>i===ei?{...e, sets: e.sets.map(s=>({...s, bw: newBw, weight: latestW}))}:e)}));
    } else {
      setDraft(p=>({...p,exercises:p.exercises.map((e,i)=>i===ei?{...e, sets: e.sets.map(s=>({...s, bw: newBw, weight: ''}))}:e)}));
    }
  }

  function setMuscle(m){
    const newM = draft.muscle === m ? '' : m;

    // Auto-save current exercises as template for the outgoing muscle group
    if(draft.muscle && draft.muscle !== newM){
      const outgoing = draft.exercises.filter(e=>e.name.trim()).map(e=>({
        name: e.name.trim(), muscle: e.muscle||'',
        sets: e.sets.length > 0 ? e.sets.map(s=>({bw:!!s.bw})) : [{bw:false}]
      }));
      if(outgoing.length > 0){
        setSettings(s=>({...s, templates:{...(s.templates||{}), [draft.muscle]:outgoing}}));
      }
    }

    if(newM === ''){
      setDraft(p=>({...p, muscle:'', exercises:[mkEx()]}));
      return;
    }

    // Load incoming muscle's dedicated template
    const tmpl = (settings.templates||{})[newM];
    if(tmpl && tmpl.length > 0){
      const lastW = Object.entries(data).sort((a,b)=>b[0].localeCompare(a[0])).find(([k,w])=>k!==selected && w.muscle===newM);
      const newExs = tmpl.map(tex=>{
        const prevEx = lastW && lastW[1].exercises.find(e=>e.name===tex.name);
        return {
          name: tex.name, muscle: tex.muscle||'',
          sets: tex.sets.map((ts,si)=>{
            const prevSet = prevEx && prevEx.sets[si];
            return {reps:'', weight:'', bw:!!ts.bw, prevReps:prevSet?prevSet.reps:'', prevWeight:prevSet?prevSet.weight:''};
          })
        };
      });
      setDraft(p=>({...p, muscle:newM, exercises:newExs}));
      setHintSet({ei:0, si:0, field:'weight'});
      return;
    }

    // Fall back to history if no dedicated template yet
    const lastW = Object.entries(data).sort((a,b)=>b[0].localeCompare(a[0])).find(([k,w])=>k!==selected && w.muscle===newM);
    if(lastW){
      const newExs = lastW[1].exercises.map(ex=>({
        name:ex.name, muscle:ex.muscle||'', sets:ex.sets.map(s=>({reps:'', weight:'', bw:s.bw, prevReps:s.reps, prevWeight:s.weight}))
      }));
      setDraft(p=>({...p, muscle:newM, exercises:newExs}));
    } else {
      setDraft(p=>({...p, muscle:newM, exercises:[mkEx()]}));
    }
    // Restore hint to weight of first exercise after switching muscle group
    setHintSet({ei:0, si:0, field:'weight'});
  }
  function saveDay(){
    if(!draft)return;
    const cl={muscle:draft.muscle,exercises:draft.exercises.filter(e=>e.name.trim()).map(e=>({name:e.name.trim(),muscle:e.muscle||'',sets:e.sets.filter(s=>s.reps!==''||s.weight!==''||s.bw).map(s=>({reps:Number(s.reps)||0,weight:s.bw?Number(getLatestWeight())||0:Number(s.weight)||0,bw:!!s.bw,rest:Number(s.rest)||0}))}))};
    if(!cl.exercises.length)return;
    setData(p=>({...p,[selected]:cl}));
    // Auto-save template for this muscle group
    if(draft.muscle){
      const templateExs = draft.exercises.filter(e=>e.name.trim()).map(e=>({
        name: e.name.trim(), muscle: e.muscle||'',
        sets: e.sets.length > 0 ? e.sets.map(s=>({bw:!!s.bw})) : [{bw:false}]
      }));
      if(templateExs.length > 0){
        setSettings(s=>({...s, templates:{...(s.templates||{}), [draft.muscle]:templateExs}}));
      }
    }
    flash('Збережено!');
  }

  function deleteDay(k){const key = typeof k === 'string' ? k : selected; if(!window.confirm('Дійсно видалити це тренування?')) return; setData(p=>{const n={...p};delete n[key];return n});if(selected===key)setDraft(mkDay());setHistoryDetail(null);flash('Видалено')}

  // stats
  const sortedKeysData = Object.keys(data).sort();
  const lastKeyData = sortedKeysData.length > 0 ? sortedKeysData[sortedKeysData.length - 1] : '';
  let actualStart = filterStart;
  let actualEnd = filterEnd;
  if (filterStart === 'last') {
    actualStart = lastKeyData;
    actualEnd = lastKeyData;
  } else if (filterStart === 'all') {
    actualStart = '';
    actualEnd = '';
  }

  const filteredDataEntries = Object.entries(data).filter(([k])=>{
    if(actualStart && k < actualStart) return false;
    if(actualEnd && k > actualEnd) return false;
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
        const mg = MUSCLES.find(e=>e.id===m);
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
        const mg = MUSCLES.find(e=>e.id===m);
        if(!mg) return;
        if(!seen.has(mg.id)){ seen.add(mg.id); if(map[mg.id]) map[mg.id].days++; }
      });
    });
    return Object.entries(map).sort((a,b)=>b[1].sets-a[1].sets);
  })();
  // ─── CALENDAR TAB ───────────────────────────────────────────────
  function renderCalendar(){
    const hasData=data[selected];
    return React.createElement(React.Fragment,null,
      // calendar trigger
      React.createElement('div', {style: {marginBottom: '16px', display: 'flex', justifyContent: 'center'}},
        React.createElement('button', {
          className: 'date-trigger-btn',
          onClick: () => setShowCalendarPopup(true)
        }, React.createElement(CalendarIcon, {size: 16, style:{marginTop:'-2px'}}), React.createElement('span', null, selected === tKey ? 'Сьогодні ▾' : fmtFull(selected) + ' ▾'))
      ),
      // calendar modal
      showCalendarPopup && React.createElement('div',{className:'cc-overlay',onClick:()=>setShowCalendarPopup(false)},
        React.createElement('div',{className:'cc-modal',onClick:e=>e.stopPropagation(),style:{padding:0,overflow:'hidden'}},
          React.createElement('div',{className:'calendar-wrap',style:{marginBottom:0,border:'none',borderRadius:0}},
            React.createElement('div',{className:'cal-nav'},
              React.createElement('button',{className:'cal-arrow',onClick:()=>setCalDate(d=>new Date(d.getFullYear(),d.getMonth()-1,1))},React.createElement(ArrowLeftIcon)),
              React.createElement('span',{className:'cal-month'},`${MONTHS[month]} ${year}`),
              React.createElement('button',{className:'cal-arrow',onClick:()=>setCalDate(d=>new Date(d.getFullYear(),d.getMonth()+1,1))},React.createElement(ArrowRightIcon))
            ),
            React.createElement('div',{className:'cal-weekdays'},WEEKDAYS.map(w=>React.createElement('div',{key:w,className:'cal-wd'},w))),
            React.createElement('div',{className:'cal-grid'},grid.map((d,idx)=>{
              if(!d)return React.createElement('div',{key:'e'+idx,className:'cal-day empty'});
              const k=toKey(new Date(year,month,d));
              let cls='cal-day';
              if(k===tKey)cls+=' today';
              if(data[k])cls+=' has-workout';
              if(k===selected)cls+=' selected';
              return React.createElement('div',{key:idx,className:cls,onClick:()=>selectDay(d)},d,data[k]&&React.createElement('div',{className:'day-dot '+(k<tKey?'past':'current')}));
            }))
          )
        )
      ),
      // day editor
      selected&&draft&&React.createElement('div',{className:'day-panel'},
        React.createElement('div',{className:'day-panel-header', style: {paddingBottom: '0', borderBottom: 'none'}},
          React.createElement('div',null,
            React.createElement('div',{className:'day-panel-title', style: {fontSize: '18px'}},hasData?React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'6px'}}, React.createElement(EditIcon), 'Редагування тренування'):React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'6px'}}, React.createElement(PlusIcon), 'Нове тренування'))
          )
        ),
        React.createElement('div',{className:'day-panel-body'},
          React.createElement('div',{className:'muscle-row'},
            (settings.muscles||[]).map(m=>React.createElement('button',{key:m,className:'muscle-tag'+(draft.muscle===m?' active':''),onClick:()=>setMuscle(m)},
              m,
              React.createElement('span',{className:'chip-del',onClick:e=>{
                e.stopPropagation();
                setSettings(s=>({...s, muscles:s.muscles.filter(x=>x!==m), deletedMuscles: [...(s.deletedMuscles||[]), m]}));
                if(draft.muscle===m)setMuscle('');
                flash('Шаблон видалено', 'Відновити', () => {
                  setSettings(s=>({
                    ...s, 
                    muscles: [...(s.muscles||[]), m], 
                    deletedMuscles: (s.deletedMuscles||[]).filter(x=>x!==m)
                  }));
                }, 5000);
              }},React.createElement(XIcon))
            )),
            React.createElement('div',{className:'add-muscle-wrap'},
              React.createElement('input',{className:'add-muscle-input',placeholder:'Назва…',value:newMuscle,onChange:e=>setNewMuscle(e.target.value),
                onKeyDown:e=>{if(e.key==='Enter'&&newMuscle.trim()){setSettings(s=>({...s,muscles:[...(s.muscles||[]),newMuscle.trim()]}));setNewMuscle('')}}
              }),
              React.createElement('button',{className:'add-muscle-btn',onClick:()=>{if(newMuscle.trim()){setSettings(s=>({...s,muscles:[...(s.muscles||[]),newMuscle.trim()]}));setNewMuscle('')}}},React.createElement(PlusIcon)))
          ),
          draft.exercises.map((ex,ei)=>React.createElement('div',{key:ei,className:'exercise-block'},
            React.createElement('div',{className:'ex-name-row'},
              React.createElement('input',{className:'ex-name-input'+(ex.name===''?' hint-name':''),placeholder:'Назва вправи…',value:ex.name,
                onChange:e=>setExName(ei,e.target.value),
                onFocus:()=>setHintSet({ei,si:0,field:'weight'}),
                onBlur:()=>setHintSet(h=>h&&h.ei===ei&&h.field==='weight'?null:h)
              }),
              draft.exercises.length>1&&React.createElement('button',{className:'ex-remove-btn',onClick:()=>rmEx(ei)},React.createElement(XIcon))
            ),
            // muscle selector per exercise
            React.createElement('div',{className:'emoji-muscle-row'},
              MUSCLES.map(mg=>React.createElement('button',{
                key:mg.id,
                className:'emoji-muscle-btn'+(ex.muscle===mg.id?' active':''),
                onClick:()=>setExMuscle(ei,mg.id)
              }, mg.label))
            ),
            // "Минулого разу" hint
            
            // BW toggle at exercise level
            settings.showBwToggle !== false && React.createElement('button',{className:'bw-toggle-btn'+(ex.sets[0].bw?' active':''),onClick:()=>toggleBW(ei),style:{marginBottom:'12px',width:'100%',padding:'8px 12px',borderRadius:'10px',border:'1px solid '+(ex.sets[0].bw?'rgba(16,185,129,.3)':'var(--border)'),background:ex.sets[0].bw?'rgba(16,185,129,.12)':'var(--bg3)',color:ex.sets[0].bw?'var(--green2)':'var(--text3)',fontSize:'12px',fontWeight:'700',cursor:'pointer',display:'flex',alignItems:'center',justifyContent:'center',gap:'6px',transition:'all .15s',fontFamily:'inherit'}},
              React.createElement('span',null,'🏃'),ex.sets[0].bw?'Своя вага (увімкнено)':'Вправа зі своєю вагою'
            ),
            React.createElement('div',{className:'sets-header'},
              React.createElement('span', {style:{color:'var(--text2)', whiteSpace:'nowrap', overflow:'visible', position:'relative', zIndex:5, textTransform:'uppercase'}}, (() => {
                const mg = MUSCLES.find(m => m.id === ex.muscle);
                return mg ? mg.label : 'Сет';
              })()),
              React.createElement('span',null,'Вага'),
              React.createElement('span',null,''),
              React.createElement('span',null,'Повтори'),
              React.createElement('span',null,'')
            ),
            ex.sets.map((s,si)=>{
              const isPR = !s.bw && s.weight && checkPR(ex.name, Number(s.weight), selected);
              return React.createElement('div',{key:si,className: si===0?'set-row set-row-first':'set-row'},
                React.createElement('div',{className:'set-badge', style: isPR ? {boxShadow: '0 0 8px #10b981', color: '#10b981'} : {}}, si+1),
                React.createElement('input',{className:'set-input'+(hintSet&&hintSet.ei===ei&&hintSet.si===si&&hintSet.field==='weight'?' hint-pulse':''),type:s.bw?'text':'number',inputMode:'decimal',placeholder:(settings.showPrevPlaceholder !== false && s.prevWeight) ? s.prevWeight : 'кг',value:s.bw?s.weight+' кг':s.weight,disabled:s.bw,
                  onChange:e=>{setField(ei,si,'weight',e.target.value);setField(ei,si,'bw',false)},
                  onFocus:()=>setHintSet({ei,si,field:'reps'}),
                  onBlur:()=>setHintSet(h=>h&&h.ei===ei&&h.si===si&&h.field==='reps'?null:h)
                }),
                React.createElement('div', {style:{color:'var(--text3)', fontSize:'12px', fontWeight:'700', textAlign:'center', marginTop:'2px'}}, '✕'),
                React.createElement('input',{className:'set-input'+(hintSet&&hintSet.ei===ei&&hintSet.si===si&&hintSet.field==='reps'?' hint-pulse':''),type:'number',inputMode:'numeric',placeholder:(settings.showPrevPlaceholder !== false && s.prevReps) ? s.prevReps : '12',value:s.reps,
                  onChange:e=>setField(ei,si,'reps',e.target.value),
                  onFocus:()=>setHintSet(null),
                  onBlur:()=>setHintSet(null)
                }),
                si>0?React.createElement('button',{className:'set-del-btn',onClick:()=>rmSet(ei,si)},React.createElement(XIcon)):React.createElement('div')
              );
            }),
            React.createElement('div',{className:'add-set-row'},
              React.createElement('button',{className:'add-set-btn',onClick:()=>addSet(ei)},React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'}}, React.createElement(PlusIcon), 'Підхід'))
            )
          )),
          React.createElement('button',{className:'add-ex-btn',onClick:addEx},React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'}}, React.createElement(PlusIcon), 'Додати вправу')),
          React.createElement('button',{className:'save-btn',onClick:saveDay},hasData?React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'8px'}}, React.createElement(SaveIcon), 'Оновити'):React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'8px'}}, React.createElement(CheckIcon), 'Зберегти тренування')),
            
          null
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
    const validExercises = w.exercises.filter(ex=>ex.sets.length>0);
    const exTons=validExercises.map(ex=>({name:ex.name,ton:calcExTonnage(ex),sets:ex.sets}));
    const maxExTon=Math.max(...exTons.map(e=>e.ton),1);

    return React.createElement(React.Fragment,null,
      // back button
      React.createElement('div',{style:{display:'flex',alignItems:'center',gap:'12px',marginBottom:'16px'}},
        React.createElement('button',{className:'cal-arrow',onClick:()=>setHistoryDetail(null)},React.createElement(ArrowLeftIcon)),
        React.createElement('div',null,
          React.createElement('div',{style:{fontSize:'16px',fontWeight:800}},k===tKey?'Сьогодні':fmtFull(k)),
          React.createElement('div',{style:{fontSize:'12px',color:'var(--text3)',marginTop:'2px'}},w.muscle?React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'4px'}}, React.createElement(TargetIcon, {size:12}), w.muscle):k)
        )
      ),
      // total tonnage for this day
      React.createElement('div',{className:'tonnage-card'},
        React.createElement('div',{className:'tonnage-value'},ton>1000?(ton/1000).toFixed(1)+' т':ton+' кг'),
        
        React.createElement('div',{className:'tonnage-row'},
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},validExercises.length),React.createElement('div',{className:'tonnage-item-lbl'},'Вправ')),
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},w.exercises.reduce((a,e)=>a+e.sets.length,0)),React.createElement('div',{className:'tonnage-item-lbl'},'Підходів')),
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},w.exercises.reduce((a,e)=>a+e.sets.reduce((b,s)=>b+(Number(s.reps)||0),0),0)),React.createElement('div',{className:'tonnage-item-lbl'},'Повторень'))
        )
      ),
      // per-exercise tonnage chart
      
      React.createElement('div',{className:'muscle-breakdown',style:{marginBottom:'24px'}},
        exTons.map((ex,i)=>
          React.createElement('div',{key:i,className:'mb-row'},
            React.createElement('div',{className:'mb-label'},ex.name),
            React.createElement('div',{className:'mb-bar-wrap'},
              React.createElement('div',{className:'mb-bar c'+i%8,style:{width:Math.max(Math.round(ex.ton/maxExTon*100),3)+'%'}})
            ),
            React.createElement('div',{className:'mb-val'},ex.ton>1000?(ex.ton/1000).toFixed(1)+'т':ex.ton+'кг')
          )
        )
      ),
      // detailed exercises
      
      validExercises.map((ex,i)=>{
        const exTon=calcExTonnage(ex);
        
        function analyzeDrops(sets) {
          if (sets.length < 2) return null;
          const firstWeight = sets[0].bw ? 'bw' : sets[0].weight;
          const sameWeight = sets.every(s => (s.bw ? 'bw' : s.weight) === firstWeight);
          if (!sameWeight) return null;
          
          const reps = sets.map(s => Number(s.reps) || 0);
          if (Math.max(...reps) < 8) return null;

          let maxDropPct = 0;
          let worstDropInfo = null;
          let dropsStrs = [];

          for (let i = 1; i < sets.length; i++) {
            const prevReps = reps[i-1];
            const currReps = reps[i];
            if (prevReps === 0) continue;
            const dropPct = (prevReps - currReps) / prevReps;
            const restTime = 0; // rest field removed from sets
            
            const pctVal = Math.round(dropPct * 100);
            if (pctVal > 0) dropsStrs.push(`${prevReps}→${currReps} (-${pctVal}%)`);
            else dropsStrs.push(`${prevReps}→${currReps}`);
            
            if (dropPct > maxDropPct) {
              maxDropPct = dropPct;
              worstDropInfo = { idx: i, prev: prevReps, curr: currReps, pct: pctVal, rest: restTime };
            }
          }

          if (!worstDropInfo || maxDropPct <= 0) return null;
          
          const dStr = `Динаміка: ` + dropsStrs.join(', ');

          if (maxDropPct >= 0.4) {
            if (worstDropInfo.rest > 0 && worstDropInfo.rest <= 90) {
              return { 
                color: 'var(--blue)', bg: 'rgba(59,130,246,0.1)', border: 'rgba(59,130,246,0.2)',
                pct: worstDropInfo.pct, max: worstDropInfo.prev, min: worstDropInfo.curr,
                msg: dStr,
                advice: `Очікуваний спад через короткий відпочинок (${worstDropInfo.rest}с) перед ${worstDropInfo.idx+1}-м сетом. Для сили відпочивай більше.` 
              };
            }
            return { 
              color: 'var(--red)', bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.2)',
              pct: worstDropInfo.pct, max: worstDropInfo.prev, min: worstDropInfo.curr,
              msg: dStr,
              advice: `Критичне падіння перед ${worstDropInfo.idx+1}-м сетом. Збільш відпочинок до 3-5 хв або знизь вагу.` 
            };
          } else if (maxDropPct >= 0.2) {
            return { 
              color: 'var(--orange)', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.2)',
              pct: Math.round(maxDropPct*100), max: worstDropInfo.prev, min: worstDropInfo.curr,
              msg: dStr,
              advice: 'Нормальна втома для гіпертрофії. Тримай поточну вагу та час відпочинку.' 
            };
          } else {
            return { 
              color: 'var(--green)', bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.2)',
              pct: Math.round(maxDropPct*100), max: worstDropInfo.prev, min: worstDropInfo.curr,
              msg: dStr,
              advice: 'Відмінна витривалість! Можна спробувати додати вагу на наступному тренуванні.' 
            };
          }
        }
        const insight = analyzeDrops(ex.sets);

        return React.createElement('div',{key:i,className:'detail-ex-card'},
          React.createElement('div',{className:'detail-ex-header'},
            React.createElement('div',{className:'detail-ex-name',style:{display:'flex',alignItems:'center',gap:'6px'}},(()=>{const mg=MUSCLES.find(e=>e.id===(ex.muscle||''));return mg?(MuscleIcons[mg.icon]?MuscleIcons[mg.icon](16):null):null})(),ex.name),
            React.createElement('div',{className:'detail-ex-ton'},exTon>1000?(exTon/1000).toFixed(1)+' т':exTon+' кг')
          ),
          React.createElement('table',{className:'detail-table'},
            React.createElement('thead',null,
              React.createElement('tr',null,
                React.createElement('th',null,'Сет'),
                React.createElement('th',null,'Вага'),
                React.createElement('th',null,''),
                React.createElement('th',null,'Повт.'),
                React.createElement('th',null,'Об\'єм')
              )
            ),
            React.createElement('tbody',null,
              ex.sets.map((s,j)=>React.createElement('tr',{key:j},
                React.createElement('td',null,React.createElement('span',{className:'set-badge'},j+1)),
                React.createElement('td',null,s.bw?'СВ ('+s.weight+'кг)':s.weight+' кг'),
                React.createElement('td',{style:{color:'var(--text3)', fontSize:'11px', textAlign:'center', fontWeight:'700', padding:'0'}},'✕'),
                React.createElement('td',null,s.reps),
                React.createElement('td',{className:'detail-vol'},Math.round((Number(s.reps)||0)*(Number(s.weight)||0))+' кг')
              ))
            )
          ),
          insight && React.createElement('div', {style:{marginTop:'12px', display:'flex', flexDirection:'column', gap:'8px'}},
            React.createElement('button', {
              onClick: () => setOpenInsights(prev => ({...prev, [i]: !prev[i]})),
              style: {
                background: openInsights[i] ? insight.bg : 'transparent',
                border: '1px solid ' + (openInsights[i] ? insight.border : 'var(--border)'),
                color: openInsights[i] ? insight.color : 'var(--text2)',
                padding: '6px 12px', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '6px',
                cursor: 'pointer', fontSize: '12px', fontWeight: '600', transition: 'all 0.2s', alignSelf: 'flex-start'
              }
            }, React.createElement(LightbulbIcon, {size:14}), openInsights[i] ? 'Приховати аналіз' : 'Аналіз витривалості'),
            
            openInsights[i] && React.createElement('div',{className:'insight-box',style:{background:insight.bg,borderColor:insight.border, marginTop:0}},
              React.createElement('div',{className:'insight-content'},
                React.createElement('h4',{className:'insight-title',style:{color:insight.color}},'Аналіз витривалості'),
                React.createElement('p',{className:'insight-text'},
                  `Повторення впали на `,
                  React.createElement('strong',null,`${insight.pct}%`),
                  ` (з ${insight.max} до ${insight.min}). ${insight.msg}`,
                  React.createElement('br'),React.createElement('br'),
                  React.createElement('strong',null,'Порада: '), insight.advice
                )
              )
            )
          )
        );
      }),
      // compare + edit + delete buttons
      React.createElement('div',{style:{display:'flex',gap:'8px',marginTop:'16px'}},
        React.createElement('button',{
          className:'save-btn',
          style:{flex:1,background:'var(--bg4)',boxShadow:'none',border:'1px solid var(--border)'},
          onClick:()=>{
            // Find previous workout with same muscles
            const allKeys = Object.keys(data).sort();
            const idx = allKeys.indexOf(k);
            const muscle = w.muscle || '';
            // Search backwards for workout with overlapping muscles
            let prevKey = null;
            for(let i = idx-1; i >= 0; i--){
              const pk = allKeys[i];
              const pw = data[pk];
              if(!pw || !pw.exercises || pw.exercises.length === 0) continue;
              // match if same muscle tag OR any exercise name matches
              const pwMuscle = pw.muscle || '';
              const sameTag = muscle && pwMuscle && (
                muscle.split(',').map(s=>s.trim()).some(m => pwMuscle.includes(m)) ||
                pwMuscle.split(',').map(s=>s.trim()).some(m => muscle.includes(m))
              );
              const exNames = w.exercises.map(e=>e.name.toLowerCase().trim()).filter(Boolean);
              const pwExNames = pw.exercises.map(e=>e.name.toLowerCase().trim()).filter(Boolean);
              const sameEx = exNames.some(n => pwExNames.includes(n));
              if(sameTag || sameEx){ prevKey = pk; break; }
            }
            if(!prevKey){
              // Just take the previous workout regardless
              const allKeys2 = Object.keys(data).sort();
              const i = allKeys2.indexOf(k);
              if(i > 0) prevKey = allKeys2[i-1];
            }
            if(prevKey) setCompareModal({keyA: prevKey, keyB: k});
            else flash('Немає попередніх тренувань для порівняння');
          }
        }, React.createElement('div',{style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'}}, '⚡ Порівняти')),
        React.createElement('button',{
          className:'save-btn',
          style:{flex:1,background:'var(--bg4)',boxShadow:'none',border:'1px solid var(--border)'},
          onClick:()=>{
            const[y,m]=k.split('-').map(Number);
            const workout = data[k];
            setCalDate(new Date(y,m-1,1));
            setSelected(k);
            setDraft(sanitizeDraft(workout));
            setTab('calendar');
            setHistoryDetail(null);
          }
        }, React.createElement('div',{style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'}}, React.createElement(EditIcon), 'Ред.'))
      ),
      React.createElement('button',{className:'del-day-btn',style:{marginTop:'12px'},onClick:()=>deleteDay(k)},React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'}}, React.createElement(TrashIcon), 'Видалити'))
    );
  }

  function renderCompareModal(){
    if(!compareModal) return null;
    const { keyA, keyB } = compareModal;
    const wA = data[keyA];
    const wB = data[keyB];
    if(!wA || !wB) return null;

    // ── Core stats ──────────────────────────────────────────────
    const tonA = calcTonnage(wA);
    const tonB = calcTonnage(wB);
    const tonDiff = tonB - tonA;
    const tonPct = tonA > 0 ? Math.round((tonDiff/tonA)*100) : 0;
    const setsA = wA.exercises.reduce((a,e)=>a+e.sets.length,0);
    const setsB = wB.exercises.reduce((a,e)=>a+e.sets.length,0);
    const repsA = wA.exercises.reduce((a,e)=>a+e.sets.reduce((b,s)=>b+(Number(s.reps)||0),0),0);
    const repsB = wB.exercises.reduce((a,e)=>a+e.sets.reduce((b,s)=>b+(Number(s.reps)||0),0),0);

    // Quality reps = reps in hypertrophy range 6-20 with weight > 0
    function qualityReps(exercises){
      return exercises.reduce((a,e)=>a+e.sets.reduce((b,s)=>{
        const r=Number(s.reps)||0; const w=Number(s.weight)||0;
        return b+(r>=6&&r<=20&&w>0?r:0);
      },0),0);
    }
    const qualA = qualityReps(wA.exercises);
    const qualB = qualityReps(wB.exercises);
    const qualDiff = qualB - qualA;

    // ── Per-exercise comparisons ─────────────────────────────────
    const exComps = [];
    wB.exercises.forEach(exB => {
      if(!exB.name) return;
      const exA = wA.exercises.find(e=>e.name&&e.name.toLowerCase().trim()===exB.name.toLowerCase().trim());
      const maxWB = exB.sets.length ? Math.max(...exB.sets.map(s=>Number(s.weight)||0)) : 0;
      const maxRB = exB.sets.length ? Math.max(...exB.sets.map(s=>Number(s.reps)||0)) : 0;
      const maxWA = exA ? Math.max(...exA.sets.map(s=>Number(s.weight)||0)) : null;
      const maxRA = exA ? Math.max(...exA.sets.map(s=>Number(s.reps)||0)) : null;
      const tonExA = exA ? calcExTonnage(exA) : null;
      const tonExB = calcExTonnage(exB);
      const qualExA = exA ? exA.sets.reduce((a,s)=>{const r=Number(s.reps)||0,w=Number(s.weight)||0;return a+(r>=6&&r<=20&&w>0?r:0);},0) : null;
      const qualExB = exB.sets.reduce((a,s)=>{const r=Number(s.reps)||0,w=Number(s.weight)||0;return a+(r>=6&&r<=20&&w>0?r:0);},0);
      const wDiff = maxWA!==null ? maxWB-maxWA : null;
      const rDiff = maxRA!==null ? maxRB-maxRA : null;
      const vDiff = tonExA!==null ? tonExB-tonExA : null;
      const qDiff = qualExA!==null ? qualExB-qualExA : null;

      // Hypertrophy score: quality reps > volume > PRs
      const hyScore = (qDiff>0?qDiff*4:0)+(rDiff>0&&wDiff===0?rDiff*3:0)+(vDiff>0?vDiff/40:0)+(wDiff>0?wDiff*1.5:0);

      let tag = 'stable';
      if(maxWA===null) tag='new';
      else if(qDiff>0&&wDiff===0) tag='more_reps';
      else if(wDiff>0) tag='pr';
      else if(vDiff>0) tag='volume';
      exComps.push({name:exB.name,maxWA,maxWB,maxRA,maxRB,tonExA,tonExB,wDiff,rDiff,vDiff,qDiff,qualExA,qualExB,hyScore,tag});
    });

    // ── Hero achievements (hypertrophy-first) ───────────────────
    const muscleLabel = (wB.muscle||'').split(',')[0].trim();
    const achievements = [];
    const repGains = exComps.filter(e=>e.rDiff>0&&e.wDiff===0).sort((a,b)=>b.rDiff-a.rDiff);
    const qualGains = exComps.filter(e=>e.qDiff>0).sort((a,b)=>b.qDiff-a.qDiff);
    const prEx = exComps.filter(e=>e.wDiff>0).sort((a,b)=>b.wDiff-a.wDiff);
    const newEx = exComps.filter(e=>e.tag==='new');
    repGains.forEach(e=>achievements.push({icon:'\ud83d\udcc8',text:'+'+e.rDiff+' \u043f\u043e\u0432\u0442. \u2014 '+e.name,color:'var(--green2)'}));
    if(qualDiff>0&&repGains.length===0) achievements.push({icon:'\u2b50',text:'\u0411\u0456\u043b\u044c\u0448\u0435 \u044f\u043a\u0456\u0441\u043d\u0438\u0445 \u043f\u043e\u0432\u0442\u043e\u0440\u0435\u043d\u044c: +'+qualDiff,color:'var(--green2)'});
    prEx.forEach(e=>achievements.push({icon:'\ud83c\udfc6',text:'New PR: '+e.name+' \u2014 '+e.maxWB+' \u043a\u0433',color:'#f59e0b'}));
    newEx.forEach(e=>achievements.push({icon:'\u2728',text:'\u041d\u043e\u0432\u0430 \u0432\u043f\u0440\u0430\u0432\u0430: '+e.name,color:'var(--accent2)'}));
    const topAchievements = achievements.slice(0,3);

    // ── Best growth indicator (hypertrophy score) ────────────────
    const bestGrowth = exComps.filter(e=>e.hyScore>0).sort((a,b)=>b.hyScore-a.hyScore)[0]||null;

    // ── Auto conclusion (hypertrophy-focused) ───────────────────
    const anyQualUp = qualDiff > 0;
    const anyRepUp = repGains.length > 0;
    const anyPR = prEx.length > 0;
    const volChange = Math.abs(tonPct)<2?'stable':tonPct>0?'up':'down';
    let conclusion = '';
    const muscleStr = muscleLabel ? ' \u043c\u0456\u0437 '+muscleLabel.toLowerCase() : '';
    if(anyRepUp&&anyQualUp&&volChange==='stable')
      conclusion='\u041a\u0440\u0430\u0449\u0438\u0439 \u0441\u0442\u0438\u043c\u0443\u043b \u0434\u043b\u044f \u0440\u043e\u0441\u0442\u0443'+muscleStr+'. \u0411\u0456\u043b\u044c\u0448\u0435 \u044f\u043a\u0456\u0441\u043d\u0438\u0445 \u043f\u043e\u0432\u0442\u043e\u0440\u0435\u043d\u044c \u043f\u0440\u0438 \u0442\u0456\u0439 \u0441\u0430\u043c\u0456\u0439 \u0432\u0430\u0437\u0456.';
    else if(anyRepUp&&volChange==='up')
      conclusion='\u0421\u0438\u043b\u044c\u043d\u0435 \u0442\u0440\u0435\u043d\u0443\u0432\u0430\u043d\u043d\u044f: \u0431\u0456\u043b\u044c\u0448\u0435 \u043f\u043e\u0432\u0442\u043e\u0440\u0435\u043d\u044c \u0456 \u0432\u0438\u0449\u0438\u0439 \u043e\u0431\u0454\u043c.';
    else if(anyRepUp)
      conclusion='\u041f\u0440\u043e\u0433\u0440\u0435\u0441 \u043f\u043e \u043f\u043e\u0432\u0442\u043e\u0440\u0435\u043d\u043d\u044f\u0445'+muscleStr+'. \u041c\u0456\u0437 \u043e\u0442\u0440\u0438\u043c\u0443\u0454 \u0431\u0456\u043b\u044c\u0448\u0435 \u0440\u043e\u0431\u043e\u0442\u0438.';
    else if(anyPR&&volChange==='stable')
      conclusion='\u041d\u043e\u0432\u0438\u0439 \u0440ó\u043a\u043e\u0440\u0434 \u0432\u0430\u0433\u0438. \u0421\u0442\u0435\u0436 \u0437\u0430 \u044f\u043a\u0456\u0441\u0442\u044e \u043f\u043e\u0432\u0442\u043e\u0440\u0435\u043d\u044c \u0432 \u043d\u0430\u0441\u0442\u0443\u043f\u043d\u043e\u043c\u0443 \u0442\u0440\u0435\u043d\u0443\u0432\u0430\u043d\u043d\u0456.';
    else if(anyQualUp)
      conclusion='\u042f\u043a\u0456\u0441\u043d\u0456\u0448\u0430 \u0440\u043e\u0431\u043e\u0442\u0430: \u0431\u0456\u043b\u044c\u0448\u0435 \u043f\u043e\u0432\u0442\u043e\u0440\u0435\u043d\u044c \u0443 \u0434\u0456\u0430\u043f\u0430\u0437\u043e\u043d\u0456 \u0433\u0456\u043f\u0435\u0440\u0442\u0440\u043e\u0444\u0456\u0457.';
    else if(exComps.some(e=>e.wDiff<0&&e.rDiff<0))
      conclusion='\u0412\u0430\u0440\u0442\u043e \u0434\u0430\u0442\u0438 \u0431\u0456\u043b\u044c\u0448\u0435 \u0447\u0430\u0441\u0443 \u043d\u0430 \u0432\u0456\u0434\u043f\u043e\u0447\u0438\u043d\u043e\u043a \u0430\u0431\u043e \u0437\u043c\u0435\u043d\u0448\u0438\u0442\u0438 \u0440\u043e\u0431\u043e\u0447\u0438\u0439 \u043e\u0431\u0454\u043c.';
    else
      conclusion='\u0421\u0442\u0430\u0431\u0456\u043b\u044c\u043d\u0430 \u0440\u043e\u0431\u043e\u0442\u0430. \u041f\u0456\u0434\u0442\u0440\u0438\u043c\u0443\u0439 \u0440\u0438\u0442\u043c \u0456 \u043f\u0440\u043e\u0433\u0440\u0435\u0441\u0443\u0439 \u0432 \u043f\u043e\u0432\u0442\u043e\u0440\u0435\u043d\u043d\u044f\u0445.';
    if(bestGrowth&&bestGrowth.rDiff>0)
      conclusion+=' \u041d\u0430\u0439\u0431\u0456\u043b\u044c\u0448\u0438\u0439 \u0440\u0456\u0441\u0442: '+bestGrowth.name+' (+'+bestGrowth.rDiff+' \u043f\u043e\u0432\u0442).';
    else if(bestGrowth&&bestGrowth.wDiff>0)
      conclusion+=' \u0420\u0435\u043a\u043e\u0440\u0434: '+bestGrowth.name+' ('+bestGrowth.maxWB+'\u043a\u0433).';

    // ── Recovery & Performance ───────────────────────────────────
    let recoveryMsg = '', recoveryColor = 'var(--text2)', recoveryIcon = '\u2764\ufe0f';
    const volumeDown = tonB < tonA * 0.95;
    const setsDown = setsB < setsA;
    if((anyRepUp||anyQualUp)&&(volumeDown||setsDown)){
      recoveryMsg='\u041f\u0440\u043e\u0433\u0440\u0435\u0441 \u043d\u0435\u0437\u0432\u0430\u0436\u0430\u044e\u0447\u0438 \u043d\u0430 \u0432\u0442\u043e\u043c\u0443. \u0421\u0435 \u043e\u0437\u043d\u0430\u043a\u0430 \u0430\u0434\u0430\u043f\u0442\u0430\u0446\u0456\u0457.';
      recoveryColor='var(--green2)'; recoveryIcon='\ud83d\udcaa';
    } else if(anyRepUp&&volChange==='up'){
      recoveryMsg='\u0412\u0456\u0434\u043c\u0456\u043d\u043d\u0435 \u0432\u0456\u0434\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u044f. \u041f\u043e\u0432\u043d\u0430 \u043f\u0440\u043e\u0434\u0443\u043a\u0442³\u0432\u043d\u0456\u0441\u0442\u044c.';
      recoveryColor='var(--green2)'; recoveryIcon='\u26a1';
    } else if(volChange==='down'&&!anyRepUp&&!anyPR){
      recoveryMsg='\u0421\u0445\u043e\u0436\u0430 \u043f\u0440\u043e\u0434\u0443\u043a\u0442\u0438\u0432\u043d\u0456\u0441\u0442\u044c \u043f\u0440\u0438 \u043d\u0438\u0436\u0447\u043e\u043c\u0443 \u043e\u0431\u0454\u043c\u0456. \u041c\u043e\u0436\u043b\u0438\u0432\u0435, \u043d\u0435\u0434\u043e\u0441\u0442\u0430\u0442\u043d\u044c\u043e \u0432\u0456\u0434\u043f\u043e\u0447\u0438\u043dк\u0443.';
      recoveryColor='var(--orange)'; recoveryIcon='\ud83d\ude34';
    } else {
      recoveryMsg='\u0421\u0442\u0430\u0431\u0456\u043b\u044c\u043d\u0435 \u0432\u0456\u0434\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u044f \u0456 \u0435\u043d\u0435\u0440\u0433\u0456\u044f.';
      recoveryColor='var(--text2)'; recoveryIcon='\u2714\ufe0f';
    }

    // ── Cycle history helper ─────────────────────────────────────
    const allSortedKeys = Object.keys(data).sort();
    function getCycleHistory(exName){
      const hist=[];
      allSortedKeys.forEach(k=>{
        const w=data[k]; if(!w||!w.exercises) return;
        const ex=w.exercises.find(e=>e.name&&e.name.toLowerCase().trim()===exName.toLowerCase().trim());
        if(!ex||!ex.sets.length) return;
        const maxW=Math.max(...ex.sets.map(s=>Number(s.weight)||0));
        const maxR=Math.max(...ex.sets.map(s=>Number(s.reps)||0));
        const qr=ex.sets.reduce((a,s)=>{const r=Number(s.reps)||0,w=Number(s.weight)||0;return a+(r>=6&&r<=20&&w>0?r:0);},0);
        hist.push({key:k,maxW,maxR,qr});
      });
      return hist.slice(-5);
    }

    const TAG_CONFIG = {
      pr:       {label:'New PR',      bg:'rgba(245,158,11,.15)',  color:'#f59e0b',        border:'rgba(245,158,11,.3)'},
      more_reps:{label:'+Rep PR',     bg:'rgba(16,185,129,.12)',  color:'var(--green2)',  border:'rgba(16,185,129,.25)'},
      volume:   {label:'More volume', bg:'rgba(16,185,129,.08)',  color:'var(--green2)',  border:'rgba(16,185,129,.15)'},
      stable:   {label:'Stable',      bg:'rgba(255,255,255,.05)', color:'var(--text3)',   border:'var(--border)'},
      new:      {label:'New',         bg:'rgba(124,58,237,.12)',  color:'var(--accent2)', border:'rgba(124,58,237,.25)'},
    };

    return React.createElement('div',{className:'cc-overlay',onClick:()=>setCompareModal(null)},
      React.createElement('div',{className:'cc-modal',onClick:e=>e.stopPropagation(),
        style:{maxHeight:'92vh',overflow:'auto',padding:'0',borderRadius:'24px',display:'flex',flexDirection:'column'}},

        // ── Sticky header ──
        React.createElement('div',{style:{
          position:'sticky',top:0,zIndex:10,background:'var(--bg2)',
          borderBottom:'1px solid var(--border)',padding:'16px 20px 12px',
          display:'flex',alignItems:'center',justifyContent:'space-between',borderRadius:'24px 24px 0 0'
        }},
          React.createElement('div',null,
            React.createElement('div',{style:{fontSize:'11px',color:'var(--text3)',marginBottom:'2px'}},'\u041f\u043e\u0440\u0456\u0432\u043d\u044f\u043d\u043d\u044f'),
            React.createElement('div',{style:{fontSize:'16px',fontWeight:800,color:'var(--text1)'}},
              fmtShort(keyA),
              React.createElement('span',{style:{color:'var(--text3)',margin:'0 8px'}},'\u2192'),
              fmtShort(keyB)
            )
          ),
          React.createElement('button',{className:'cc-btn',onClick:()=>setCompareModal(null)},React.createElement(XIcon))
        ),

        React.createElement('div',{style:{padding:'18px 16px',display:'flex',flexDirection:'column',gap:'14px'}},

          // ── 1. Hero achievements ──
          topAchievements.length>0 && React.createElement('div',{style:{
            background:'linear-gradient(135deg,rgba(16,185,129,.1),rgba(124,58,237,.06))',
            border:'1px solid rgba(16,185,129,.2)',borderRadius:'18px',padding:'16px'
          }},
            React.createElement('div',{style:{fontSize:'10px',fontWeight:800,color:'var(--green2)',textTransform:'uppercase',letterSpacing:'.08em',marginBottom:'12px'}},'\u041f\u0440\u043e\u0433\u0440\u0435\u0441 \u043f\u043e \u0433\u0456\u043f\u0435\u0440\u0442\u0440\u043e\u0444\u0456\u0457'),
            topAchievements.map((a,i)=>React.createElement('div',{key:i,style:{
              display:'flex',alignItems:'center',gap:'10px',marginBottom:i<topAchievements.length-1?'10px':0
            }},
              React.createElement('span',{style:{fontSize:'20px',lineHeight:1}},a.icon),
              React.createElement('span',{style:{fontSize:'14px',fontWeight:700,color:a.color}},a.text)
            ))
          ),

          // ── 2. Auto conclusion ──
          React.createElement('div',{style:{
            background:'var(--bg3)',border:'1px solid var(--border)',borderRadius:'14px',
            padding:'14px 16px',fontSize:'14px',fontWeight:600,color:'var(--text1)',lineHeight:1.6
          }},conclusion),

          // ── 3. Best Growth Indicator ──
          bestGrowth && React.createElement('div',{style:{
            background:'linear-gradient(135deg,rgba(16,185,129,.08),rgba(16,185,129,.03))',
            border:'1px solid rgba(16,185,129,.2)',borderRadius:'16px',padding:'14px 16px'
          }},
            React.createElement('div',{style:{fontSize:'10px',fontWeight:800,color:'var(--green2)',textTransform:'uppercase',letterSpacing:'.07em',marginBottom:'8px'}},'\ud83c\udf31 \u041d\u0430\u0439\u043a\u0440\u0430\u0449\u0438\u0439 \u0441\u0438\u0433\u043d\u0430\u043b \u0440\u043e\u0441\u0442\u0443'),
            React.createElement('div',{style:{fontSize:'16px',fontWeight:800,color:'var(--text1)',marginBottom:'8px'}},bestGrowth.name),
            React.createElement('div',{style:{display:'flex',flexDirection:'column',gap:'3px'}},
              bestGrowth.rDiff>0 && React.createElement('div',{style:{fontSize:'13px',color:'var(--green2)',fontWeight:600}},
                '\u2191 +'+bestGrowth.rDiff+' \u043f\u043e\u0432\u0442. \u043f\u0440\u0438 '+(bestGrowth.wDiff===0?'\u0442\u0456\u0439 \u0441\u0430\u043c\u0456\u0439 \u0432\u0430\u0437\u0456':'\u043d\u043e\u0432\u0456\u0439 \u0432\u0430\u0437\u0456')),
              bestGrowth.qDiff>0 && React.createElement('div',{style:{fontSize:'13px',color:'var(--green2)',fontWeight:600}},
                '\u2191 +'+bestGrowth.qDiff+' \u044f\u043a\u0456\u0441\u043d\u0438\u0445 \u043f\u043e\u0432\u0442\u043e\u0440\u0435\u043d\u044c'),
              bestGrowth.vDiff>0 && React.createElement('div',{style:{fontSize:'12px',color:'var(--text2)'}},
                '\u2191 +'+bestGrowth.vDiff+'\u043a\u0433 \u0435\u0444\u0435\u043a\u0442\u0438\u0432\u043d\u043e\u0433\u043e \u043e\u0431\u0454\u043c\u0443'),
              bestGrowth.wDiff>0 && React.createElement('div',{style:{fontSize:'12px',color:'#f59e0b'}},
                '\u2191 \u0412\u0430\u0433\u0430 '+bestGrowth.maxWA+'\u2192'+bestGrowth.maxWB+'\u043a\u0433')
            )
          ),

          // ── 4. Recovery & Performance ──
          React.createElement('div',{style:{
            background:'var(--bg3)',border:'1px solid var(--border)',borderRadius:'14px',padding:'12px 14px',
            display:'flex',alignItems:'flex-start',gap:'10px'
          }},
            React.createElement('span',{style:{fontSize:'20px',lineHeight:1,flexShrink:0}},recoveryIcon),
            React.createElement('div',null,
              React.createElement('div',{style:{fontSize:'10px',fontWeight:800,color:'var(--text3)',textTransform:'uppercase',letterSpacing:'.07em',marginBottom:'4px'}},'\u0412\u0456\u0434\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u044f \u0456 \u043f\u0440\u043e\u0434\u0443\u043a\u0442\u0438\u0432\u043d\u0456\u0441\u0442\u044c'),
              React.createElement('div',{style:{fontSize:'13px',fontWeight:600,color:recoveryColor,lineHeight:1.5}},recoveryMsg)
            )
          ),

          // ── 5. Exercise cards ──
          exComps.length>0 && React.createElement('div',null,
            React.createElement('div',{style:{fontSize:'10px',fontWeight:800,color:'var(--text3)',textTransform:'uppercase',letterSpacing:'.08em',marginBottom:'10px'}},'\u0412\u043f\u0440\u0430\u0432\u0438'),
            exComps.map((ex,i)=>{
              const tag=TAG_CONFIG[ex.tag]||TAG_CONFIG.stable;
              const cycleHist=getCycleHistory(ex.name);
              return React.createElement('div',{key:i,style:{
                background:'var(--bg3)',border:'1px solid var(--border)',borderRadius:'16px',padding:'14px',marginBottom:'10px'
              }},
                React.createElement('div',{style:{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:'10px'}},
                  React.createElement('div',{style:{fontWeight:700,fontSize:'14px',color:'var(--text1)',flex:1,marginRight:'8px'}},ex.name),
                  React.createElement('div',{style:{
                    fontSize:'10px',fontWeight:700,padding:'3px 8px',borderRadius:'20px',
                    background:tag.bg,color:tag.color,border:'1px solid '+tag.border,whiteSpace:'nowrap'
                  }},tag.label)
                ),
                React.createElement('div',{style:{display:'flex',flexDirection:'column',gap:'5px'}},
                  // Weight — show if changed OR always for new
                  ex.maxWA===null
                    ? React.createElement('div',{style:{display:'flex',justifyContent:'space-between'}},
                        React.createElement('span',{style:{fontSize:'12px',color:'var(--text3)'}},'\u0412\u0430\u0433\u0430'),
                        React.createElement('span',{style:{fontSize:'13px',fontWeight:700,color:'var(--accent2)'}},ex.maxWB+' \u043a\u0433'))
                    : React.createElement('div',{style:{display:'flex',justifyContent:'space-between'}},
                        React.createElement('span',{style:{fontSize:'12px',color:'var(--text3)'}},'Max \u0432\u0430\u0433\u0430'),
                        ex.wDiff!==0
                          ? React.createElement('span',{style:{fontSize:'13px',fontWeight:700,color:ex.wDiff>0?'#f59e0b':'var(--text2)'}},ex.maxWA+' \u2192 '+ex.maxWB+' \u043a\u0433'+(ex.wDiff>0?' \ud83c\udfc6':''))
                          : React.createElement('span',{style:{fontSize:'13px',color:'var(--text2)'}},ex.maxWB+' \u043a\u0433')
                      ),
                  // Reps — only if changed
                  ex.maxRA!==null && ex.rDiff!==0 && React.createElement('div',{style:{display:'flex',justifyContent:'space-between'}},
                    React.createElement('span',{style:{fontSize:'12px',color:'var(--text3)'}},'Max \u043f\u043e\u0432\u0442.'),
                    React.createElement('span',{style:{fontSize:'13px',fontWeight:700,color:ex.rDiff>0?'var(--green2)':'var(--red)'}},
                      ex.maxRA+' \u2192 '+ex.maxRB+(ex.rDiff>0?' (+'+ex.rDiff+')':' ('+ex.rDiff+')')
                    )
                  ),
                  // Quality reps — if changed
                  ex.qualExA!==null && ex.qDiff!==0 && React.createElement('div',{style:{display:'flex',justifyContent:'space-between'}},
                    React.createElement('span',{style:{fontSize:'12px',color:'var(--text3)'}},'\u042f\u043a\u0456\u0441\u043d\u0456 \u043f\u043e\u0432\u0442. (6\u201320)'),
                    React.createElement('span',{style:{fontSize:'13px',fontWeight:700,color:ex.qDiff>0?'var(--green2)':'var(--text3)'}},
                      ex.qualExA+' \u2192 '+ex.qualExB+(ex.qDiff>0?' (+'+ex.qDiff+')':' ('+ex.qDiff+')')
                    )
                  ),
                  // Volume — only if changed >2%
                  ex.vDiff!==null && Math.abs(ex.vDiff/(ex.tonExA||1))>=0.02 && React.createElement('div',{style:{display:'flex',justifyContent:'space-between'}},
                    React.createElement('span',{style:{fontSize:'12px',color:'var(--text3)'}},'\u0415\u0444. \u043e\u0431\u0454\u043c'),
                    React.createElement('span',{style:{fontSize:'13px',fontWeight:600,color:ex.vDiff>0?'var(--green2)':'var(--text3)'}},
                      (ex.tonExA>1000?(ex.tonExA/1000).toFixed(1)+'\u0442':ex.tonExA+'\u043a\u0433')+
                      ' \u2192 '+(ex.tonExB>1000?(ex.tonExB/1000).toFixed(1)+'\u0442':ex.tonExB+'\u043a\u0433')+
                      (ex.vDiff>0?' (+'+ex.vDiff+')':' ('+ex.vDiff+')')
                    )
                  ),
                  ex.tag==='stable'&&ex.maxWA!==null && React.createElement('div',{style:{fontSize:'12px',color:'var(--text3)'}},'\u2248 \u0411\u0435\u0437 \u0437\u043c\u0456\u043d')
                ),
                // Cycle trend
                cycleHist.length>=2 && React.createElement('div',{style:{marginTop:'10px',paddingTop:'10px',borderTop:'1px solid var(--border)'}},
                  React.createElement('div',{style:{fontSize:'9px',color:'var(--text3)',marginBottom:'6px',fontWeight:700,textTransform:'uppercase',letterSpacing:'.05em'}},'\u0422\u0440\u0435\u043d\u0434'),
                  React.createElement('div',{style:{display:'flex',gap:'6px',overflowX:'auto'}},
                    cycleHist.map((h,j)=>{
                      const isCur=h.key===keyB;
                      return React.createElement('div',{key:j,style:{display:'flex',flexDirection:'column',alignItems:'center',gap:'2px',flexShrink:0}},
                        React.createElement('div',{style:{
                          fontSize:'10px',fontWeight:700,
                          color:isCur?'var(--accent2)':'var(--text2)',
                          background:isCur?'rgba(124,58,237,.15)':'var(--bg4)',
                          padding:'3px 6px',borderRadius:'7px',
                          border:isCur?'1px solid var(--accent-dark)':'1px solid var(--border)',
                          whiteSpace:'nowrap'
                        }},h.maxW+'\xd7'+h.maxR),
                        h.qr>0&&React.createElement('div',{style:{fontSize:'8px',color:'var(--green2)',fontWeight:600}},h.qr+'q'),
                        React.createElement('div',{style:{fontSize:'8px',color:'var(--text3)'}},fmtShort(h.key))
                      );
                    })
                  )
                )
              );
            })
          ),

          // ── 6. Overall stats (last, compact) ──
          React.createElement('div',{style:{background:'var(--bg3)',border:'1px solid var(--border)',borderRadius:'14px',padding:'12px 14px'}},
            React.createElement('div',{style:{fontSize:'10px',fontWeight:800,color:'var(--text3)',textTransform:'uppercase',letterSpacing:'.08em',marginBottom:'10px'}},'\u041e\u0441\u043d\u043e\u0432\u043d\u0430 \u0441\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430'),
            React.createElement('div',{style:{display:'flex',justifyContent:'space-between'}},
              [['\u041e\u0431\u0454\u043c',tonA>1000?(tonA/1000).toFixed(1)+'\u0442':tonA+'\u043a\u0433',tonB>1000?(tonB/1000).toFixed(1)+'\u0442':tonB+'\u043a\u0433',tonPct],
               ['\u042f\u043a. \u043f\u043e\u0432\u0442',qualA,qualB,qualA>0?Math.round(qualDiff/qualA*100):0],
               ['\u041f\u0456\u0434\u0445\u043e\u0434\u0438',setsA,setsB,setsA>0?Math.round((setsB-setsA)/setsA*100):0]].map(([lbl,vA,vB,pct],i)=>{
                const isStable=Math.abs(pct)<2;
                return React.createElement('div',{key:i,style:{textAlign:'center',flex:1}},
                  React.createElement('div',{style:{fontSize:'10px',color:'var(--text3)',marginBottom:'3px',fontWeight:600}},lbl),
                  isStable
                    ? React.createElement('div',{style:{fontSize:'13px',fontWeight:700,color:'var(--text2)'}},String(vB))
                    : React.createElement('div',null,
                        React.createElement('div',{style:{fontSize:'10px',color:'var(--text3)'}},String(vA)),
                        React.createElement('div',{style:{fontSize:'13px',fontWeight:800,color:pct>0?'var(--green2)':pct<-5?'var(--red)':'var(--text1)'}},String(vB))
                      )
                );
              })
            )
          )
        )
      )
    );
  }

  function renderHistory(){
    if(historyDetail) return renderHistoryDetail();
    
    let filterText = 'За весь час';
    if(filterStart === 'last') filterText = 'Last';
    else if(filterStart === 'all') filterText = 'За весь час';
    else if(filterStart && filterEnd) {
      if(filterStart === filterEnd) filterText = fmtShort(filterStart);
      else filterText = fmtShort(filterStart) + ' - ' + fmtShort(filterEnd);
    } else if(filterStart) filterText = 'З ' + fmtShort(filterStart);
    else if(filterEnd) filterText = 'До ' + fmtShort(filterEnd);

    // Calculate max muscle tonnage for progress bars
    const maxMuscleTonnage = muscleStats.length > 0 ? Math.max(...muscleStats.map(s => s[1].tonnage)) : 1;

    return React.createElement(React.Fragment,null,
      React.createElement('div',{className:'history-header'},
        React.createElement('h2',{style:{display:'flex',alignItems:'center',gap:'8px'}},React.createElement('div',{style:{display:'flex',alignItems:'center',marginTop:'-2px'}},React.createElement(HistoryIcon)),'Щоденник'),
        React.createElement('button', {
          className: 'date-trigger-btn',
          style: {padding: '8px 16px', fontSize: '13px'},
          onClick: () => {
            setPickerStart(actualStart); setPickerEnd(actualEnd);
            setPickerYear(actualStart ? parseInt(actualStart.split('-')[0]) : new Date().getFullYear());
            setPickerMonth(actualStart ? parseInt(actualStart.split('-')[1])-1 : new Date().getMonth());
            setShowPicker(true);
          }
        }, React.createElement(CalendarIcon, {size: 14, style:{marginTop:'-1px'}}), filterText + ' ▾')
      ),
      
      // Dashboard Card
      React.createElement('div',{className:'tonnage-card'},
        React.createElement('div',{className:'tonnage-value'},(totalTonnage/1000).toFixed(1)+'т'),
        React.createElement('div',{className:'tonnage-label'},'Загальний об\'єм'),
        React.createElement('div',{className:'tonnage-row'},
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},totalDays),React.createElement('div',{className:'tonnage-item-lbl'},'ТРЕНУВАНЬ')),
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},totalSets),React.createElement('div',{className:'tonnage-item-lbl'},'ПІДХОДІВ')),
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},thisWeek),React.createElement('div',{className:'tonnage-item-lbl'},'ЦЕЙ ТИЖД.'))
        )
      ),
      
      history.length===0
        ?React.createElement('div',{className:'empty-state'},React.createElement('div',{className:'e-icon'},React.createElement(BookIcon)),React.createElement('h3',null,'Поки пусто'),React.createElement('p',null,'Записуй тренування в календарі'))
        :React.createElement(React.Fragment,null,
          
          // Muscle Activity Bars
          muscleStats.length>0&&React.createElement(React.Fragment,null,
            React.createElement('div',{className:'section-label'},'Активність'),
            React.createElement('div',{className:'muscle-tonnage-list'},
              muscleStats.map(([key,stat])=>{
                const t = stat.tonnage;
                const pct = Math.max(5, Math.round((t / maxMuscleTonnage) * 100)); // min 5% for visibility
                return React.createElement('div',{key:key,className:'mt-row'},
                  React.createElement('div',{className:'mt-bar-container'},
                    React.createElement('div',{className:'mt-bar-header'},
                      React.createElement('span',{className:'mt-name'},stat.label),
                      React.createElement('span',{className:'mt-tonnage'},t>1000?(t/1000).toFixed(1)+' т':t+' кг')
                    ),
                    React.createElement('div',{className:'mt-bar-bg'},
                      React.createElement('div',{className:'mt-bar-fill', style:{width: pct + '%'}})
                    )
                  )
                );
              })
            )
          ),
          
          // Workout Feed
          React.createElement('div',{className:'section-label'},'Тренування ('+history.length+')'),
          React.createElement('div',{className:'history-list'},history.map(([k,w])=>{
            const ton = calcTonnage(w);
            const validExercises = w.exercises.filter(ex=>ex.sets.length>0);
            const totalEx = validExercises.length;
            const totalSets = validExercises.reduce((a,e)=>a+e.sets.length,0);
            return React.createElement('div',{key:k,className:'history-card',onClick:()=>setHistoryDetail(k)},
              React.createElement('div',{className:'hc-top'},
                React.createElement('div',null,
                  React.createElement('div',{className:'hc-title'},k===tKey?'Сьогодні':fmtFull(k)),
                  React.createElement('div',{className:'hc-date'},k)
                ),
                w.muscle&&React.createElement('span',{className:'hc-muscle'},w.muscle)
              ),
              React.createElement('div',{className:'hc-stats'},
                React.createElement('span',{className:'hc-stat'}, React.createElement(ActivityIcon, {size:12, className:'hc-stat-icon'}), React.createElement('strong',null,totalEx),'вправ'),
                React.createElement('span',{className:'hc-stat'}, React.createElement(RefreshIcon, {size:12, className:'hc-stat-icon'}), React.createElement('strong',null,totalSets),'підх.'),
                React.createElement('span',{className:'hc-stat'}, React.createElement(WeightIcon, {size:12, className:'hc-stat-icon'}), React.createElement('strong',null,ton>1000?(ton/1000).toFixed(1)+'т':ton+'кг'))
              ),
              React.createElement('div',{className:'hc-exercises'},validExercises.map((ex,i)=>{
                const et = calcExTonnage(ex);
                const mg = MUSCLES.find(e=>e.id===(ex.muscle||''));
                return React.createElement('div',{key:i,className:'hc-ex'},
                  React.createElement('div',{className:'hc-ex-left'},
                    ex.name + (ex.sets[0]&&ex.sets[0].bw?' (СВ)':'')
                  ),
                  React.createElement('div',{className:'hc-ex-right'},
                    `${ex.sets.length} х ${et>1000?(et/1000).toFixed(1)+'т':et+'кг'}`
                  )
                );
              }))
            );
          }))
        )
    );
  }

  function renderAnalytics() {
    const weightHistory = settings.weightHistory || {};
    const allWeightKeys = Object.keys(weightHistory).sort();
    const totalWPages = Math.ceil(allWeightKeys.length / 10);
    const remainder = allWeightKeys.length % 10 || 10;
    let wEnd, wStart;
    if (weightPage === 0) {
      wEnd = allWeightKeys.length;
      wStart = Math.max(0, allWeightKeys.length - remainder);
    } else {
      wEnd = allWeightKeys.length - remainder - (weightPage - 1) * 10;
      wStart = Math.max(0, wEnd - 10);
    }
    const weightKeys = allWeightKeys.slice(wStart, wEnd);
    const weightChartData = weightKeys.map(k => ({ date: k, weight: weightHistory[k] }));
    const wMin = weightChartData.length > 0 ? Math.min(...weightChartData.map(d => d.weight)) : 0;
    const wMax = weightChartData.length > 0 ? Math.max(...weightChartData.map(d => d.weight)) : 0;
    const wRange = (wMax - wMin) || 1;
    const wBase = Math.max(0, wMin - (wRange * 0.4));

    const svgW = 1000;
    const svgH = 160; 
    const padX = 50;
    const padY = 30; 
    const chartW = svgW - padX * 2;
    const chartH = svgH - padY * 2;

    const getX = (i) => padX + (i / (weightChartData.length - 1 || 1)) * chartW;
    const getY = (w) => svgH - padY - ((w - wBase) / (wMax - wBase + wRange * 0.1 || 1)) * chartH;

    let lineD = '';
    let areaD = '';
    if (weightChartData.length > 0) {
      weightChartData.forEach((d, i) => {
        const x = getX(i);
        const y = getY(d.weight);
        if (i === 0) {
          lineD = `M ${x} ${y}`;
          areaD = `M ${x} ${svgH - padY} L ${x} ${y}`;
        } else {
          const prevX = getX(i - 1);
          const prevY = getY(weightChartData[i - 1].weight);
          const cpX1 = prevX + (x - prevX) / 2;
          const cpX2 = prevX + (x - prevX) / 2;
          lineD += ` C ${cpX1} ${prevY}, ${cpX2} ${y}, ${x} ${y}`;
          areaD += ` C ${cpX1} ${prevY}, ${cpX2} ${y}, ${x} ${y}`;
        }
      });
      if (weightChartData.length > 0) areaD += ` L ${getX(weightChartData.length - 1)} ${svgH - padY} Z`;
    }

    return React.createElement('div', {className: 'analytics-container'},
      React.createElement('h2', {style:{display:'flex',alignItems:'center',gap:'8px',marginBottom:'16px'}}, React.createElement(TrendingUpIcon), 'Аналітика'),
      
      React.createElement('div', {className: 'chart-wrapper'},
        // Weight header + inputs
        React.createElement('div', {style:{display:'flex', flexDirection:'column', gap:'16px', marginBottom:'24px'}},
          React.createElement('span', {style:{fontSize:'15px', fontWeight:'800', letterSpacing:'-0.3px', display:'flex', justifyContent:'space-between', alignItems:'center'}}, 
            'Динаміка власної ваги (кг)',
            React.createElement('button', {
              style:{background:'none', border:'none', padding:'6px', cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center'},
              onClick:()=>setConfirmAction({
                title: 'Видалити всю історію ваги?',
                onConfirm: () => { setSettings(s=>({...s, weightHistory:{}})); setWeightPage(0); flash('Історію очищено'); }
              })
            }, React.createElement(TrashIcon, {size: 18, style:{color:'#ffffff'}}))
          ),
          React.createElement('div', {className: 'pixel-row'},
            React.createElement('button', {style:{flex: 1}, onClick:()=>setShowBwPicker(true)}, React.createElement(CalendarIcon, {size: 14, style:{marginRight:'8px'}}), fmtShort(bwDate)),
            React.createElement('div', {className: 'input-wrap'},
              React.createElement('input', {type:'number', step:'0.1', placeholder:'75.5', value:bwValue, onChange:e=>setBwValue(e.target.value)}),
              React.createElement('span', {className: 'suffix'}, 'кг')
            ),
            React.createElement('button', {className: 'primary', style:{flex: 1}, onClick:()=>{
              let val = Number(bwValue);
              if(bwDate && val > 0) {
                setSettings(s => {
                  const newS = {...s, weightHistory: {...(s.weightHistory||{}), [bwDate]: val}, lastUpdated: Date.now()};
                  persist(SETTINGS_KEY, newS);
                  return newS;
                }); 
                setWeightPage(0);
                setBwValue('');
                flash('Вагу збережено');
              }
            }}, 'Додати')
          )
        ),

        // Weight Chart
        weightChartData.length > 0 ? React.createElement('div', {style:{position:'relative', margin:'0 -10px'}},
          // Nav buttons
          allWeightKeys.length > 10 && React.createElement(React.Fragment, null,
            React.createElement('button', {className:'chart-nav-btn left', disabled: weightPage >= totalWPages-1, onClick:()=>setWeightPage(p=>Math.min(p+1, totalWPages-1))}, React.createElement(ArrowLeftIcon, {size:18})),
            React.createElement('button', {className:'chart-nav-btn right', disabled: weightPage === 0, onClick:()=>setWeightPage(p=>Math.max(0, p-1))}, React.createElement(ArrowRightIcon, {size:18}))
          ),
          React.createElement('div', {className: 'chart-container'},
            React.createElement('svg', {viewBox: `0 0 ${svgW} ${svgH}`, style: {width: '100%', height: '100%', overflow: 'visible'}},
              React.createElement('path', {d: areaD, fill: '#34d399', fillOpacity: 0.15}),
              React.createElement('path', {d: lineD, fill: 'none', stroke: '#34d399', strokeWidth: 3, strokeLinecap: 'round', strokeLinejoin: 'round'}),
              weightChartData.map((d, i) => {
                const x = getX(i);
                const y = getY(d.weight);
                return React.createElement('g', {
                  key: i, 
                  onClick: () => { setEditItem({type:'weight', date:d.date, val:d.weight}); setEditVal(d.weight); },
                  style: {cursor:'pointer'}
                },
                  React.createElement('circle', {cx: x, cy: y, r: 8, fill: '#34d399'}),
                  React.createElement('text', {x: x, y: y - 28, fill: '#34d399', fontSize: '36px', fontWeight: '800', textAnchor: 'middle'}, d.weight % 1 === 0 ? d.weight : d.weight.toFixed(1))
                );
              })
            )
          ),
          React.createElement('div', {style:{display:'flex', justifyContent:'space-between', padding:'0 5px', marginTop:'0', marginBottom:'16px'}},
            weightChartData.map((d, i) => React.createElement('div', {key: i, style:{fontSize:'10px', color:'var(--text3)', fontWeight:'600', textAlign:'center', flex:1, lineHeight:'1.1'}}, fmtShort(d.date).split(' ').map((s, idx)=>React.createElement('div', {key:idx}, s))))
          )
        ) : React.createElement('div', {style:{textAlign:'center',color:'var(--text3)', padding:'40px 0'}}, 'Додайте свою вагу'),

        React.createElement('div', {style:{height:'1px', background:'var(--border)', margin:'20px 0' }}),

        // Body measurements section
        React.createElement('div', {style:{display:'flex', flexDirection:'column', gap:'12px'}},
          React.createElement('span', {style:{fontSize:'15px', fontWeight:'800', letterSpacing:'-0.3px', display:'flex', alignItems:'center', gap:'8px'}}, 
            React.createElement('span', {style:{fontSize:'18px'}}, '📏'), 'Заміри тіла (см)'
          ),
          // Top Row: Date & Muscle Selector
          React.createElement('div', {className: 'pixel-row'},
            React.createElement('button', {style:{flex: '1'}, onClick:()=>setShowMeasPicker(true)}, React.createElement(CalendarIcon, {size: 14, style:{marginRight:'8px'}}), fmtShort(measDate)),
            React.createElement('button', {style:{flex: '2', justifyContent:'space-between', padding:'0 16px'}, onClick:()=>setShowMuscleModal(true)}, 
              measMuscleName || 'Виберіть м\'яз', React.createElement('span', {style:{fontSize:'10px', opacity:0.6}}, '▼')
            )
          ),
          // Bottom Row: Value & Add Button
          React.createElement('div', {className: 'pixel-row'},
            React.createElement('div', {className: 'input-wrap', style:{flex: '1'}},
              React.createElement('input', {type:'number', step:'0.1', placeholder:'78.5', value:measValue, onChange:e=>setMeasValue(e.target.value)}),
              React.createElement('span', {className: 'suffix'}, 'см')
            ),
            React.createElement('button', {className: 'primary', style:{flex: '1'}, onClick:()=>{
              let val = Number(measValue);
              if(measDate && val > 0 && measMuscleName) {
                setSettings(s => {
                  const current = Array.isArray(s.measHistory) ? s.measHistory : [];
                  const newS = {...s, measHistory: [{date: measDate, val, name: measMuscleName}, ...current].slice(0, 50), lastUpdated: Date.now()};
                  persist(SETTINGS_KEY, newS);
                  return newS;
                });
                setMeasValue('');
                flash('Замір збережено');
              }
            }}, 'Додати')
          ),

          // Measurement History List
          (Array.isArray(settings.measHistory) && settings.measHistory.length > 0) && React.createElement('div', {style:{marginTop:'12px', display:'flex', flexDirection:'column', gap:'8px'}},
            settings.measHistory.slice(0, 10).map((item, idx) => {
              const mInfo = MUSCLE_MEASUREMENTS.find(m => m.label === item.name);
              return React.createElement('div', {
                key: idx, 
                onClick:()=>{ setEditItem({type:'meas', date:item.date, val:item.val, name:item.name, originalIndex:idx}); setEditVal(item.val); },
                style:{display:'flex', alignItems:'center', justifyContent:'space-between', padding:'10px 16px', background:'var(--bg2)', borderRadius:'14px', border:'1px solid var(--border)', cursor:'pointer'}
              },
                React.createElement('div', {style:{display:'flex', alignItems:'center', gap:'12px'}},
                  (mInfo && MuscleIcons[mInfo.icon]) ? MuscleIcons[mInfo.icon](32) : null,
                  React.createElement('div', {style:{display:'flex', flexDirection:'column'}},
                    React.createElement('span', {style:{fontSize:'14px', fontWeight:'700'}}, item.name),
                    React.createElement('span', {style:{fontSize:'11px', color:'var(--text3)'}}, fmtShort(item.date))
                  )
                ),
                React.createElement('div', {style:{display:'flex', alignItems:'center', gap:'12px'}},
                  React.createElement('span', {style:{fontSize:'16px', fontWeight:'800', color:'#34d399'}}, `${item.val}`),
                  React.createElement('button', {
                    style:{background:'none', border:'none', padding:'8px', cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center'},
                    onClick:(e)=>{
                      e.stopPropagation();
                      setEditItem({type:'meas', date:item.date, val:item.val, name:item.name, originalIndex:idx});
                    }
                  }, React.createElement(TrashIcon, {size: 18, style:{color:'var(--text3)', opacity:0.6}}))
                )
              );
            })
          )
        )
      )
    );
  }




  function renderSettings(){
    return React.createElement(React.Fragment,null,
      React.createElement('div',{className:'settings-section'},
        React.createElement('h2',{style:{display:'flex',alignItems:'center',gap:'8px'}},React.createElement('div',{style:{display:'flex',alignItems:'center',marginTop:'-2px'}},React.createElement(SettingsIcon)),'Налаштування'),
        React.createElement('div',{className:'settings-card'},
          React.createElement('h3',null,'👤 Ваше ім\'я'),
          React.createElement('p',null,'Вкажи своє ім\'я для відображення в системі'),
          React.createElement('input',{className:'settings-input',type:'text',placeholder:'Наприклад: Іван',value:settings.userName||'',
            onChange:e=>setSettings(s=>({...s,userName:e.target.value})),
            onBlur:()=>flash('Ім\'я збережено')})
        ),
        // info
        React.createElement('div',{className:'settings-card'},
          React.createElement('h3',null,'Інтерфейс'),
          React.createElement('label',{style:{display:'flex',alignItems:'center',gap:'8px',cursor:'pointer',marginBottom:'12px'}},
            React.createElement('input',{type:'checkbox',checked:settings.showBwToggle!==false,onChange:e=>setSettings(s=>({...s,showBwToggle:e.target.checked}))}),
            React.createElement('span',{style:{fontSize:'14px',color:'var(--text2)'}},'Кнопка «Вправа зі своєю вагою»')
          ),
          React.createElement('label',{style:{display:'flex',alignItems:'center',gap:'8px',cursor:'pointer',marginBottom:'4px'}},
            React.createElement('input',{type:'checkbox',checked:settings.showPrevPlaceholder!==false,onChange:e=>setSettings(s=>({...s,showPrevPlaceholder:e.target.checked}))}),
            React.createElement('span',{style:{fontSize:'14px',color:'var(--text2)'}},'Показувати попередній результат (як підказку)')
          )
        ),
        React.createElement('div',{className:'settings-card', style:{display:'flex',gap:'16px',alignItems:'center'}},
          React.createElement('div', {style:{flex:1}},
            React.createElement('h3',null,React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'8px'}}, React.createElement('div',{style:{display:'flex',alignItems:'center',marginTop:'-1px'}},React.createElement(SmartphoneIcon)), 'На робочий стіл')),
            React.createElement('p',{style:{lineHeight:'1.5', marginBottom:0, marginTop:'8px', fontSize:'13px'}},
              'У Safari натисни «Поділитися» (квадрат зі стрілкою) → «На початковий екран». Апка працюватиме як повноцінний додаток з цією іконкою.'
            )
          ),
          React.createElement('img', {src:'assets/icon_book.png', style:{width:'64px',height:'64px',borderRadius:'16px',boxShadow:'0 4px 12px rgba(0,0,0,0.3)', flexShrink:0}})
        ),
        // theme section
        React.createElement('div',{className:'settings-card'},
          React.createElement('h3',null,'🎨 Тема оформлення'),
          React.createElement('p',null,'Підберіть кольорову гаму під свій настрій'),
          React.createElement('div',{style:{display:'flex',gap:'8px',marginTop:'14px',flexWrap:'wrap'}},
            THEMES.map(t=>
              React.createElement('button',{key:t.id,onClick:()=>setSettings(s=>({...s,theme:t.id})),style:{
                flex:'1 1 0', minWidth:'52px',
                height:'44px', borderRadius:'10px', cursor:'pointer',
                background:`linear-gradient(135deg,${t.accent},${t.dark})`,
                border:`2px solid ${(settings.theme||'classic')===t.id?'#fff':'transparent'}`,
                boxShadow:(settings.theme||'classic')===t.id?`0 0 0 1px ${t.accent},0 4px 12px rgba(0,0,0,.5)`:'none',
                transition:'all .2s', position:'relative', display:'flex', alignItems:'center', justifyContent:'center'
              }},
                React.createElement('span',{style:{fontSize:'10px',fontWeight:'800',color:'#fff',textShadow:'0 1px 4px rgba(0,0,0,.6)'}},t.name),
                (settings.theme||'classic')===t.id && React.createElement('div',{style:{position:'absolute',top:'-4px',right:'-4px',width:'14px',height:'14px',borderRadius:'50%',background:'#fff',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'9px',color:'#000',fontWeight:'900',boxShadow:'0 1px 4px rgba(0,0,0,.5)'}},'✓')
              )
            )
          ),
        ),

        // deleted templates
        (settings.deletedMuscles && settings.deletedMuscles.length > 0) && React.createElement('div',{className:'settings-card'},
          React.createElement('h3',null,'🗑 Видалені шаблони'),
          React.createElement('div',{style:{display:'flex',flexDirection:'column',gap:'8px',marginTop:'8px'}},
            settings.deletedMuscles.map(m=>
              React.createElement('div',{key:m,style:{display:'flex',alignItems:'center',justifyContent:'space-between',background:'var(--bg4)',padding:'10px 12px',borderRadius:'8px',border:'1px solid var(--border)',gap:'8px'}},
                React.createElement('span',{style:{color:'var(--text2)',textDecoration:'line-through',fontWeight:'600',flex:1}},m),
                React.createElement('div',{style:{display:'flex',gap:'6px',alignItems:'center'}},
                  React.createElement('button',{style:{padding:'5px 12px',fontSize:'12px',fontWeight:'700',background:'rgba(74,222,128,0.12)',color:'#4ade80',border:'1px solid rgba(74,222,128,0.25)',borderRadius:'8px',cursor:'pointer',whiteSpace:'nowrap'},onClick:()=>{
                    setSettings(s=>({...s, muscles: [...(s.muscles||[]), m], deletedMuscles: s.deletedMuscles.filter(x=>x!==m)}));
                    flash('Шаблон відновлено');
                  }},'Відновити'),
                  React.createElement('button',{style:{width:'28px',height:'28px',display:'flex',alignItems:'center',justifyContent:'center',background:'rgba(239,68,68,0.08)',border:'1px solid rgba(239,68,68,0.2)',borderRadius:'8px',cursor:'pointer',color:'var(--red)',fontSize:'14px',flexShrink:0},onClick:()=>{
                    setSettings(s=>({...s, deletedMuscles: s.deletedMuscles.filter(x=>x!==m)}));
                  }},React.createElement(XIcon,{size:14}))
                )
              )
            )
          )
        ),

        // admin panel
        ((adminTaps.logo && adminTaps.sync) || localStorage.getItem('override_uid') || (uid || '').startsWith(ADMIN_UID.substring(0,8))) && React.createElement('div',{className:'settings-card'},
          React.createElement('h3',null,'👑 Admin Panel'),
          React.createElement('p',{style:{fontSize:'12px',color:'var(--text3)',marginBottom:'12px'}},'Твій UID: ',React.createElement('span',{style:{fontFamily:'monospace',color:'var(--text2)',wordBreak:'break-all',userSelect:'all'}},uid||'—')),
          React.createElement('button',{className:'save-btn',onClick:async()=>{
            try {
              const snap = await db.collection('users').get();
              const accs = [];
              snap.forEach(d => { accs.push({ uid: d.id, ...d.data() }); });
              setAdminAccounts(accs);
            } catch(e) {
              setAdminAccounts([]);
            }
            setShowAdminModal(true);
          }},'Всі акаунти'),
          localStorage.getItem('override_uid') && React.createElement('button',{className:'del-day-btn',style:{marginTop:'10px'},onClick:()=>{
            localStorage.removeItem('override_uid');
            window.location.reload();
          }},'Повернутись у свій акаунт')
        ),
      )
    );
  }

  function renderAdminModal(){
    if(!showAdminModal) return null;

    // Saved accounts from localStorage
    let savedAccounts = [];
    try { savedAccounts = JSON.parse(localStorage.getItem('admin_known_uids') || '[]'); } catch{}

    async function switchToUid(targetUid) {
      if(!targetUid || !targetUid.trim()) return;
      targetUid = targetUid.trim();
      if(targetUid === uid && !localStorage.getItem('override_uid')) { flash('Це вже твій акаунт'); return; }
      setCloudStatus('connecting');

      // Очищаємо дані ДО завантаження — щоб не лишались старі
      setData({});
      setSelected(todayKey());
      setDraft(null);
      persist(STORAGE, {});

      const cloud = await loadFromCloud(targetUid);
      if(cloud) {
        localStorage.setItem('override_uid', targetUid);
        setUid(targetUid);
        setData(cloud.data || {});
        if(cloud.settings) {
          setSettings(cloud.settings);
          persist(SETTINGS_KEY, cloud.settings);
        }
        persist(STORAGE, cloud.data || {});
        const existing = JSON.parse(localStorage.getItem('admin_known_uids') || '[]');
        if(!existing.includes(targetUid)) {
          localStorage.setItem('admin_known_uids', JSON.stringify([targetUid, ...existing].slice(0,10)));
        }
        setAdminUidInput('');
        setShowAdminModal(false);
        setCloudStatus('synced');
        if(cloud._workoutsBlocked) {
          flash('⚠️ Тренування заблоковані rules — оновіть Firestore Rules');
        } else {
          const name = cloud.settings?.userName || targetUid.substring(0,8) + '…';
          flash('👤 ' + name + ' — ' + Object.keys(cloud.data || {}).length + ' тренувань');
        }
      } else {
        // Повертаємось на свій акаунт якщо не знайдено
        const myCloud = await loadFromCloud(ADMIN_UID);
        if(myCloud){ setData(myCloud.data||{}); if(myCloud.settings)setSettings(myCloud.settings); persist(STORAGE,myCloud.data||{}); }
        localStorage.removeItem('override_uid');
        setUid(ADMIN_UID);
        setCloudStatus('synced');
        flash('Акаунт не знайдено');
      }
    }

    return React.createElement('div', {className:'cc-overlay', onClick:()=>setShowAdminModal(false)},
      React.createElement('div', {className:'cc-modal', onClick:e=>e.stopPropagation(), style:{maxHeight:'85vh',overflow:'auto',padding:'24px'}},
        React.createElement('div', {className:'cc-header', style:{marginBottom:'20px'}},
          React.createElement('div', {className:'cc-title'}, '👑 Всі акаунти'),
          React.createElement('button', {className:'cc-btn', onClick:()=>setShowAdminModal(false)}, React.createElement(XIcon))
        ),

        // Current UID display
        React.createElement('div', {style:{background:'var(--bg3)',borderRadius:'12px',padding:'10px 14px',marginBottom:'16px',border:'1px solid var(--border)'}},
          React.createElement('div', {style:{fontSize:'11px',color:'var(--text3)',marginBottom:'2px',textTransform:'uppercase',letterSpacing:'0.05em'}},'Поточний UID'),
          React.createElement('div', {style:{fontSize:'11px',fontFamily:'monospace',color:'var(--green2)',wordBreak:'break-all',userSelect:'all'}}, uid || '—')
        ),

        // Accounts list from Firebase
        adminAccounts.length > 0
          ? React.createElement(React.Fragment, null,
              React.createElement('div', {style:{fontSize:'12px',color:'var(--text3)',marginBottom:'10px'}}, adminAccounts.length + ' акаунтів знайдено'),
              adminAccounts.map((acc, i) => React.createElement('div', {
                key: acc.uid,
                onClick: ()=>switchToUid(acc.uid),
                style:{
                  padding:'12px 14px', marginBottom:'8px', cursor:'pointer',
                  background: acc.uid===uid ? 'rgba(124,58,237,0.12)' : 'var(--bg3)',
                  border:'1px solid '+(acc.uid===uid?'var(--accent-dark)':'var(--border)'),
                  borderRadius:'12px'
                }
              },
                React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:'4px'}},
                  React.createElement('div', {style:{fontSize:'14px',fontWeight:'700',color: acc.uid===uid?'var(--accent2)':'var(--text1)'}},
                    acc.uid===uid && React.createElement('span',{style:{color:'var(--green2)',marginRight:'6px'}},'● '),
                    acc.settings?.userName || '—'
                  ),
                  React.createElement('div', {style:{fontSize:'11px',color:'var(--text3)'}},
                    acc.updatedAt?.toDate ? acc.updatedAt.toDate().toLocaleDateString('uk-UA') : '—'
                  )
                ),
                React.createElement('div', {style:{fontSize:'10px',fontFamily:'monospace',color:'var(--text3)',wordBreak:'break-all'}}, acc.uid)
              ))
            )
          : React.createElement(React.Fragment, null,
              // Manual UID input fallback
              React.createElement('div', {style:{fontSize:'13px',color:'var(--text2)',marginBottom:'8px',fontWeight:'600'}},'Або введи UID вручну:'),
              React.createElement('div', {style:{display:'flex',gap:'8px',marginBottom:'16px'}},
                React.createElement('input', {
                  type:'text', placeholder:'Вставте UID сюди…',
                  value: adminUidInput,
                  onChange: e=>setAdminUidInput(e.target.value),
                  onKeyDown: e=>{ if(e.key==='Enter') switchToUid(adminUidInput); },
                  style:{
                    flex:1, background:'var(--bg3)', border:'1px solid var(--border2)',
                    borderRadius:'10px', padding:'10px 14px', color:'var(--text1)',
                    fontSize:'13px', fontFamily:'monospace', outline:'none'
                  }
                }),
                React.createElement('button', {
                  onClick:()=>switchToUid(adminUidInput),
                  style:{
                    background:'var(--accent-dark)',color:'#fff',border:'none',
                    borderRadius:'10px',padding:'10px 16px',fontWeight:'700',
                    fontSize:'13px',cursor:'pointer',whiteSpace:'nowrap'
                  }
                }, 'Перейти')
              ),
              savedAccounts.length > 0 && React.createElement(React.Fragment, null,
                React.createElement('div', {style:{fontSize:'13px',color:'var(--text2)',marginBottom:'8px',fontWeight:'600'}},'Збережені:'),
                savedAccounts.map((savedUid, i) => React.createElement('div', {
                  key: i,
                  onClick: ()=>switchToUid(savedUid),
                  style:{
                    display:'flex',alignItems:'center',justifyContent:'space-between',
                    padding:'10px 14px',marginBottom:'6px',
                    background: savedUid===uid?'rgba(124,58,237,0.12)':'var(--bg3)',
                    border:'1px solid '+(savedUid===uid?'var(--accent-dark)':'var(--border)'),
                    borderRadius:'10px',cursor:'pointer'
                  }
                },
                  React.createElement('div', {style:{fontSize:'12px',fontFamily:'monospace',color:'var(--text2)',wordBreak:'break-all',flex:1}},
                    savedUid===uid && React.createElement('span',{style:{color:'var(--green2)',marginRight:'6px'}},'● '),
                    savedUid
                  ),
                  React.createElement('button', {
                    onClick:(e)=>{ e.stopPropagation(); const next=savedAccounts.filter(x=>x!==savedUid); localStorage.setItem('admin_known_uids',JSON.stringify(next)); flash('Видалено'); setShowAdminModal(false); setTimeout(()=>setShowAdminModal(true),50); },
                    style:{background:'none',border:'none',color:'var(--text3)',cursor:'pointer',padding:'4px',flexShrink:0}
                  }, React.createElement(XIcon, {size:14}))
                ))
              )
            )
      )
    );
  }

    function renderBwPicker(){
    if(!showBwPicker) return null;
    const grid = buildGrid(bwPickerYear, bwPickerMonth);
    
    return React.createElement('div',{className:'cc-overlay',onClick:()=>setShowBwPicker(false)},
      React.createElement('div',{className:'cc-modal',onClick:e=>e.stopPropagation(),style:{padding:0,overflow:'hidden'}},
        React.createElement('div',{className:'calendar-wrap',style:{marginBottom:0,border:'none',borderRadius:0}},
          React.createElement('div',{className:'cal-nav'},
            React.createElement('button',{className:'cal-arrow',onClick:()=>setBwPickerMonth(m=>{if(m===0){setBwPickerYear(y=>y-1);return 11}return m-1})},React.createElement(ArrowLeftIcon)),
            React.createElement('span',{className:'cal-month'},`${MONTHS[bwPickerMonth]} ${bwPickerYear}`),
            React.createElement('button',{className:'cal-arrow',onClick:()=>setBwPickerMonth(m=>{if(m===11){setBwPickerYear(y=>y+1);return 0}return m+1})},React.createElement(ArrowRightIcon))
          ),
          React.createElement('div',{className:'cal-weekdays'},
            WEEKDAYS.map(w=>React.createElement('div',{key:w,className:'cal-wd'},w))
          ),
          React.createElement('div',{className:'cal-grid'},
            grid.map((d,i)=>{
              if(!d) return React.createElement('div',{key:i,className:'cal-day empty'});
              const k = toKey(new Date(bwPickerYear, bwPickerMonth, d));
              const isSel = k === bwDate;
              const hasData = settings.weightHistory && settings.weightHistory[k];
              const cls = 'cal-day' + (isSel?' selected':'') + (k===todayKey()?' today':'') + (hasData?' has-workout':'');
              return React.createElement('div',{key:i,className:cls,onClick:()=>{
                setBwDate(k);
                setShowBwPicker(false);
              }},d,hasData&&React.createElement('div',{className:'day-dot '+(k<todayKey()?'past':'current')}));
            })
          )
        )
      )
    );
  }

  function renderMeasPicker(){
    if(!showMeasPicker) return null;
    const grid = buildGrid(measPickerYear, measPickerMonth);
    
    return React.createElement('div',{className:'cc-overlay',onClick:()=>setShowMeasPicker(false)},
      React.createElement('div',{className:'cc-modal',onClick:e=>e.stopPropagation(),style:{padding:0,overflow:'hidden'}},
        React.createElement('div',{className:'calendar-wrap',style:{marginBottom:0,border:'none',borderRadius:0}},
          React.createElement('div',{className:'cal-nav'},
            React.createElement('button',{className:'cal-arrow',onClick:()=>setMeasPickerMonth(m=>{if(m===0){setMeasPickerYear(y=>y-1);return 11}return m-1})},React.createElement(ArrowLeftIcon)),
            React.createElement('span',{className:'cal-month'},`${MONTHS[measPickerMonth]} ${measPickerYear}`),
            React.createElement('button',{className:'cal-arrow',onClick:()=>setMeasPickerMonth(m=>{if(m===11){setMeasPickerYear(y=>y+1);return 0}return m+1})},React.createElement(ArrowRightIcon))
          ),
          React.createElement('div',{className:'cal-weekdays'},
            WEEKDAYS.map(w=>React.createElement('div',{key:w,className:'cal-wd'},w))
          ),
          React.createElement('div',{className:'cal-grid'},
            grid.map((d,i)=>{
              if(!d) return React.createElement('div',{key:i,className:'cal-day empty'});
              const k = toKey(new Date(measPickerYear, measPickerMonth, d));
              const isSel = k === measDate;
              const hasData = settings.measHistory && settings.measHistory[k];
              const cls = 'cal-day' + (isSel?' selected':'') + (k===todayKey()?' today':'') + (hasData?' has-workout':'');
              return React.createElement('div',{key:i,className:cls,onClick:()=>{
                setMeasDate(k);
                setShowMeasPicker(false);
              }},d,hasData&&React.createElement('div',{className:'day-dot '+(k<todayKey()?'past':'current')}));
            })
          )
        )
      )
    );
  }

  function renderThemePicker(isOnboarding=false){
    if(!showThemePicker) return null;
    const cur = settings.theme || 'classic';
    return React.createElement('div',{className:'cc-overlay',onClick:isOnboarding?null:()=>setShowThemePicker(false),style:{zIndex:9999,flexDirection:'column',alignItems:'center',justifyContent:'center',padding:'20px'}},
      React.createElement('div',{onClick:e=>e.stopPropagation(),style:{width:'100%',maxWidth:'420px',background:'var(--bg2)',border:'1px solid var(--border)',borderRadius:'24px',padding:'28px 20px',boxShadow:'0 20px 60px rgba(0,0,0,.8)'}},
        React.createElement('div',{style:{textAlign:'center',marginBottom:'6px',fontSize:'24px'}},'\uD83C\uDFA8'),
        React.createElement('h2',{style:{textAlign:'center',fontSize:'20px',fontWeight:'800',marginBottom:'6px'}},isOnboarding?'Оберіть тему':'Тема оформлення'),
        React.createElement('p',{style:{textAlign:'center',fontSize:'13px',color:'var(--text3)',marginBottom:'24px'}},isOnboarding?'Можна змінити пізніше в Налаштуваннях':'Ваш стиль — ваш вибір'),
        React.createElement('div',{style:{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'12px',marginBottom:'20px'}},
          THEMES.map(t=>
            React.createElement('button',{key:t.id,onClick:()=>{setSettings(s=>({...s,theme:t.id}));},style:{
              background:t.bg, border:`2px solid ${cur===t.id?t.accent:'transparent'}`,
              borderRadius:'16px', padding:'16px 12px', cursor:'pointer',
              outline: cur===t.id?`0 0 0 2px ${t.accent} inset`:'none',
              transition:'all .2s', position:'relative', overflow:'hidden',
              boxShadow: cur===t.id?`0 0 0 2px ${t.accent}, 0 8px 24px rgba(0,0,0,.5)`:'0 4px 12px rgba(0,0,0,.4)'
            }},
              React.createElement('div',{style:{display:'flex',gap:'5px',marginBottom:'10px'}},
                React.createElement('div',{style:{flex:1,height:'10px',borderRadius:'5px',background:t.accent,opacity:0.9}}),
                React.createElement('div',{style:{flex:1,height:'10px',borderRadius:'5px',background:t.dark,opacity:0.7}}),
                React.createElement('div',{style:{width:'10px',height:'10px',borderRadius:'5px',background:'#ffffff',opacity:0.15}})
              ),
              React.createElement('div',{style:{display:'flex',gap:'5px',marginBottom:'10px'}},
                React.createElement('div',{style:{height:'6px',width:'60%',borderRadius:'3px',background:'rgba(255,255,255,0.15)'}}),
                React.createElement('div',{style:{height:'6px',flex:1,borderRadius:'3px',background:`${t.accent}44`}})
              ),
              React.createElement('div',{style:{height:'24px',borderRadius:'8px',background:`${t.accent}22`,border:`1px solid ${t.accent}44`,marginBottom:'8px'}}),
              React.createElement('div',{style:{fontSize:'13px',fontWeight:'700',color:t.accent,textAlign:'left'}},t.name),
              cur===t.id && React.createElement('div',{style:{position:'absolute',top:'8px',right:'8px',width:'18px',height:'18px',borderRadius:'50%',background:t.accent,display:'flex',alignItems:'center',justifyContent:'center',fontSize:'10px'}},'✓')
            )
          )
        ),
        isOnboarding
          ? React.createElement('button',{onClick:()=>{if(!settings.theme)setSettings(s=>({...s,theme:'classic'}));setShowThemePicker(false);},style:{width:'100%',padding:'14px',background:`linear-gradient(135deg,${(THEMES.find(t=>t.id===(settings.theme||'classic'))||THEMES[0]).accent},${(THEMES.find(t=>t.id===(settings.theme||'classic'))||THEMES[0]).dark})`,border:'none',borderRadius:'12px',color:'#fff',fontSize:'15px',fontWeight:'700',cursor:'pointer'}},'Готово →')
          : React.createElement('button',{onClick:()=>setShowThemePicker(false),style:{width:'100%',padding:'12px',background:'var(--bg4)',border:'1px solid var(--border)',borderRadius:'12px',color:'var(--text2)',fontSize:'14px',fontWeight:'600',cursor:'pointer'}},'Закрити')
      )
    );
  }

  function renderMuscleModal(){
    if(!showMuscleModal) return null;
    return React.createElement('div', {className:'cc-overlay bottom', onClick:()=>setShowMuscleModal(false)},
      React.createElement('div', {className:'cc-modal', onClick:e=>e.stopPropagation(), style:{
        maxWidth:'480px', borderRadius:'24px 24px 0 0',
        padding:'20px', background:'var(--bg1)', borderTop:'1px solid var(--border)',
        maxHeight:'70vh', overflowY:'auto'
      }},
        React.createElement('div', {style:{width:'40px', height:'4px', background:'var(--border)', borderRadius:'2px', margin:'0 auto 20px' }}),
        React.createElement('div', {className:'cc-header', style:{marginBottom:'20px'}},
          React.createElement('div', {className:'cc-title', style:{width:'100%', textAlign:'center', fontSize:'18px'}}, 'Вибір м\'яза')
        ),
        React.createElement('div', {style:{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:'16px'}},
          MUSCLE_MEASUREMENTS.map(m => React.createElement('button', {
            key: m.label,
            onClick: () => { setMeasMuscleName(m.label); setShowMuscleModal(false); },
            style: {
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px',
              padding: '12px 4px', borderRadius: '16px', border: 'none',
              background: measMuscleName === m.label ? 'rgba(52,211,153,0.1)' : 'transparent',
              color: measMuscleName === m.label ? '#34d399' : 'var(--text1)',
              cursor: 'pointer'
            }
          }, 
            (MuscleIcons[m.icon]) ? MuscleIcons[m.icon](40) : null,
            React.createElement('span', {style:{fontSize:'11px', fontWeight:'700', textAlign:'center'}}, m.label)
          ))
        )
      )
    );
  }

  function renderEditModal(){
    if(!editItem) return null;

    return React.createElement('div', {className:'cc-overlay', onClick:()=>setEditItem(null), style:{zIndex:9998}},
      React.createElement('div', {className:'cc-modal', onClick:e=>e.stopPropagation(), style:{padding:'24px', width:'320px'}},
        React.createElement('div', {style:{fontSize:'18px', fontWeight:'800', marginBottom:'4px'}}, editItem.type === 'weight' ? 'Редагувати вагу' : 'Редагувати замір'),
        React.createElement('div', {style:{fontSize:'12px', color:'var(--text3)', marginBottom:'20px'}}, fmtFull(editItem.date) + (editItem.name ? ` • ${editItem.name}` : '')),
        
        React.createElement('div', {className:'input-wrap', style:{marginBottom:'24px', background:'var(--bg3)', borderRadius:'12px', padding:'4px 12px'}},
          React.createElement('input', {
            type:'number', step:'0.1', value:editVal, 
            onChange:e=>setEditVal(e.target.value),
            style:{background:'none', border:'none', color:'var(--text1)', fontSize:'20px', fontWeight:'700', width:'100%', padding:'12px 0'}
          }),
          React.createElement('span', {style:{color:'var(--text3)', fontWeight:'700'}}, editItem.type === 'weight' ? 'кг' : 'см')
        ),

        React.createElement('div', {style:{display:'flex', flexDirection:'column', gap:'12px'}},
          React.createElement('button', {className:'primary', style:{width:'100%', padding:'14px'}, onClick:()=>{
            const finalVal = Number(editVal);
            if(finalVal > 0) {
              setSettings(s => {
                let newS;
                if(editItem.type === 'weight') {
                  newS = {...s, weightHistory: {...(s.weightHistory||{}), [editItem.date]: finalVal}, lastUpdated: Date.now()};
                } else {
                  const history = Array.isArray(s.measHistory) ? [...s.measHistory] : [];
                  if(history[editItem.originalIndex]) history[editItem.originalIndex].val = finalVal;
                  newS = {...s, measHistory: history, lastUpdated: Date.now()};
                }
                persist(SETTINGS_KEY, newS);
                return newS;
              });
              setEditItem(null);
              flash('Зміни збережено');
            }
          }}, 'Зберегти'),
          React.createElement('button', {style:{width:'100%', padding:'12px', background:'rgba(239,68,68,0.1)', border:'none', borderRadius:'12px', color:'#ef4444', fontWeight:'700', cursor:'pointer'}, onClick:()=>{
            setConfirmAction({
              title: `Видалити цей запис?`,
              onConfirm: () => {
                setSettings(s => {
                  let newS;
                  if(editItem.type === 'weight') {
                    const next = {...(s.weightHistory||{})};
                    delete next[editItem.date];
                    newS = {...s, weightHistory: next, lastUpdated: Date.now()};
                  } else {
                    const history = Array.isArray(s.measHistory) ? s.measHistory : [];
                    const nextHistory = history.filter((_, i) => i !== editItem.originalIndex);
                    newS = {...s, measHistory: nextHistory, lastUpdated: Date.now()};
                  }
                  persist(SETTINGS_KEY, newS);
                  return newS;
                });
                setEditItem(null);
                flash('Видалено');
              }
            });
          }}, 'Видалити'),
          React.createElement('button', {style:{width:'100%', padding:'12px', background:'none', border:'none', color:'var(--text3)', fontWeight:'600', cursor:'pointer'}, onClick:()=>setEditItem(null)}, 'Скасувати')
        )
      )
    );
  }

  function renderConfirmModal(){
    if(!confirmAction) return null;
    return React.createElement('div', {className:'cc-overlay', onClick:()=>setConfirmAction(null), style:{zIndex:9999}},
      React.createElement('div', {className:'cc-modal', onClick:e=>e.stopPropagation(), style:{padding:'24px', textAlign:'center', width:'300px'}},
        React.createElement('div', {style:{fontSize:'18px', fontWeight:'800', marginBottom:'12px'}}, 'Підтвердження'),
        React.createElement('div', {style:{fontSize:'14px', color:'var(--text2)', marginBottom:'24px'}}, confirmAction.title),
        React.createElement('div', {style:{display:'flex', gap:'12px'}},
          React.createElement('button', {style:{flex:1, background:'var(--bg3)', color:'var(--text1)', border:'none', padding:'12px', borderRadius:'12px', fontWeight:'700'}, onClick:()=>setConfirmAction(null)}, 'Скасувати'),
          React.createElement('button', {style:{flex:1, background:'#ef4444', color:'white', border:'none', padding:'12px', borderRadius:'12px', fontWeight:'700'}, onClick:()=>{
            confirmAction.onConfirm();
            setConfirmAction(null);
          }}, 'Видалити')
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
      React.createElement('div',{className:'cc-modal',onClick:e=>e.stopPropagation(),style:{padding:0,overflow:'hidden'}},
        React.createElement('div',{className:'calendar-wrap',style:{marginBottom:0,border:'none',borderRadius:0}},
          React.createElement('div',{className:'cal-nav'},
            React.createElement('button',{className:'cal-arrow',onClick:()=>setPickerMonth(m=>{if(m===0){setPickerYear(y=>y-1);return 11}return m-1})},React.createElement(ArrowLeftIcon)),
            React.createElement('span',{className:'cal-month'},`${MONTHS[pickerMonth]} ${pickerYear}`),
            React.createElement('button',{className:'cal-arrow',onClick:()=>setPickerMonth(m=>{if(m===11){setPickerYear(y=>y+1);return 0}return m+1})},React.createElement(ArrowRightIcon))
          ),
          React.createElement('div',{className:'cal-weekdays'},
            WEEKDAYS.map(w=>React.createElement('div',{key:w,className:'cal-wd'},w))
          ),
          React.createElement('div',{className:'cal-grid'},
            grid.map((d,idx)=>{
              if(!d) return React.createElement('div',{key:idx,className:'cal-day empty'});
              const k = toKey(new Date(pickerYear, pickerMonth, d));
              let cls = 'cal-day';
              if(k===todayKey()) cls+=' today';
              if(data[k]) cls += ' has-workout';
              if(k === pickerStart || k === pickerEnd) cls += ' selected';
              if(k === pickerStart) cls += ' range-start';
              if(k === pickerEnd) cls += ' range-end';
              if(pickerStart && pickerEnd && k > pickerStart && k < pickerEnd) cls += ' in-range';
              return React.createElement('div',{key:idx,className:cls,onClick:()=>handleDayClick(d)},d,data[k]&&React.createElement('div',{className:'day-dot '+(k<todayKey()?'past':'current')}));
            })
          ),
          React.createElement('div',{className:'cc-footer', style:{marginTop:'20px'}},
            React.createElement('button',{className:'cc-action secondary',onClick:()=>{setFilterStart('all');setFilterEnd('all');setShowPicker(false)}},'За весь час'),
            React.createElement('button',{className:'cc-action primary',onClick:()=>{setFilterStart(pickerStart);setFilterEnd(pickerEnd);setShowPicker(false)}},'Застосувати')
          )
        )
      )
    );
  }

  // ─── MAIN RENDER ───────────────────────────────────────────────
  return React.createElement('div',{id:'app-root'},
    React.createElement('div',{className:'page'},
      React.createElement('div',{className:'app-header'},
        React.createElement('div',{className:'app-logo'},
          React.createElement('div',{className:'logo-icon', onClick:()=>setAdminTaps(p=>({...p, logo: true})), style:{cursor:'pointer', background:'none', padding:0}},
            React.createElement('img', {src: 'assets/icon_book.png', style: {width: '48px', height: '48px', borderRadius: '12px'}})
          ),
          React.createElement('div',{className:'logo-text'},
            React.createElement('h1',null,'Gym Notebook'),
            React.createElement('p',null,'Щоденник тренувань')
          )
        ),
        React.createElement('div',{className:'cloud-status', style:{cursor:tab==='settings'?'pointer':'default'}, onClick:()=>{if(tab==='settings'&&adminTaps.logo)setAdminTaps(p=>({...p,sync:true}))}},
          React.createElement('span',{className:'cloud-dot '+(cloudStatus==='synced'?'green':cloudStatus==='saving'?'yellow':'gray')}),
          React.createElement('span',{className:'cloud-text'},
            cloudStatus==='synced'?React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'4px'}}, React.createElement(CheckCircleIcon), 'Синхр.'):cloudStatus==='saving'?React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'4px'}}, React.createElement(RefreshIcon), 'Зберіг...'):cloudStatus==='connecting'?React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'4px'}}, React.createElement(WifiIcon), 'З\'єдн...'):React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'4px'}}, React.createElement(WifiOffIcon), 'Офлайн')
          )
        )
      ),
      tab==='calendar'&&renderCalendar(),
      tab==='history'&&renderHistory(),
      tab==='settings'&&renderSettings(),
      tab==='analytics'&&renderAnalytics()
    ),
    // bottom tabs
    React.createElement('div',{className:'tab-bar'},
      React.createElement('div',{className:'tab-bar-inner'},
        React.createElement('button',{className:'tab-btn'+(tab==='calendar'?' active':''),onClick:()=>setTab('calendar')},
          React.createElement('span',{className:'tab-icon'},React.createElement(CalendarIcon)),React.createElement('span',null,'Календар')
        ),
        React.createElement('button',{className:'tab-btn'+(tab==='history'?' active':''),onClick:()=>setTab('history')},
          React.createElement('span',{className:'tab-icon'},React.createElement(HistoryIcon)),React.createElement('span',null,'Щоденник')
        ),
        React.createElement('button',{className:'tab-btn'+(tab==='analytics'?' active':''),onClick:()=>setTab('analytics')},
          React.createElement('span',{className:'tab-icon'},React.createElement(TrendingUpIcon)),React.createElement('span',null,'Аналітика')
        ),
        React.createElement('button',{className:'tab-btn'+(tab==='settings'?' active':''),onClick:()=>setTab('settings')},
          React.createElement('span',{className:'tab-icon'},React.createElement(SettingsIcon)),React.createElement('span',null,'Налаштування')
        )
      )
    ),
    toast&&React.createElement('div',{key:toast.id,className:'toast'+(toast.actionText?' toast-action':''), style:{display:'flex', alignItems:'center', justifyContent:'space-between', gap:'16px', '--toast-dur': (toast.duration||1800)+'ms'}},
      React.createElement('span', null, toast.m || toast),
      toast.actionText && React.createElement(React.Fragment, null,
        React.createElement('button', {
          onClick: () => { toast.actionFn(); setToast(null); clearTimeout(tRef.current); },
          style: {background:'rgba(139,27,50,0.85)',color:'#fca5a5',border:'1px solid rgba(220,80,100,0.35)',padding:'6px 12px',borderRadius:'8px',fontWeight:'700',fontSize:'13px',cursor:'pointer',whiteSpace:'nowrap',flexShrink:0}
        }, toast.actionText)
      )
    ),
      renderCustomPicker(),
      renderBwPicker(),
      renderMeasPicker(),
      renderAdminModal(),
      renderMuscleModal(),
      renderEditModal(),
      renderConfirmModal(),
      renderCompareModal(),
      renderThemePicker(settings.theme === undefined)

  );
}

ReactDOM.createRoot(document.getElementById('root')).render(React.createElement(App));
