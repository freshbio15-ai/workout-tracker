import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. We need to add the Rehab Progress Bar rendering function/logic
# I'll add a helper function `renderRehabProgress()` near `renderCalendar` or inside `App`.
# And we need the Quick Switch logic.

# First, modify the header block (lines ~1044-1058)
header_pattern = r"React\.createElement\('div',\{className:'app-header'\},[\s\S]*?React\.createElement\('div',\{className:'cloud-status'\},[\s\S]*?\)[\s]*?\),"

new_header = r"""React.createElement('div',{className:'app-header'},
        React.createElement('div',{className:'app-logo'},
          React.createElement('div',{className:'logo-icon', onClick:()=>setShowEasterEgg(true), style:{cursor:'pointer'}},React.createElement(ActivityIcon, {size: 20})),
          React.createElement('div',{className:'logo-text'},
            React.createElement('h1',null,'Gym Notebook'),
            React.createElement('p',null,'Твій щоденник тренувань')
          )
        ),
        React.createElement('div',{style:{display:'flex', alignItems:'center', gap:'8px'}},
          React.createElement('button', {
            onClick: () => {
              if (settings.rehab?.active) {
                setSettings(s => ({...s, rehab: {...s.rehab, active: false}}));
              } else {
                const date = prompt("Введіть дату початку реабілітації (YYYY-MM-DD):", settings.rehab?.startDate || new Date().toISOString().split('T')[0]);
                if (date !== null) {
                  setSettings(s => ({...s, rehab: {active: true, startDate: date}}));
                }
              }
            },
            style: {
              background: settings.rehab?.active ? 'rgba(45, 212, 191, 0.15)' : 'var(--bg3)',
              border: '1px solid ' + (settings.rehab?.active ? 'rgba(45, 212, 191, 0.3)' : 'var(--border)'),
              borderRadius: '20px', padding: '4px 8px', fontSize: '14px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.2s'
            },
            title: settings.rehab?.active ? 'Режим Реабілітації (Увімкнено)' : 'Нормальний режим'
          }, settings.rehab?.active ? '🛡️' : '💪'),
          React.createElement('div',{className:'cloud-status'},
            React.createElement('span',{className:'cloud-dot '+(cloudStatus==='synced'?'green':cloudStatus==='saving'?'yellow':'gray')}),
            React.createElement('span',{className:'cloud-text'},
              cloudStatus==='synced'?React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'4px'}}, React.createElement(CheckCircleIcon), 'Синхр.'):cloudStatus==='saving'?React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'4px'}}, React.createElement(RefreshIcon), 'Зберіг...'):cloudStatus==='connecting'?React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'4px'}}, React.createElement(WifiIcon), 'З\'єдн...'):React.createElement('div', {style:{display:'flex',alignItems:'center',gap:'4px'}}, React.createElement(WifiOffIcon), 'Офлайн')
            )
          )
        )
      ),
      // Rehab Progress Bar
      settings.rehab?.active && (function(){
        if (!settings.rehab.startDate) return null;
        const start = new Date(settings.rehab.startDate);
        const now = new Date();
        const diffTime = Math.abs(now - start);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        const maxDays = 240;
        const currentDays = Math.min(diffDays, maxDays);
        const progress = (currentDays / maxDays) * 100;
        
        if (currentDays >= maxDays) {
          return React.createElement('div', {className: 'rehab-success-banner'},
            React.createElement('div', {className: 'rehab-success-text'}, 'Вітаю, друже! 🎉\\nТи пройшов шлях відновлення.\\nЧас повертатися до великих ваг! 🚀')
          );
        }
        
        return React.createElement('div', {className: 'rehab-progress-wrapper'},
          React.createElement('div', {className: 'rehab-progress-header'},
            React.createElement('span', {className: 'rehab-progress-title'}, '🛡️ Етап одужання'),
            React.createElement('span', {className: 'rehab-progress-text'}, `День ${currentDays} / ${maxDays}`)
          ),
          React.createElement('div', {className: 'rehab-progress-bar-bg'},
            React.createElement('div', {className: 'rehab-progress-bar-fill', style: {width: progress + '%'}})
          ),
          React.createElement('div', {style: {display: 'flex', justifyContent: 'space-between', fontSize: '9px', color: 'var(--text3)', marginTop: '2px'}},
            React.createElement('span', null, settings.rehab.startDate),
            React.createElement('span', {style: {cursor: 'pointer', textDecoration: 'underline'}, onClick: () => {
              const nd = prompt('Змінити дату (DEBUG):', settings.rehab.startDate);
              if (nd) setSettings(s => ({...s, rehab: {...s.rehab, startDate: nd}}));
            }}, 'Змінити день (Debug)'),
            React.createElement('span', null, 'Фініш')
          )
        );
      })(),"""

js = re.sub(header_pattern, new_header, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Header and progress bar added.")
