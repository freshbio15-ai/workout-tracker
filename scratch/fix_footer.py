import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Fix cc-footer padding inside calendar-wrap
js = js.replace(
    "React.createElement('div',{className:'cc-footer', style:{marginTop:'20px', padding: '0 20px 20px'}}",
    "React.createElement('div',{className:'cc-footer', style:{marginTop:'20px'}})"
)

# Add .today class to renderCustomPicker
js = js.replace(
    "let cls = 'cal-day';",
    "let cls = 'cal-day';\n              if(k===todayKey()) cls+=' today';"
)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Footer and today class fixed.")
