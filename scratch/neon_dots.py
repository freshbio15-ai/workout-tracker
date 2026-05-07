import re

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

# Remove old day-dot
old_day_dot = ".cal-day.has-workout .day-dot{position:absolute;bottom:4px;width:5px;height:5px;border-radius:50%;background:var(--green2)}"
if old_day_dot in css:
    css = css.replace(old_day_dot, "")

# Add new day-dot classes
new_day_dot_css = """
.cal-day .day-dot{position:absolute;bottom:4px;width:5px;height:5px;border-radius:50%}
.cal-day .day-dot.current{background:var(--green2);box-shadow:0 0 6px var(--green2)}
.cal-day .day-dot.past{background:var(--text3)}
.cal-day.selected .day-dot{background:rgba(255,255,255,.8);box-shadow:none}
"""
css += new_day_dot_css

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# In renderCalendar
old_render_cal = "data[k]&&React.createElement('div',{className:'day-dot'})"
new_render_cal = "data[k]&&React.createElement('div',{className:'day-dot '+(k<tKey?'past':'current')})"
js = js.replace(old_render_cal, new_render_cal)

# In renderCustomPicker
old_custom_cal = "data[k]&&React.createElement('div',{className:'day-dot'})"
new_custom_cal = "data[k]&&React.createElement('div',{className:'day-dot '+(k<todayKey()?'past':'current')})"
js = js.replace(old_custom_cal, new_custom_cal)

# In renderBwPicker
old_bw_cal = """              const cls = 'cal-day' + (isSel?' selected':'') + (k===todayKey()?' today':'');
              return React.createElement('div',{key:i,className:cls,onClick:()=>{"""
new_bw_cal = """              const hasData = settings.weightHistory && settings.weightHistory[k];
              const cls = 'cal-day' + (isSel?' selected':'') + (k===todayKey()?' today':'') + (hasData?' has-workout':'');
              return React.createElement('div',{key:i,className:cls,onClick:()=>{"""
js = js.replace(old_bw_cal, new_bw_cal)

old_bw_cal_return = """              }},d);"""
new_bw_cal_return = """              }},d,hasData&&React.createElement('div',{className:'day-dot '+(k<todayKey()?'past':'current')}));"""
js = js.replace(old_bw_cal_return, new_bw_cal_return)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Neon dots added")
