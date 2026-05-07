import re

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

new_css = """
/* ===== ANALYTICS TAB ===== */
.analytics-container{padding-bottom:100px}
.chart-wrapper{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:20px 16px;margin-top:16px}
.chart-title{font-size:16px;font-weight:700;margin-bottom:24px;text-align:center;color:var(--text1)}
.chart-container{display:flex;align-items:flex-end;justify-content:space-between;height:180px;gap:8px;padding-top:20px}
.chart-col{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%;position:relative;}
.chart-bar{width:100%;max-width:30px;background:rgba(255,255,255,0.05);border-radius:6px 6px 0 0;position:relative;display:flex;align-items:flex-end;transition:height 0.5s ease;overflow:hidden}
.chart-bar-fill{width:100%;background:linear-gradient(180deg,var(--accent),#6d28d9);border-radius:6px 6px 0 0;box-shadow:0 0 10px rgba(124,58,237,0.4);transition:height 0.5s ease}
.chart-value{position:absolute;top:-22px;font-size:11px;font-weight:700;color:var(--text2);opacity:0.6;transition:opacity 0.2s}
.chart-col:hover .chart-value{opacity:1;color:var(--accent2)}
.chart-label{font-size:10px;color:var(--text3);margin-top:8px;font-weight:600;text-align:center}

/* ===== TEMPLATES ===== */
.template-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px;margin-top:20px}
.template-card{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:16px;cursor:pointer;transition:all 0.2s;backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);position:relative;overflow:hidden}
.template-card:hover{background:rgba(255,255,255,0.06);border-color:rgba(124,58,237,0.3);transform:translateY(-2px)}
.template-card::before{content:'';position:absolute;top:0;left:0;width:100%;height:4px;background:linear-gradient(90deg,var(--accent),#10b981)}
.template-title{font-size:15px;font-weight:700;color:var(--text1);margin-bottom:4px}
.template-muscle{font-size:12px;color:var(--text3);font-weight:600}
.template-ex-count{font-size:11px;color:var(--accent2);margin-top:8px;font-weight:700}

/* ===== PR BADGE ===== */
@keyframes pulse-glow{
  0%{box-shadow:0 0 4px rgba(16,185,129,0.4)}
  50%{box-shadow:0 0 12px rgba(16,185,129,0.8)}
  100%{box-shadow:0 0 4px rgba(16,185,129,0.4)}
}
.pr-badge{display:inline-flex;align-items:center;justify-content:center;background:rgba(16,185,129,0.15);color:#10b981;font-size:10px;font-weight:800;padding:2px 6px;border-radius:10px;border:1px solid rgba(16,185,129,0.3);margin-left:6px;animation:pulse-glow 2s infinite;text-shadow:0 0 4px rgba(16,185,129,0.3)}
"""

if "/* ===== ANALYTICS TAB ===== */" not in css:
    css += "\n" + new_css
    with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
        f.write(css)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    text = f.read()

# 1. Add TrendingUpIcon
trending_up_svg = "const TrendingUpIcon = ({size=24, className=''}) => React.createElement('svg', {width: size, height: size, className, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round'}, React.createElement('polyline', {points: '23 6 13.5 15.5 8.5 10.5 1 18'}), React.createElement('polyline', {points: '17 6 23 6 23 12'}));\n"

if "TrendingUpIcon" not in text:
    text = text.replace("const ActivityIcon", trending_up_svg + "const ActivityIcon")

# 2. Add renderAnalytics
render_analytics_code = """
  function renderAnalytics() {
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
    );
  }
"""
if "function renderAnalytics()" not in text:
    text = text.replace("function renderSettings()", render_analytics_code + "\n  function renderSettings()")

# 3. Modify render tree for analytics
if "tab==='analytics'&&renderAnalytics()" not in text:
    text = text.replace("tab==='settings'&&renderSettings()", "tab==='settings'&&renderSettings(),\n      tab==='analytics'&&renderAnalytics()")

# 4. Modify tab-bar to include 4th tab
if "setTab('analytics')" not in text:
    old_tab_bar_inner = """React.createElement('div',{className:'tab-bar-inner'},
        React.createElement('button',{className:'tab-btn'+(tab==='calendar'?' active':''),onClick:()=>setTab('calendar')},
          React.createElement('span',{className:'tab-icon'},React.createElement(CalendarIcon)),React.createElement('span',null,'Календар')
        ),
        React.createElement('button',{className:'tab-btn'+(tab==='history'?' active':''),onClick:()=>setTab('history')},
          React.createElement('span',{className:'tab-icon'},React.createElement(HistoryIcon)),React.createElement('span',null,'Історія')
        ),
        React.createElement('button',{className:'tab-btn'+(tab==='settings'?' active':''),onClick:()=>setTab('settings')},
          React.createElement('span',{className:'tab-icon'},React.createElement(SettingsIcon)),React.createElement('span',null,'Налаштування')
        )
      )"""
    new_tab_bar_inner = """React.createElement('div',{className:'tab-bar-inner'},
        React.createElement('button',{className:'tab-btn'+(tab==='calendar'?' active':''),onClick:()=>setTab('calendar')},
          React.createElement('span',{className:'tab-icon'},React.createElement(CalendarIcon)),React.createElement('span',null,'Календар')
        ),
        React.createElement('button',{className:'tab-btn'+(tab==='history'?' active':''),onClick:()=>setTab('history')},
          React.createElement('span',{className:'tab-icon'},React.createElement(HistoryIcon)),React.createElement('span',null,'Історія')
        ),
        React.createElement('button',{className:'tab-btn'+(tab==='analytics'?' active':''),onClick:()=>setTab('analytics')},
          React.createElement('span',{className:'tab-icon'},React.createElement(TrendingUpIcon)),React.createElement('span',null,'Аналітика')
        ),
        React.createElement('button',{className:'tab-btn'+(tab==='settings'?' active':''),onClick:()=>setTab('settings')},
          React.createElement('span',{className:'tab-icon'},React.createElement(SettingsIcon)),React.createElement('span',null,'Налаштування')
        )
      )"""
    text = text.replace(old_tab_bar_inner, new_tab_bar_inner)

# 5. Templates Logic
template_save_btn = """React.createElement('button',{className:'save-btn',style:{marginTop:'8px',background:'var(--bg3)',color:'var(--text1)'},onClick:()=>{
              const tName = prompt('Введіть назву шаблону:');
              if(tName){
                const tpls = settings.templates || [];
                setSettings({...settings, templates: [...tpls, {id: Date.now().toString(), name: tName, muscle: draft.muscle, exercises: draft.exercises}]});
                flash('Шаблон збережено');
              }
            }},'Зберегти як шаблон')"""

if "Зберегти як шаблон" not in text:
    old_save_btn = """React.createElement('button',{className:'save-btn',onClick:saveDay},hasData?React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'8px'}}, React.createElement(SaveIcon), 'Оновити'):React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'8px'}}, React.createElement(CheckIcon), 'Зберегти тренування')),"""
    new_save_btn = old_save_btn + "\n            " + template_save_btn + ","
    text = text.replace(old_save_btn, new_save_btn)

templates_list_ui = """
          !hasData && (settings.templates && settings.templates.length > 0) && React.createElement('div', {style:{marginTop:'24px', width:'100%'}},
            React.createElement('h3', {style:{fontSize:'16px',fontWeight:'700',color:'var(--text1)',marginBottom:'12px'}}, 'Або виберіть шаблон:'),
            React.createElement('div', {className:'template-grid'},
              settings.templates.map(tpl => React.createElement('div', {
                key: tpl.id, 
                className:'template-card',
                onClick: () => {
                  setDraft({muscle: tpl.muscle, exercises: JSON.parse(JSON.stringify(tpl.exercises))});
                }
              },
                React.createElement('div', {className:'template-title'}, tpl.name),
                React.createElement('div', {className:'template-muscle'}, tpl.muscle || 'Різне'),
                React.createElement('div', {className:'template-ex-count'}, tpl.exercises.length + ' вправ')
              ))
            )
          ),
"""

if "Або виберіть шаблон:" not in text:
    old_day_body = """React.createElement('div',{className:'day-panel-body'},
          !hasData&&React.createElement('div',{className:'dp-empty'},"""
    new_day_body = """React.createElement('div',{className:'day-panel-body'},
          !hasData&&React.createElement('div',{className:'dp-empty'},""" + templates_list_ui
    text = text.replace(old_day_body, new_day_body)

# 6. Personal Records logic
check_pr_fn = """
  // Check if a given weight is a PR for an exercise up to a certain date
  const checkPR = useCallback((exName, currentWeight, dateKey) => {
    if(!exName || !currentWeight || currentWeight <= 0) return false;
    let isPR = true;
    let hasPrevious = false;
    for(let d in data) {
      if(d < dateKey) {
        data[d].exercises.forEach(ex => {
          if(ex.name.toLowerCase().trim() === exName.toLowerCase().trim()) {
            ex.sets.forEach(s => {
              if(!s.bw && s.weight >= currentWeight) isPR = false;
              if(!s.bw && s.weight > 0) hasPrevious = true;
            });
          }
        });
      }
    }
    return isPR && hasPrevious; // Only highlight if it beats previous records (and there were previous records)
  }, [data]);
"""

if "const checkPR" not in text:
    text = text.replace("function App(){", "function App(){\n" + check_pr_fn)

pr_badge_editor = """
                      // PR Logic inside Day Editor
                      const isPR = !s.bw && s.weight && checkPR(e.name, Number(s.weight), selected);
                      const prBadge = isPR ? React.createElement('span', {className:'pr-badge'}, 'PR 🏆') : null;
"""

if "PR 🏆" not in text:
    old_set_header = "React.createElement('div',{className:'set-header'},React.createElement('strong',null,'Підхід '+(j+1)),"
    new_set_header = pr_badge_editor + "\n                      " + "React.createElement('div',{className:'set-header'},React.createElement('strong',null,'Підхід '+(j+1), prBadge),"
    text = text.replace(old_set_header, new_set_header)
    
    old_h_set_header = """return React.createElement('div',{key:j,className:'h-set-row'},
                      React.createElement('div',{className:'h-set-num'},'Підхід '+(j+1)),"""
    new_h_set_header = """const isPR = !s.bw && s.weight && checkPR(e.name, Number(s.weight), k);
                    const prBadge = isPR ? React.createElement('span', {className:'pr-badge'}, 'PR 🏆') : null;
                    return React.createElement('div',{key:j,className:'h-set-row'},
                      React.createElement('div',{className:'h-set-num'},'Підхід '+(j+1), prBadge),"""
    text = text.replace(old_h_set_header, new_h_set_header)


with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(text)

print("Features added successfully")
