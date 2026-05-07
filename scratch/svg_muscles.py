import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Define SVGs
svg_defs = """const ChestMuscleIcon = ({size=24, color='currentColor', className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: color, strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M4 8l8-4 8 4v4c0 4-3 8-8 12-5-4-8-8-8-12z'}), React.createElement('line', {x1: 12, y1: 4, x2: 12, y2: 20}));
const BackMuscleIcon = ({size=24, color='currentColor', className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: color, strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('polygon', {points: '12 2 22 8 18 22 6 22 2 8'}), React.createElement('line', {x1: 12, y1: 2, x2: 12, y2: 22}));
const LegsMuscleIcon = ({size=24, color='currentColor', className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: color, strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M8 2v20'}), React.createElement('path', {d: 'M16 2v20'}), React.createElement('path', {d: 'M6 12h4'}), React.createElement('path', {d: 'M14 12h4'}));
const ShouldersMuscleIcon = ({size=24, color='currentColor', className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: color, strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M2 14c0-6.6 5.4-12 12-12s12 5.4 12 12'}), React.createElement('line', {x1: 2, y1: 14, x2: 22, y2: 14}));
const BicepsMuscleIcon = ({size=24, color='currentColor', className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: color, strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M14 4h-4c-4 0-6 2-6 6 0 2 1 4 2 5v5h8v-5c1-1 2-3 2-5 0-4-2-6-6-6z'}), React.createElement('circle', {cx: 14, cy: 12, r: 3}));
const TricepsMuscleIcon = ({size=24, color='currentColor', className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: color, strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('path', {d: 'M10 4h4c4 0 6 2 6 6 0 2-1 4-2 5v5H10v-5c-1-1-2-3-2-5 0-4 2-6 6-6z'}), React.createElement('circle', {cx: 10, cy: 12, r: 3}));
const AbsMuscleIcon = ({size=24, color='currentColor', className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: color, strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('rect', {x: 6, y: 4, width: 12, height: 16, rx: 2}), React.createElement('line', {x1: 6, y1: 12, x2: 18, y2: 12}), React.createElement('line', {x1: 12, y1: 4, x2: 12, y2: 20}));

const MUSCLES = [
  {id:'chest', icon: ChestMuscleIcon, color:'#ec4899', label:'Груди'},
  {id:'back', icon: BackMuscleIcon, color:'#3b82f6', label:'Спина'},
  {id:'legs', icon: LegsMuscleIcon, color:'#10b981', label:'Ноги'},
  {id:'shoulders', icon: ShouldersMuscleIcon, color:'#f97316', label:'Плечі'},
  {id:'biceps', icon: BicepsMuscleIcon, color:'#ef4444', label:'Біцепс'},
  {id:'triceps', icon: TricepsMuscleIcon, color:'#06b6d4', label:'Трицепс'},
  {id:'abs', icon: AbsMuscleIcon, color:'#eab308', label:'Прес'},
];
"""

old_muscle_emojis = """// muscles are image-based, assigned per exercise
const MUSCLE_EMOJIS = [
  {id:'chest',icon:'assets/icon_chest.png',label:'Груди'},
  {id:'back',icon:'assets/icon_back.png',label:'Спина'},
  {id:'legs',icon:'assets/icon_legs.png',label:'Ноги'},
  {id:'shoulders',icon:'assets/icon_shoulders.png',label:'Плечі'},
  {id:'biceps',icon:'assets/icon_biceps.png',label:'Біцепс'},
  {id:'triceps',icon:'assets/icon_triceps.png',label:'Трицепс'},
  {id:'abs',icon:'assets/icon_abs.png',label:'Прес'},
  {id:'cardio',icon:'assets/icon_cardio.png',label:'Кардіо'},
];"""

if old_muscle_emojis in js:
    js = js.replace(old_muscle_emojis, svg_defs)
else:
    print("Failed to replace MUSCLE_EMOJIS array")

# 2. Replace occurrences of MUSCLE_EMOJIS
js = js.replace("MUSCLE_EMOJIS", "MUSCLES")

# 3. Replace the img tag for the selector
old_selector_img = "React.createElement('img',{src:mg.icon,className:'muscle-btn-icon',alt:mg.label})"
new_selector_svg = "React.createElement(mg.icon,{size:20,color:mg.color})"
js = js.replace(old_selector_img, new_selector_svg)

# 4. Replace the img tag for the inline icons
old_inline_img = "React.createElement('img',{src:mg.icon,className:'inline-muscle-icon'})"
new_inline_svg = "React.createElement(mg.icon,{size:14,color:mg.color})"
js = js.replace(old_inline_img, new_inline_svg)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("SVGs injected")
