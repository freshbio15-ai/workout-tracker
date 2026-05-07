import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Replace all occurrences of 'фунт' with 'lbs'
js = js.replace("'фунт'", "'lbs'")
js = js.replace(">фунт<", ">lbs<") # button text

# Update weightChartData map to convert based on unit
old_weight_chart_data = "const weightChartData = weightKeys.map(k => ({ date: k, weight: weightHistory[k] }));"
new_weight_chart_data = "const weightChartData = weightKeys.map(k => ({ date: k, weight: bwUnit === 'lbs' ? (weightHistory[k] / 0.453592) : weightHistory[k] }));"
if old_weight_chart_data in js:
    js = js.replace(old_weight_chart_data, new_weight_chart_data)
else:
    print("Warning: weightChartData replacement failed.")

# Update title
old_title = "'Динаміка власної ваги (кг)',"
new_title = "`Динаміка власної ваги (${bwUnit})`,"
if old_title in js:
    js = js.replace(old_title, new_title)
else:
    print("Warning: title replacement failed.")

# Update prompt edit logic
old_click = """              return React.createElement('div', {key: i, className: 'chart-col', style:{cursor:'pointer'}, onClick:()=>{
                const nw = prompt(`Змінити вагу за ${fmtShort(d.date)}?\\nВведіть нове значення (або залиште порожнім щоб видалити):`, d.weight);
                if (nw !== null) {
                  if (nw.trim() === '') {
                    setSettings(s => { const ns = {...s, weightHistory: {...(s.weightHistory||{})}}; delete ns.weightHistory[d.date]; return ns; });
                    flash('Запис видалено');
                  } else {
                    const val = Number(nw);
                    if (!isNaN(val) && val > 0) {
                      setSettings(s => ({...s, weightHistory: {...(s.weightHistory||{}), [d.date]: val}}));
                      flash('Запис оновлено');
                    }
                  }
                }
              }},"""

new_click = """              return React.createElement('div', {key: i, className: 'chart-col', style:{cursor:'pointer'}, onClick:()=>{
                const nw = prompt(`Змінити вагу за ${fmtShort(d.date)} (${bwUnit})?\\nВведіть нове значення (або залиште порожнім щоб видалити):`, d.weight % 1 === 0 ? d.weight : d.weight.toFixed(3));
                if (nw !== null) {
                  if (nw.trim() === '') {
                    setSettings(s => { const ns = {...s, weightHistory: {...(s.weightHistory||{})}}; delete ns.weightHistory[d.date]; return ns; });
                    flash('Запис видалено');
                  } else {
                    let val = Number(nw);
                    if (!isNaN(val) && val > 0) {
                      if (bwUnit === 'lbs') val = val * 0.453592;
                      setSettings(s => ({...s, weightHistory: {...(s.weightHistory||{}), [d.date]: val}}));
                      flash('Запис оновлено');
                    }
                  }
                }
              }},"""

if old_click in js:
    js = js.replace(old_click, new_click)
else:
    print("Warning: chart click handler replacement failed.")

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Applied lbs changes")
