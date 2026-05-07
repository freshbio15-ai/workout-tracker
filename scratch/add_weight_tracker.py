import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    text = f.read()

# 1. Add state variables
old_state = "  const [pickerEnd,setPickerEnd]=useState('');\n  const [uid,setUid]=useState(null);"
new_state = "  const [pickerEnd,setPickerEnd]=useState('');\n  const [bwDate,setBwDate]=useState(todayKey());\n  const [bwValue,setBwValue]=useState('');\n  const [uid,setUid]=useState(null);"
if old_state in text:
    text = text.replace(old_state, new_state)
    print("State variables added.")
else:
    print("Could not find state variables location.")

# 2. Modify renderAnalytics
old_render = """    const maxVol = Math.max(...chartData.map(d => d.vol), 1); // prevent div by 0

    return React.createElement(React.Fragment, null,
      React.createElement('div', {className: 'analytics-container'},
        React.createElement('h2', {style:{display:'flex',alignItems:'center',gap:'8px',marginBottom:'16px'}}, React.createElement(TrendingUpIcon), 'Аналітика'),
        
        React.createElement('div', {className: 'chart-wrapper'},
          React.createElement('div', {className: 'chart-title'}, 'Тоннаж за останні 10 тренувань (кг)'),
          chartData.length > 0 ? React.createElement('div', {className: 'chart-container'},
            chartData.map((d, i) => {
              const h = Math.round((d.vol / maxVol) * 100);
              return React.createElement('div', {key: i, className: 'chart-col'},
                React.createElement('div', {className: 'chart-value'}, d.vol > 0 ? d.vol : ''),
                React.createElement('div', {className: 'chart-bar', style: {height: '100%'}},
                  React.createElement('div', {className: 'chart-bar-fill', style: {height: h + '%'}})
                ),
                React.createElement('div', {className: 'chart-label'}, fmtShort(d.date))
              );
            })
          ) : React.createElement('div', {style:{textAlign:'center',color:'var(--text3)'}}, 'Немає даних')
        )
      )
    );"""

new_render = """    const maxVol = Math.max(...chartData.map(d => d.vol), 1); // prevent div by 0

    // Weight Tracker logic
    const weightHistory = settings.weightHistory || {};
    const weightKeys = Object.keys(weightHistory).sort().slice(-15);
    const weightChartData = weightKeys.map(k => ({ date: k, weight: weightHistory[k] }));
    const wMin = weightChartData.length > 0 ? Math.min(...weightChartData.map(d => d.weight)) : 0;
    const wMax = weightChartData.length > 0 ? Math.max(...weightChartData.map(d => d.weight)) : 0;
    const wRange = (wMax - wMin) || 1;
    const wBase = Math.max(0, wMin - (wRange * 0.5));

    return React.createElement(React.Fragment, null,
      React.createElement('div', {className: 'analytics-container'},
        React.createElement('h2', {style:{display:'flex',alignItems:'center',gap:'8px',marginBottom:'16px'}}, React.createElement(TrendingUpIcon), 'Аналітика'),
        
        React.createElement('div', {className: 'chart-wrapper'},
          React.createElement('div', {className: 'chart-title'}, 'Тоннаж за останні 10 тренувань (кг)'),
          chartData.length > 0 ? React.createElement('div', {className: 'chart-container'},
            chartData.map((d, i) => {
              const h = Math.round((d.vol / maxVol) * 100);
              return React.createElement('div', {key: i, className: 'chart-col'},
                React.createElement('div', {className: 'chart-value'}, d.vol > 0 ? d.vol : ''),
                React.createElement('div', {className: 'chart-bar', style: {height: '100%'}},
                  React.createElement('div', {className: 'chart-bar-fill', style: {height: h + '%'}})
                ),
                React.createElement('div', {className: 'chart-label'}, fmtShort(d.date))
              );
            })
          ) : React.createElement('div', {style:{textAlign:'center',color:'var(--text3)'}}, 'Немає даних')
        ),

        // Weight tracker section
        React.createElement('div', {className: 'chart-wrapper', style:{marginTop:'24px'}},
          React.createElement('div', {className: 'chart-title', style:{display:'flex',justifyContent:'space-between',alignItems:'center', flexWrap:'wrap', gap:'12px', paddingBottom:'12px'}}, 
            'Динаміка власної ваги (кг)',
            React.createElement('div', {style:{display:'flex', gap:'8px', width:'100%'}},
              React.createElement('input', {type:'date', className:'set-input', style:{flex:'1', padding:'6px', margin:0}, value:bwDate, onChange:e=>setBwDate(e.target.value)}),
              React.createElement('input', {type:'number', step:'0.001', className:'set-input', style:{flex:'1', padding:'6px', margin:0}, placeholder:'75.5', value:bwValue, onChange:e=>setBwValue(e.target.value)}),
              React.createElement('button', {className:'bw-toggle-btn active', style:{padding:'0 12px', margin:0, borderRadius:'var(--radius-xs)', background:'rgba(16,185,129,.15)', border:'1px solid rgba(16,185,129,.3)', color:'var(--green2)', fontSize:'12px', fontWeight:'700', cursor:'pointer'}, onClick:()=>{
                if(bwDate && bwValue) {
                  setSettings(s => ({...s, weightHistory: {...(s.weightHistory||{}), [bwDate]: Number(bwValue)}}));
                  setBwValue('');
                  flash('Вагу збережено');
                }
              }}, 'Додати')
            )
          ),
          weightChartData.length > 0 ? React.createElement('div', {className: 'chart-container', style:{height:'140px'}},
            weightChartData.map((d, i) => {
              const h = Math.max(5, Math.round(((d.weight - wBase) / (wMax - wBase + wRange*0.2)) * 100));
              return React.createElement('div', {key: i, className: 'chart-col'},
                React.createElement('div', {className: 'chart-value', style:{color:'var(--green2)'}}, d.weight % 1 === 0 ? d.weight : d.weight.toFixed(3)),
                React.createElement('div', {className: 'chart-bar', style: {height: '100%'}},
                  React.createElement('div', {className: 'chart-bar-fill', style: {height: h + '%', background:'linear-gradient(to top, var(--green), var(--green2))', boxShadow:'0 0 10px rgba(16,185,129,0.3)'}})
                ),
                React.createElement('div', {className: 'chart-label'}, fmtShort(d.date))
              );
            })
          ) : React.createElement('div', {style:{textAlign:'center',color:'var(--text3)'}}, 'Додайте свою вагу для відображення графіка')
        )
      )
    );"""

if old_render in text:
    text = text.replace(old_render, new_render)
    print("Render replaced successfully.")
else:
    print("Could not find render function content.")
    
with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(text)

