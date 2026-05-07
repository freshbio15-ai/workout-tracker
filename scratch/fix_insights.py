import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    text = f.read()

# 1. Update startTimer
old_timer = """  function startTimer(sec) {
    setTimerEnd(Date.now() + sec * 1000);
    setTimeLeft(sec);
    setShowTimerPopup(false);
  }"""

new_timer = """  function startTimer(sec) {
    setTimerEnd(Date.now() + sec * 1000);
    setTimeLeft(sec);
    setShowTimerPopup(false);
    
    setDraft(p => {
      if(!p) return p;
      const d = JSON.parse(JSON.stringify(p));
      let found = false;
      for (let i = d.exercises.length - 1; i >= 0; i--) {
        const ex = d.exercises[i];
        for (let j = ex.sets.length - 1; j >= 0; j--) {
          if (ex.sets[j].reps !== '') {
            ex.sets[j].rest = sec;
            found = true;
            break;
          }
        }
        if(found) break;
      }
      return d;
    });
  }"""

text = text.replace(old_timer, new_timer)

# 2. Update analyzeDrops
old_analyze = """        function analyzeDrops(sets) {
          if (sets.length < 2) return null;
          const firstWeight = sets[0].bw ? 'bw' : sets[0].weight;
          const sameWeight = sets.every(s => (s.bw ? 'bw' : s.weight) === firstWeight);
          if (!sameWeight) return null;
          
          const reps = sets.map(s => Number(s.reps) || 0);
          const maxReps = Math.max(...reps);
          if (maxReps < 8) return null;
          
          const minReps = Math.min(...reps);
          const dropPct = (maxReps - minReps) / maxReps;

          if (dropPct >= 0.4) {
            return { 
              color: 'var(--red)', bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.2)',
              pct: Math.round(dropPct*100), max: maxReps, min: minReps,
              msg: `М'язи не встигають відновлювати АТФ.`,
              advice: 'Збільш час відпочинку до 3-5 хвилин для підтримки високої інтенсивності.' 
            };
          } else if (dropPct >= 0.2) {
            return { 
              color: 'var(--orange)', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.2)',
              pct: Math.round(dropPct*100), max: maxReps, min: minReps,
              msg: `Нормальна втома для гіпертрофії.`,
              advice: 'Для збереження об\'єму спробуй відпочивати 2-3 хвилини.' 
            };
          }
          return null;
        }"""

new_analyze = """        function analyzeDrops(sets) {
          if (sets.length < 2) return null;
          const firstWeight = sets[0].bw ? 'bw' : sets[0].weight;
          const sameWeight = sets.every(s => (s.bw ? 'bw' : s.weight) === firstWeight);
          if (!sameWeight) return null;
          
          const reps = sets.map(s => Number(s.reps) || 0);
          if (Math.max(...reps) < 8) return null;
          
          // Check drop between consecutive sets
          for (let i = 1; i < sets.length; i++) {
            const prevReps = reps[i-1];
            const currReps = reps[i];
            const dropPct = (prevReps - currReps) / prevReps;
            const restTime = sets[i-1].rest || 0;
            
            if (dropPct >= 0.4) {
              if (restTime > 0 && restTime < 120) {
                return { 
                  color: 'var(--blue)', bg: 'rgba(59,130,246,0.1)', border: 'rgba(59,130,246,0.2)',
                  pct: Math.round(dropPct*100), max: prevReps, min: currReps,
                  msg: `Повторення впали через короткий відпочинок (${Math.round(restTime/60)} хв).`,
                  advice: 'Це нормально для метаболічного стресу. Для збереження сили відпочивай більше.' 
                };
              }
              return { 
                color: 'var(--red)', bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.2)',
                pct: Math.round(dropPct*100), max: prevReps, min: currReps,
                msg: `М'язи не встигають відновлювати АТФ.`,
                advice: 'Збільш час відпочинку до 3-5 хвилин для підтримки високої інтенсивності.' 
              };
            } else if (dropPct >= 0.2) {
              return { 
                color: 'var(--orange)', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.2)',
                pct: Math.round(dropPct*100), max: prevReps, min: currReps,
                msg: `Нормальна втома для гіпертрофії.`,
                advice: 'Для збереження об\'єму спробуй відпочивати 2-3 хвилини.' 
              };
            }
          }
          return null;
        }"""

text = text.replace(old_analyze, new_analyze)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(text)

print("Logic updated")
