import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    content = f.read()

# 1. Add SVGs
svgs = """// ── SVGs ─────────────────────────────────────────────────────────────
const CalendarIcon = ({size=24, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('rect', {x: 3, y: 4, width: 18, height: 18, rx: 2, ry: 2}), React.createElement('line', {x1: 16, y1: 2, x2: 16, y2: 6}), React.createElement('line', {x1: 8, y1: 2, x2: 8, y2: 6}), React.createElement('line', {x1: 3, y1: 10, x2: 21, y2: 10}));
const HistoryIcon = ({size=24, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('line', {x1: 18, y1: 20, x2: 18, y2: 10}), React.createElement('line', {x1: 12, y1: 20, x2: 12, y2: 4}), React.createElement('line', {x1: 6, y1: 20, x2: 6, y2: 14}));
const SettingsIcon = ({size=24, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('circle', {cx: 12, cy: 12, r: 3}), React.createElement('path', {d: 'M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z'}));
const TimerIcon = ({size=24, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('circle', {cx: 12, cy: 13, r: 8}), React.createElement('path', {d: 'M12 9v4l2 2'}), React.createElement('line', {x1: 10, y1: 2, x2: 14, y2: 2}));
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

"""

# Remove old SVGs block if exists
content = re.sub(r'// ── SVGs ──.*?const mkSet=\(\)=>', 'const mkSet=()=>', content, flags=re.DOTALL)
content = content.replace('const mkSet=()=>', svgs + 'const mkSet=()=>')

# Logo
content = content.replace("'💪'", "React.createElement(ActivityIcon, {size: 20})")

# Statuses
content = content.replace("'☁️ Синхр.'", "React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'4px'}}, React.createElement(CheckCircleIcon), 'Синхр.')")
content = content.replace("'⏳ Зберіг...'", "React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'4px'}}, React.createElement(RefreshIcon), 'Зберіг...')")
content = content.replace("'🔄 З\\'єдн...'", "React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'4px'}}, React.createElement(WifiIcon), 'З\\'єдн...')")
content = content.replace("'📴 Офлайн'", "React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'4px'}}, React.createElement(WifiOffIcon), 'Офлайн')")

# Day Header
content = content.replace("'📅 ', ", "React.createElement(CalendarIcon, {size: 16}), ' ', ")

# Day Panel Title / Editor
content = content.replace("'✏️ Редагування тренування'", "React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'6px'}}, React.createElement(EditIcon), 'Редагування тренування')")
content = content.replace("'Нове тренування'", "React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'6px'}}, React.createElement(PlusIcon), 'Нове тренування')")
content = content.replace("'💾 Оновити'", "React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'8px'}}, React.createElement(SaveIcon), 'Оновити')")
content = content.replace("'✅ Зберегти тренування'", "React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'8px'}}, React.createElement(CheckIcon), 'Зберегти тренування')")
content = content.replace("'🗑 Видалити'", "React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'}}, React.createElement(TrashIcon), 'Видалити')")

# History Empty State
content = content.replace("'🗑 Все видалено'", "React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'6px'}}, React.createElement(TrashIcon), 'Все видалено')")
content = content.replace("'✏️ Редагувати тренування'", "React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'}}, React.createElement(EditIcon), 'Редагувати тренування')")
content = content.replace("'📔'", "React.createElement(BookIcon)")

# History Labels
content = content.replace("'🎯 '+w.muscle", "React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'4px'}}, React.createElement(TargetIcon, {size:12}), w.muscle)")
content = content.replace("'💡'", "React.createElement(LightbulbIcon)")

# Settings Sections
content = content.replace("'🏋️ Власна вага'", "React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'8px'}}, React.createElement(WeightIcon), 'Власна вага')")
content = content.replace("'📱 Як зберегти на робочий стіл'", "React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'8px'}}, React.createElement(SmartphoneIcon), 'Як зберегти на робочий стіл')")
content = content.replace("'📊 Статистика'", "React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'8px'}}, React.createElement(BarChartIcon), 'Статистика')")
content = content.replace("'⚠️ Зона небезпеки'", "React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'8px'}}, React.createElement(AlertTriangleIcon), 'Зона небезпеки')")

# Timer Popup
content = content.replace("'⏳',fmtTimer(timeLeft)", "React.createElement(HourglassIcon, {size:20}), ' ', fmtTimer(timeLeft)")
content = content.replace("'⏱️ Таймер відпочинку'", "React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'8px'}}, React.createElement(TimerIcon, {size:18}), 'Таймер відпочинку')")
content = content.replace("'⏱ ', ", "React.createElement(TimerIcon, {size:12, style:{marginRight:'4px'}}), ")

# Add Set / Add Exercise buttons
content = content.replace("'+'", "React.createElement(PlusIcon)")
content = content.replace("'+ Підхід'", "React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'}}, React.createElement(PlusIcon), 'Підхід')")
content = content.replace("'+ Додати вправу'", "React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'}}, React.createElement(PlusIcon), 'Додати вправу')")

# Generic texts
content = content.replace("'‹'", "React.createElement(ArrowLeftIcon)")
content = content.replace("'›'", "React.createElement(ArrowRightIcon)")

# Only replace full matches for X to not replace lowercase x randomly
# XIcon replacements - checking specific usages in code:
# React.createElement('button',{className:'x-btn',onClick:()=>remEx(ei)},'✕')
content = content.replace("'✕'", "React.createElement(XIcon)")
content = content.replace("'×'", "React.createElement(XIcon)")

# Calendar emoji left in history detail header?
content = content.replace("'📅 '", "React.createElement(CalendarIcon, {size:16}), ' '")
content = content.replace("'📅'", "React.createElement(CalendarIcon, {size:16})")

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(content)
