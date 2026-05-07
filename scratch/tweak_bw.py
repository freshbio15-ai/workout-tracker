import re

# 1. Update CSS
with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

if "::-webkit-outer-spin-button" not in css:
    css += "\n\n/* Hide spin buttons */\n.set-input::-webkit-outer-spin-button,\n.set-input::-webkit-inner-spin-button {\n  -webkit-appearance: none;\n  margin: 0;\n}\n.set-input[type=number] {\n  -moz-appearance: textfield;\n}\n"
    with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
        f.write(css)

# 2. Update JS
with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# State
old_state = "  const [pickerEnd,setPickerEnd]=useState('');\n  const [bwDate,setBwDate]=useState(todayKey());\n  const [bwValue,setBwValue]=useState('');\n  const [uid,setUid]=useState(null);"
new_state = "  const [pickerEnd,setPickerEnd]=useState('');\n  const [bwDate,setBwDate]=useState(todayKey());\n  const [bwValue,setBwValue]=useState('');\n  const [showBwPicker, setShowBwPicker] = useState(false);\n  const [bwPickerYear, setBwPickerYear] = useState(new Date().getFullYear());\n  const [bwPickerMonth, setBwPickerMonth] = useState(new Date().getMonth());\n  const [uid,setUid]=useState(null);"
js = js.replace(old_state, new_state)

# Add renderBwPicker
render_bw_picker = """  function renderBwPicker(){
    if(!showBwPicker) return null;
    const grid = buildGrid(bwPickerYear, bwPickerMonth);
    
    return React.createElement('div',{className:'cc-overlay',onClick:()=>setShowBwPicker(false)},
      React.createElement('div',{className:'cc-modal',onClick:e=>e.stopPropagation()},
        React.createElement('div',{className:'cc-header'},
          React.createElement('div',{className:'cc-title'},`${MONTHS[bwPickerMonth]} ${bwPickerYear}`),
          React.createElement('div',{className:'cc-nav'},
            React.createElement('button',{className:'cc-btn',onClick:()=>setBwPickerMonth(m=>{if(m===0){setBwPickerYear(y=>y-1);return 11}return m-1})},React.createElement(ArrowLeftIcon)),
            React.createElement('button',{className:'cc-btn',onClick:()=>setBwPickerMonth(m=>{if(m===11){setBwPickerYear(y=>y+1);return 0}return m+1})},React.createElement(ArrowRightIcon))
          )
        ),
        React.createElement('div',{className:'cc-grid-header'},
          ['Пн','Вв','Ср','Чт','Пт','Сб','Нд'].map(d=>React.createElement('div',{key:d},d))
        ),
        React.createElement('div',{className:'cc-grid'},
          grid.map((d,i)=>{
            if(!d) return React.createElement('div',{key:i,className:'cc-empty'});
            const k = toKey(new Date(bwPickerYear, bwPickerMonth, d));
            const isSel = k === bwDate;
            const cls = 'cc-day' + (isSel?' selected':'') + (k===todayKey()?' today':'');
            return React.createElement('button',{key:i,className:cls,onClick:()=>{
              setBwDate(k);
              setShowBwPicker(false);
            }},d);
          })
        )
      )
    );
  }

  function renderCustomPicker(){"""

js = js.replace("  function renderCustomPicker(){", render_bw_picker)

# Replace the input type=date with the button
old_input = "React.createElement('input', {type:'date', className:'set-input', style:{flex:'1', padding:'6px', margin:0}, value:bwDate, onChange:e=>setBwDate(e.target.value)}),"
new_input = "React.createElement('button', {className:'h-filter-btn', style:{width:'auto', flex:'1', margin:0, padding:'0 12px', gap:'6px'}, onClick:()=>setShowBwPicker(true)}, React.createElement(CalendarIcon,{size:14}), fmtShort(bwDate)),"
js = js.replace(old_input, new_input)

# Add renderBwPicker to the final return
old_final = "      renderCustomPicker()\n    )\n  );\n}"
new_final = "      renderCustomPicker(),\n      renderBwPicker()\n    )\n  );\n}"
js = js.replace(old_final, new_final)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Updates applied.")
