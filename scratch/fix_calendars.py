import re

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

# Fix .cal-day layout
old_cal_day = ".cal-day{aspect-ratio:1;border-radius:10px;display:flex;flex-direction:column;align-items:center;justify-content:space-between;font-size:13px;font-weight:500;cursor:pointer;position:relative;transition:all .15s;border:1.5px solid transparent}"
new_cal_day = ".cal-day{aspect-ratio:1;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:500;cursor:pointer;position:relative;transition:all .15s;border:1.5px solid transparent}"
css = css.replace(old_cal_day, new_cal_day)

old_day_dot = ".cal-day.has-workout .day-dot{width:5px;height:5px;border-radius:50%;background:var(--green2);margin-top:2px}"
new_day_dot = ".cal-day.has-workout .day-dot{position:absolute;bottom:4px;width:5px;height:5px;border-radius:50%;background:var(--green2)}"
css = css.replace(old_day_dot, new_day_dot)

# Copy range classes for .cal-day
range_classes = """
.cal-day.in-range{background:rgba(124,58,237,.2);border-radius:0}
.cal-day.range-start{background:linear-gradient(135deg,var(--accent),#6d28d9);color:#fff;border-radius:10px 0 0 10px}
.cal-day.range-end{background:linear-gradient(135deg,var(--accent),#6d28d9);color:#fff;border-radius:0 10px 10px 0}
.cal-day.range-start.range-end{border-radius:10px}
"""
if ".cal-day.in-range" not in css:
    css += range_classes

# Fix muscle-row alignment
css = css.replace(".muscle-row{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:14px}", ".muscle-row{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:14px;align-items:center}")

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Replace cc- classes with cal- classes in renderCustomPicker
old_picker_nav = """        React.createElement('div',{className:'cc-header'},
          React.createElement('div',{className:'cc-title'},`${MONTHS[pickerMonth]} ${pickerYear}`),
          React.createElement('div',{className:'cc-nav'},
            React.createElement('button',{className:'cc-btn',onClick:()=>setPickerMonth(m=>{if(m===0){setPickerYear(y=>y-1);return 11}return m-1})},React.createElement(ArrowLeftIcon)),
            React.createElement('button',{className:'cc-btn',onClick:()=>setPickerMonth(m=>{if(m===11){setPickerYear(y=>y+1);return 0}return m+1})},React.createElement(ArrowRightIcon))
          )
        ),"""
new_picker_nav = """        React.createElement('div',{className:'cal-nav', style:{marginBottom:0}},
          React.createElement('button',{className:'cal-arrow',onClick:()=>setPickerMonth(m=>{if(m===0){setPickerYear(y=>y-1);return 11}return m-1})},React.createElement(ArrowLeftIcon)),
          React.createElement('span',{className:'cal-month'},`${MONTHS[pickerMonth]} ${pickerYear}`),
          React.createElement('button',{className:'cal-arrow',onClick:()=>setPickerMonth(m=>{if(m===11){setPickerYear(y=>y+1);return 0}return m+1})},React.createElement(ArrowRightIcon))
        ),"""
js = js.replace(old_picker_nav, new_picker_nav)

old_picker_grid = """        React.createElement('div',{className:'cc-grid'},
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
        ),"""

new_picker_grid = """        React.createElement('div',{className:'cal-weekdays', style:{marginTop:'16px'}},
          WEEKDAYS.map(w=>React.createElement('div',{key:w,className:'cal-wd'},w))
        ),
        React.createElement('div',{className:'cal-grid'},
          grid.map((d,i)=>{
            if(!d) return React.createElement('div',{key:i,className:'cal-day empty'});
            const k = toKey(new Date(pickerYear, pickerMonth, d));
            let cls = 'cal-day';
            if(data[k]) cls += ' has-workout';
            if(k === pickerStart || k === pickerEnd) cls += ' selected';
            if(k === pickerStart) cls += ' range-start';
            if(k === pickerEnd) cls += ' range-end';
            if(pickerStart && pickerEnd && k > pickerStart && k < pickerEnd) cls += ' in-range';
            return React.createElement('div',{key:i,className:cls,onClick:()=>handleDayClick(d)},d,data[k]&&React.createElement('div',{className:'day-dot'}));
          })
        ),"""
js = js.replace(old_picker_grid, new_picker_grid)

# Fix History page icon
old_hist_header = "React.createElement('h2', {style:{display:'flex',alignItems:'center',gap:'8px',cursor:'pointer'}, onClick:()=>setShowPicker(true)}, React.createElement(CalendarIcon), `${MONTHS[histMonth]} ${histYear}`),"
new_hist_header = "React.createElement('h2', {style:{display:'flex',alignItems:'center',gap:'8px',cursor:'pointer'}, onClick:()=>setShowPicker(true)}, React.createElement('div',{style:{display:'flex',alignItems:'center',marginTop:'-2px'}},React.createElement(CalendarIcon,{size:20})), `${MONTHS[histMonth]} ${histYear}`),"
js = js.replace(old_hist_header, new_hist_header)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Calendar scripts fixed")
