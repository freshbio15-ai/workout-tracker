import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    text = f.read()

old_logic = """        function analyzeDrops(sets) {
          if (sets.length < 2) return null;
          const firstWeight = sets[0].bw ? 'bw' : sets[0].weight;
          const sameWeight = sets.every(s => (s.bw ? 'bw' : s.weight) === firstWeight);
          if (!sameWeight) return null;
          
          const reps = sets.map(s => Number(s.reps) || 0);
          if (Math.max(...reps) < 8) return null;

          let maxDropPct = 0;
          let worstDropInfo = null;
          let hasNormalDrop = false;

          for (let i = 1; i < sets.length; i++) {
            const prevReps = reps[i-1];
            const currReps = reps[i];
            if (prevReps === 0) continue;
            const dropPct = (prevReps - currReps) / prevReps;
            const restTime = Number(sets[i].rest) || 0;
            
            if (dropPct >= 0.2 && dropPct < 0.4) hasNormalDrop = true;
            
            if (dropPct > maxDropPct) {
              maxDropPct = dropPct;
              worstDropInfo = { idx: i, prev: prevReps, curr: currReps, pct: Math.round(dropPct*100), rest: restTime };
            }
          }

          if (!worstDropInfo || maxDropPct <= 0) return null;

          if (maxDropPct >= 0.4) {
            let msg = `Аномальне падіння між ${worstDropInfo.idx} і ${worstDropInfo.idx+1} підходом на ${worstDropInfo.pct}% (з ${worstDropInfo.prev} до ${worstDropInfo.curr})`;
            if (worstDropInfo.rest > 0) msg += ` в контексті відпочинку ${worstDropInfo.rest}с.`;
            else msg += `.`;
            
            if (hasNormalDrop) {
              msg += ` Між іншими підходами падіння в межах норми.`;
            }
            
            return { 
              color: 'var(--red)', bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.2)',
              pct: worstDropInfo.pct, max: worstDropInfo.prev, min: worstDropInfo.curr,
              msg: msg,
              advice: 'Спробуй збільшити відпочинок перед цим підходом або зменшити вагу, якщо це стається регулярно.' 
            };
          } else if (maxDropPct >= 0.2) {
            return { 
              color: 'var(--orange)', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.2)',
              pct: Math.round(maxDropPct*100), max: worstDropInfo.prev, min: worstDropInfo.curr,
              msg: `Загальна динаміка в нормі. Максимальне падіння склало ${Math.round(maxDropPct*100)}% між ${worstDropInfo.idx} і ${worstDropInfo.idx+1} підходом.`,
              advice: 'Нормальна втома для гіпертрофії. Для збереження об\\'єму дотримуйся режиму відпочинку 2-3 хв.' 
            };
          } else {
            return { 
              color: 'var(--green)', bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.2)',
              pct: Math.round(maxDropPct*100), max: worstDropInfo.prev, min: worstDropInfo.curr,
              msg: `Відмінна витривалість! Падіння між підходами мінімальне (до ${Math.round(maxDropPct*100)}%).`,
              advice: 'Ти добре відновлюєшся між сетами. Можеш спробувати збільшити робочу вагу.' 
            };
          }
        }"""

new_logic = """        function analyzeDrops(sets) {
          if (sets.length < 2) return null;
          const firstWeight = sets[0].bw ? 'bw' : sets[0].weight;
          const sameWeight = sets.every(s => (s.bw ? 'bw' : s.weight) === firstWeight);
          if (!sameWeight) return null;
          
          const reps = sets.map(s => Number(s.reps) || 0);
          if (Math.max(...reps) < 8) return null;

          let maxDropPct = 0;
          let worstDropInfo = null;
          let hasNormalDrop = false;
          let dropsStrs = [];

          for (let i = 1; i < sets.length; i++) {
            const prevReps = reps[i-1];
            const currReps = reps[i];
            if (prevReps === 0) continue;
            const dropPct = (prevReps - currReps) / prevReps;
            const restTime = Number(sets[i].rest) || 0;
            
            const pctVal = Math.round(dropPct * 100);
            if (pctVal > 0) dropsStrs.push(`${prevReps}→${currReps} (-${pctVal}%)`);
            else dropsStrs.push(`${prevReps}→${currReps}`);
            
            if (dropPct >= 0.2 && dropPct < 0.4) hasNormalDrop = true;
            
            if (dropPct > maxDropPct) {
              maxDropPct = dropPct;
              worstDropInfo = { idx: i, prev: prevReps, curr: currReps, pct: pctVal, rest: restTime };
            }
          }

          if (!worstDropInfo || maxDropPct <= 0) return null;
          
          const dStr = dropsStrs.join(', ');

          if (maxDropPct >= 0.4) {
            let msg = `Динаміка: ${dStr}. Аномальне падіння між ${worstDropInfo.idx} і ${worstDropInfo.idx+1} підходом на ${worstDropInfo.pct}%`;
            if (worstDropInfo.rest > 0) msg += ` (відпочинок ${worstDropInfo.rest}с).`;
            else msg += `.`;
            
            if (hasNormalDrop) {
              msg += ` Інші підходи в нормі.`;
            }
            
            return { 
              color: 'var(--red)', bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.2)',
              pct: worstDropInfo.pct, max: worstDropInfo.prev, min: worstDropInfo.curr,
              msg: msg,
              advice: 'Спробуй збільшити відпочинок перед цим підходом або зменшити вагу, якщо це стається регулярно.' 
            };
          } else if (maxDropPct >= 0.2) {
            return { 
              color: 'var(--orange)', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.2)',
              pct: Math.round(maxDropPct*100), max: worstDropInfo.prev, min: worstDropInfo.curr,
              msg: `Динаміка: ${dStr}. Всі падіння в межах норми (до ${Math.round(maxDropPct*100)}%).`,
              advice: 'Нормальна втома для гіпертрофії. Для збереження об\\'єму дотримуйся режиму відпочинку 2-3 хв.' 
            };
          } else {
            return { 
              color: 'var(--green)', bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.2)',
              pct: Math.round(maxDropPct*100), max: worstDropInfo.prev, min: worstDropInfo.curr,
              msg: `Динаміка: ${dStr}. Відмінна витривалість, падіння мінімальне (до ${Math.round(maxDropPct*100)}%).`,
              advice: 'Ти добре відновлюєшся між сетами. Можеш спробувати збільшити робочу вагу.' 
            };
          }
        }"""

if old_logic in text:
    text = text.replace(old_logic, new_logic)
    with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
        f.write(text)
    print("Logic successfully updated.")
else:
    print("Could not find old logic.")
