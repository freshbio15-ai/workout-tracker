import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    text = f.read()

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

old_target = "const isFirstLoad=useRef(true);"
new_target = "const isFirstLoad=useRef(true);\n" + check_pr_fn

if "const checkPR = useCallback" not in text:
    text = text.replace(old_target, new_target)
    with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
        f.write(text)
    print("Fixed TDZ by reinserting checkPR")
else:
    print("checkPR already exists")

