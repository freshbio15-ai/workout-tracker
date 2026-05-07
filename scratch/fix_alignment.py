import re

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

classes_to_fix = [
    ".stats-overlay",
    ".stats-close",
    ".cal-arrow",
    ".add-muscle-btn",
    ".emoji-muscle-btn",
    ".ex-remove-btn",
    ".bw-btn",
    ".timer-btn-inline",
    ".set-del-btn",
    ".timer-btn",
    ".timer-cancel",
    ".h-filter-btn",
    ".cc-overlay",
    ".cc-day",
    ".mt-emoji",
    ".pr-badge",
    ".logo-icon" # line 38, logo-icon is a single icon container
]

# We will search for each class block and replace justify-content:space-between with justify-content:center
for cls in classes_to_fix:
    # Find the block starting with cls + { or cls + " {"
    pattern = r'(' + re.escape(cls) + r'(?:\s|\n|\.|:)*{[^}]*)justify-content:space-between([^}]*})'
    css = re.sub(pattern, r'\1justify-content:center\2', css)

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Add optical alignment (marginTop: '-1px') to header icons that are inside flex containers with text
# History header
js = js.replace(
    "React.createElement(HistoryIcon),'Історія'",
    "React.createElement('div',{style:{display:'flex',alignItems:'center',marginTop:'-2px'}},React.createElement(HistoryIcon)),'Історія'"
)

# Analytics header
js = js.replace(
    "React.createElement(TrendingUpIcon), 'Аналітика'",
    "React.createElement('div',{style:{display:'flex',alignItems:'center',marginTop:'-2px'}},React.createElement(TrendingUpIcon)), 'Аналітика'"
)

# Settings header
js = js.replace(
    "React.createElement(SettingsIcon),'Налаштування'",
    "React.createElement('div',{style:{display:'flex',alignItems:'center',marginTop:'-2px'}},React.createElement(SettingsIcon)),'Налаштування'"
)

# Settings subheaders
js = js.replace(
    "React.createElement(WeightIcon), 'Власна вага'",
    "React.createElement('div',{style:{display:'flex',alignItems:'center',marginTop:'-1px'}},React.createElement(WeightIcon)), 'Власна вага'"
)
js = js.replace(
    "React.createElement(SmartphoneIcon), 'Як зберегти на робочий стіл'",
    "React.createElement('div',{style:{display:'flex',alignItems:'center',marginTop:'-1px'}},React.createElement(SmartphoneIcon)), 'Як зберегти на робочий стіл'"
)
js = js.replace(
    "React.createElement(BarChartIcon), 'Статистика'",
    "React.createElement('div',{style:{display:'flex',alignItems:'center',marginTop:'-1px'}},React.createElement(BarChartIcon)), 'Статистика'"
)

# Date Trigger Button fix text nodes so they act as one flex item
js = js.replace(
    "React.createElement(CalendarIcon, {size: 16}), ' ', selected === tKey ? 'Сьогодні' : fmtFull(selected), ' ▾')",
    "React.createElement(CalendarIcon, {size: 16}), React.createElement('span', {style:{marginTop:'1px'}}, selected === tKey ? 'Сьогодні ▾' : fmtFull(selected) + ' ▾'))"
)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Icons aligned and centered perfectly.")
