import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Replace the word "Історія" with "Щоденник" in the tab bar
js = js.replace("React.createElement('span',null,'Історія')", "React.createElement('span',null,'Щоденник')")

# 2. Redefine renderHistory
new_render_history = r"""  function renderHistory(){
    if(historyDetail) return renderHistoryDetail();
    
    let filterText = 'За весь час';
    if(filterStart === 'last') filterText = 'Last';
    else if(filterStart === 'all') filterText = 'За весь час';
    else if(filterStart && filterEnd) {
      if(filterStart === filterEnd) filterText = fmtShort(filterStart);
      else filterText = fmtShort(filterStart) + ' - ' + fmtShort(filterEnd);
    } else if(filterStart) filterText = 'З ' + fmtShort(filterStart);
    else if(filterEnd) filterText = 'До ' + fmtShort(filterEnd);

    // Calculate max muscle tonnage for progress bars
    const maxMuscleTonnage = muscleStats.length > 0 ? Math.max(...muscleStats.map(s => s[1].tonnage)) : 1;

    return React.createElement(React.Fragment,null,
      React.createElement('div',{className:'history-header'},
        React.createElement('h2',{style:{display:'flex',alignItems:'center',gap:'8px'}},React.createElement('div',{style:{display:'flex',alignItems:'center',marginTop:'-2px'}},React.createElement(HistoryIcon)),'Щоденник'),
        React.createElement('button', {
          className: 'date-trigger-btn',
          style: {padding: '8px 16px', fontSize: '13px'},
          onClick: () => {
            setPickerStart(actualStart); setPickerEnd(actualEnd);
            setPickerYear(actualStart ? parseInt(actualStart.split('-')[0]) : new Date().getFullYear());
            setPickerMonth(actualStart ? parseInt(actualStart.split('-')[1])-1 : new Date().getMonth());
            setShowPicker(true);
          }
        }, React.createElement(CalendarIcon, {size: 14, style:{marginTop:'-1px'}}), filterText + ' ▾')
      ),
      
      // Dashboard Card
      React.createElement('div',{className:'tonnage-card'},
        React.createElement('div',{className:'tonnage-value'},(totalTonnage/1000).toFixed(1)+'т'),
        React.createElement('div',{className:'tonnage-label'},'Загальний тоннаж'),
        React.createElement('div',{className:'tonnage-row'},
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},totalDays),React.createElement('div',{className:'tonnage-item-lbl'},'ТРЕНУВАНЬ')),
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},totalSets),React.createElement('div',{className:'tonnage-item-lbl'},'ПІДХОДІВ')),
          React.createElement('div',{className:'tonnage-item'},React.createElement('div',{className:'tonnage-item-val'},thisWeek),React.createElement('div',{className:'tonnage-item-lbl'},'ЦЕЙ ТИЖД.'))
        )
      ),
      
      history.length===0
        ?React.createElement('div',{className:'empty-state'},React.createElement('div',{className:'e-icon'},React.createElement(BookIcon)),React.createElement('h3',null,'Поки пусто'),React.createElement('p',null,'Записуй тренування в календарі'))
        :React.createElement(React.Fragment,null,
          
          // Muscle Activity Bars
          muscleStats.length>0&&React.createElement(React.Fragment,null,
            React.createElement('div',{className:'section-label'},'Активність м\'язів'),
            React.createElement('div',{className:'muscle-tonnage-list'},
              muscleStats.map(([key,stat])=>{
                const t = stat.tonnage;
                const pct = Math.max(5, Math.round((t / maxMuscleTonnage) * 100)); // min 5% for visibility
                return React.createElement('div',{key:key,className:'mt-row'},
                  React.createElement('div',{className:'mt-emoji'},React.createElement('img',{src:stat.icon, alt:stat.label})),
                  React.createElement('div',{className:'mt-bar-container'},
                    React.createElement('div',{className:'mt-bar-header'},
                      React.createElement('span',{className:'mt-name'},stat.label),
                      React.createElement('span',{className:'mt-tonnage'},t>1000?(t/1000).toFixed(1)+' т':t+' кг')
                    ),
                    React.createElement('div',{className:'mt-bar-bg'},
                      React.createElement('div',{className:'mt-bar-fill', style:{width: pct + '%'}})
                    )
                  )
                );
              })
            )
          ),
          
          // Workout Feed
          React.createElement('div',{className:'section-label'},'Всі тренування ('+history.length+')'),
          React.createElement('div',{className:'history-list'},history.map(([k,w])=>{
            const ton = calcTonnage(w);
            const totalEx = w.exercises.length;
            const totalSets = w.exercises.reduce((a,e)=>a+e.sets.length,0);
            return React.createElement('div',{key:k,className:'history-card',onClick:()=>setHistoryDetail(k)},
              React.createElement('div',{className:'hc-top'},
                React.createElement('div',null,
                  React.createElement('div',{className:'hc-title'},k===tKey?'Сьогодні':fmtFull(k)),
                  React.createElement('div',{className:'hc-date'},k)
                ),
                w.muscle&&React.createElement('span',{className:'hc-muscle'},w.muscle)
              ),
              React.createElement('div',{className:'hc-stats'},
                React.createElement('span',{className:'hc-stat'}, React.createElement(ActivityIcon, {size:12, className:'hc-stat-icon'}), React.createElement('strong',null,totalEx),'вправ'),
                React.createElement('span',{className:'hc-stat'}, React.createElement(RefreshIcon, {size:12, className:'hc-stat-icon'}), React.createElement('strong',null,totalSets),'підх.'),
                React.createElement('span',{className:'hc-stat'}, React.createElement(WeightIcon, {size:12, className:'hc-stat-icon'}), React.createElement('strong',null,ton>1000?(ton/1000).toFixed(1)+'т':ton+'кг'))
              ),
              React.createElement('div',{className:'hc-exercises'},w.exercises.map((ex,i)=>{
                const et = calcExTonnage(ex);
                const mg = MUSCLES.find(e=>e.id===(ex.muscle||''));
                return React.createElement('div',{key:i,className:'hc-ex'},
                  React.createElement('div',{className:'hc-ex-left'},
                    mg&&React.createElement('img',{src:mg.icon, style:{width:'14px',height:'14px'}}),
                    ex.name + (ex.sets[0]&&ex.sets[0].bw?' (СВ)':'')
                  ),
                  React.createElement('div',{className:'hc-ex-right'},
                    `${ex.sets.length} підх. · ${et>1000?(et/1000).toFixed(1)+'т':et+'кг'}`
                  )
                );
              }))
            );
          }))
        )
    );
  }"""

start_marker = "function renderHistory(){"
end_marker = "function renderHistoryDetail(){"

pattern = re.compile(re.escape(start_marker) + r"[\s\S]*?(?=" + re.escape(end_marker) + ")")
js = pattern.sub(new_render_history + "\n\n  ", js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("renderHistory updated.")
