import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Define the full clean renderAnalytics function
clean_func = r"""  function renderAnalytics() {
    // Calculate total volume per day for last 10 days
    const days = Object.keys(data).sort().slice(-10);
    const chartData = days.map(d => {
      let vol = 0;
      data[d].exercises.forEach(ex => {
        ex.sets.forEach(s => {
          if (!s.bw) vol += (s.weight||0) * (s.reps||0);
        });
      });
      return { date: d, vol: vol };
    });

    const maxVol = Math.max(...chartData.map(d => d.vol), 1); // prevent div by 0

    // Weight Tracker logic
    const weightHistory = settings.weightHistory || {};
    const allWeightKeys = Object.keys(weightHistory).sort();
    const totalWPages = Math.ceil(allWeightKeys.length / 10);
    const wStart = Math.max(0, allWeightKeys.length - (weightPage + 1) * 10);
    const wEnd = allWeightKeys.length - weightPage * 10;
    const weightKeys = allWeightKeys.slice(wStart, wEnd);
    const weightChartData = weightKeys.map(k => ({ date: k, weight: bwUnit === 'lbs' ? (weightHistory[k] / 0.453592) : weightHistory[k] }));
    const wMin = weightChartData.length > 0 ? Math.min(...weightChartData.map(d => d.weight)) : 0;
    const wMax = weightChartData.length > 0 ? Math.max(...weightChartData.map(d => d.weight)) : 0;
    const wRange = (wMax - wMin) || 1;
    const wBase = Math.max(0, wMin - (wRange * 0.5));

    return React.createElement(React.Fragment, null,
      React.createElement('div', {className: 'analytics-container'},
        React.createElement('h2', {style:{display:'flex',alignItems:'center',gap:'8px',marginBottom:'16px'}}, React.createElement('div',{style:{display:'flex',alignItems:'center',marginTop:'-2px'}},React.createElement(TrendingUpIcon)), 'Аналітика'),
        
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
            React.createElement('div', {style:{display:'flex', justifyContent:'space-between', width:'100%', alignItems:'center'}},
              `Динаміка власної ваги (${bwUnit})`,
              React.createElement('button', {onClick:()=>{if(confirm('Видалити всю історію ваги?')){setSettings(s=>({...s, weightHistory:{}})); setWeightPage(0); flash('Історію очищено');}}, style:{background:'none',border:'none',color:'var(--red)',fontSize:'12px',cursor:'pointer'}}, 'Стерти все')
            ),
            React.createElement('div', {style:{display:'flex', gap:'8px', width:'100%', alignItems:'flex-end'}},
              React.createElement('button', {
                className: 'date-trigger-btn',
                style: {flex: 1, height: '36px', padding: '0 12px', fontSize: '13px', margin: 0, boxShadow: 'none'},
                onClick: () => setShowBwPicker(true)
              }, React.createElement(CalendarIcon, {size: 14, style:{marginTop:'-1px'}}), fmtShort(bwDate) + ' ▾'),
              React.createElement('div', {style:{flex:'1', display:'flex', flexDirection:'column', gap:'6px'}},
                React.createElement('div', {style:{display:'flex', gap:'4px', justifyContent:'center'}},
                  React.createElement('button', {onClick:()=>setBwUnit('кг'), style:{padding:'2px 8px', fontSize:'10px', borderRadius:'4px', fontWeight:'bold', background: bwUnit==='кг'?'rgba(16,185,129,.15)':'var(--bg3)', color: bwUnit==='кг'?'var(--green2)':'var(--text3)', border:'1px solid '+(bwUnit==='кг'?'rgba(16,185,129,.3)':'var(--border)')}}, 'кг'),
                  React.createElement('button', {onClick:()=>setBwUnit('lbs'), style:{padding:'2px 8px', fontSize:'10px', borderRadius:'4px', fontWeight:'bold', background: bwUnit==='lbs'?'rgba(16,185,129,.15)':'var(--bg3)', color: bwUnit==='lbs'?'var(--green2)':'var(--text3)', border:'1px solid '+(bwUnit==='lbs'?'rgba(16,185,129,.3)':'var(--border)')}}, 'lbs')
                ),
                React.createElement('input', {type:'number', step:'0.001', className:'set-input', style:{padding:'0', margin:0, height:'36px'}, placeholder:bwUnit==='кг'?'75.5':'165.0', value:bwValue, onChange:e=>setBwValue(e.target.value)})
              ),
              React.createElement('button', {className:'bw-toggle-btn active', style:{padding:'0 12px', margin:0, height:'36px', borderRadius:'var(--radius-xs)', background:'rgba(16,185,129,.15)', border:'1px solid rgba(16,185,129,.3)', color:'var(--green2)', fontSize:'12px', fontWeight:'700', cursor:'pointer'}, onClick:()=>{
                let val = Number(bwValue);
                if(bwDate && val > 0) {
                  if(bwUnit === 'lbs') val = val * 0.453592; // convert lbs to kg
                  setSettings(s => ({...s, weightHistory: {...(s.weightHistory||{}), [bwDate]: val}})); setWeightPage(0);
                  setBwValue('');
                  flash('Вагу збережено');
                }
              }}, 'Додати')
            )
          ),
          weightChartData.length > 0 ? React.createElement(React.Fragment, null, 
            React.createElement('div', {className: 'chart-container', style:{height:'140px', marginBottom:'8px'}},
              weightChartData.map((d, i) => {
                const h = Math.max(5, Math.round(((d.weight - wBase) / (wMax - wBase + wRange*0.2)) * 100));
                const prev = i > 0 ? weightChartData[i-1].weight : d.weight;
                const isDrop = d.weight < prev;
                const isGain = d.weight > prev;
                const barColor = isDrop ? 'linear-gradient(to top, var(--green), var(--red))' : (isGain ? 'linear-gradient(to top, var(--red), var(--green2))' : 'linear-gradient(to top, rgba(16,185,129,0.4), var(--green2))');
                const glowColor = isDrop ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)';
                const valColor = isDrop ? 'var(--red)' : (isGain ? 'var(--green2)' : 'var(--text3)');
                const displayWeight = d.weight % 1 === 0 ? d.weight : parseFloat(d.weight.toFixed(2));
                return React.createElement('div', {key: i, className: 'chart-col', style:{cursor:'pointer'}, onClick:()=>{
                  const nw = prompt(`Змінити вагу за ${fmtShort(d.date)} (${bwUnit})?\nВведіть нове значення (або залиште порожнім щоб видалити):`, d.weight % 1 === 0 ? d.weight : d.weight.toFixed(3));
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
                }},
                  React.createElement('div', {className: 'chart-value', style:{color:valColor, fontSize:'9px', top:'-18px', whiteSpace:'nowrap'}}, displayWeight),
                  React.createElement('div', {className: 'chart-bar', style: {height: '100%'}},
                    React.createElement('div', {className: 'chart-bar-fill', style: {height: h + '%', background: barColor, boxShadow: `0 0 10px ${glowColor}`}})
                  ),
                  React.createElement('div', {className: 'chart-label'}, fmtShort(d.date))
                );
              })
            ),
            allWeightKeys.length > 10 && React.createElement('div', {style:{display:'flex', justifyContent:'center', gap:'12px', marginTop:'8px'}},
              React.createElement('button', {onClick:()=>setWeightPage(p=>Math.min(p+1, totalWPages-1)), disabled: weightPage >= totalWPages-1, style:{background:'var(--bg3)', border:'1px solid var(--border)', color: weightPage >= totalWPages-1 ? 'var(--text3)' : 'var(--text1)', padding:'6px 16px', borderRadius:'20px', cursor:'pointer', display:'flex', alignItems:'center', gap:'6px', fontSize:'11px', fontWeight:'700'}}, React.createElement(ArrowLeftIcon, {size:14}), 'Назад'),
              React.createElement('button', {onClick:()=>setWeightPage(p=>Math.max(0, p-1)), disabled: weightPage === 0, style:{background:'var(--bg3)', border:'1px solid var(--border)', color: weightPage === 0 ? 'var(--text3)' : 'var(--text1)', padding:'6px 16px', borderRadius:'20px', cursor:'pointer', display:'flex', alignItems:'center', gap:'6px', fontSize:'11px', fontWeight:'700'}}, 'Вперед', React.createElement(ArrowRightIcon, {size:14}))
            )
          ) : React.createElement('div', {style:{textAlign:'center',color:'var(--text3)'}}, 'Додайте свою вагу для відображення графіка')
        )
      )
    );
  }"""

# Find and replace the whole function in app.js
start_marker = "function renderAnalytics() {"
end_marker = "function renderSettings()"

# Use regex to find the block from start_marker to just before end_marker
pattern = re.compile(re.escape(start_marker) + r".*?(?=" + re.escape(end_marker) + r")", re.DOTALL)
new_js = pattern.sub(clean_func + "\n\n  ", js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(new_js)

print("Analytics function rewritten.")
