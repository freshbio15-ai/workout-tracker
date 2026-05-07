import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Fix calendar layout
old_cal = """        React.createElement('div',{className:'cc-grid-header'},
          ['Пн','Вв','Ср','Чт','Пт','Сб','Нд'].map(d=>React.createElement('div',{key:d},d))
        ),
        React.createElement('div',{className:'cc-grid'},
          grid.map((d,i)=>{
            if(!d) return React.createElement('div',{key:i,className:'cc-empty'});"""

new_cal = """        React.createElement('div',{className:'cc-grid'},
          WEEKDAYS.map(w=>React.createElement('div',{key:w,className:'cc-wd'},w)),
          grid.map((d,i)=>{
            if(!d) return React.createElement('div',{key:i,className:'cc-day empty'});"""

if old_cal in js:
    js = js.replace(old_cal, new_cal)
else:
    print("Calendar replacement failed")

# 2. Add clear all button and chart col click handler
old_chart_header = """          React.createElement('div', {className: 'chart-title', style:{display:'flex',justifyContent:'space-between',alignItems:'center', flexWrap:'wrap', gap:'12px', paddingBottom:'12px'}}, 
            'Динаміка власної ваги (кг)',"""

new_chart_header = """          React.createElement('div', {className: 'chart-title', style:{display:'flex',justifyContent:'space-between',alignItems:'center', flexWrap:'wrap', gap:'12px', paddingBottom:'12px'}}, 
            React.createElement('div', {style:{display:'flex', justifyContent:'space-between', width:'100%', alignItems:'center'}},
              'Динаміка власної ваги (кг)',
              React.createElement('button', {onClick:()=>{if(confirm('Видалити всю історію ваги?')){setSettings(s=>({...s, weightHistory:{}})); flash('Історію очищено');}}, style:{background:'none',border:'none',color:'var(--red)',fontSize:'12px',cursor:'pointer'}}, 'Стерти все')
            ),"""

if old_chart_header in js:
    js = js.replace(old_chart_header, new_chart_header)
else:
    print("Chart header replacement failed")

old_chart_col = """            weightChartData.map((d, i) => {
              const h = Math.max(5, Math.round(((d.weight - wBase) / (wMax - wBase + wRange*0.2)) * 100));
              return React.createElement('div', {key: i, className: 'chart-col'},"""

new_chart_col = """            weightChartData.map((d, i) => {
              const h = Math.max(5, Math.round(((d.weight - wBase) / (wMax - wBase + wRange*0.2)) * 100));
              return React.createElement('div', {key: i, className: 'chart-col', style:{cursor:'pointer'}, onClick:()=>{
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

if old_chart_col in js:
    js = js.replace(old_chart_col, new_chart_col)
else:
    print("Chart col replacement failed")

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Applied fixes")
