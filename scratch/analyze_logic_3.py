import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    text = f.read()

# Using regex to find analyzeDrops body
pattern = r'(function analyzeDrops\(sets\) \{)(.*?)(const insight = analyzeDrops\(ex\.sets\);)'

new_logic = """function analyzeDrops(sets) {
          if (sets.length < 2) return null;
          const firstWeight = sets[0].bw ? 'bw' : sets[0].weight;
          const sameWeight = sets.every(s => (s.bw ? 'bw' : s.weight) === firstWeight);
          if (!sameWeight) return null;
          
          const reps = sets.map(s => Number(s.reps) || 0);
          if (Math.max(...reps) < 8) return null;

          let maxDropPct = 0;
          let worstDropInfo = null;
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
            
            if (dropPct > maxDropPct) {
              maxDropPct = dropPct;
              worstDropInfo = { idx: i, prev: prevReps, curr: currReps, pct: pctVal, rest: restTime };
            }
          }

          if (!worstDropInfo || maxDropPct <= 0) return null;
          
          const dStr = `Динаміка: ` + dropsStrs.join(', ');

          if (maxDropPct >= 0.4) {
            if (worstDropInfo.rest > 0 && worstDropInfo.rest <= 90) {
              return { 
                color: 'var(--blue)', bg: 'rgba(59,130,246,0.1)', border: 'rgba(59,130,246,0.2)',
                pct: worstDropInfo.pct, max: worstDropInfo.prev, min: worstDropInfo.curr,
                msg: dStr,
                advice: `Очікуваний спад через короткий відпочинок (${worstDropInfo.rest}с) перед ${worstDropInfo.idx+1}-м сетом. Для сили відпочивай більше.` 
              };
            }
            return { 
              color: 'var(--red)', bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.2)',
              pct: worstDropInfo.pct, max: worstDropInfo.prev, min: worstDropInfo.curr,
              msg: dStr,
              advice: `Критичне падіння перед ${worstDropInfo.idx+1}-м сетом. Збільш відпочинок до 3-5 хв або знизь вагу.` 
            };
          } else if (maxDropPct >= 0.2) {
            return { 
              color: 'var(--orange)', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.2)',
              pct: Math.round(maxDropPct*100), max: worstDropInfo.prev, min: worstDropInfo.curr,
              msg: dStr,
              advice: 'Нормальна втома для гіпертрофії. Тримай відпочинок 2-3 хв.' 
            };
          } else {
            return { 
              color: 'var(--green)', bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.2)',
              pct: Math.round(maxDropPct*100), max: worstDropInfo.prev, min: worstDropInfo.curr,
              msg: dStr,
              advice: 'Відмінна витривалість! Можна спробувати додати вагу на наступному тренуванні.' 
            };
          }
        }
        """

match = re.search(pattern, text, re.DOTALL)
if match:
    text = text[:match.start(1)] + new_logic + match.group(3) + text[match.end(3):]
    with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
        f.write(text)
    print("Replaced logic concisely.")
else:
    print("Could not find pattern.")
