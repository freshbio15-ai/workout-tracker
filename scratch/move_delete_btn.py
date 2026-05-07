import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Update deleteDay function
old_deleteDay = r"  function deleteDay\(\)\{setData\(p=>\{const n=\{...p\};delete n\[selected\];return n\}\);setDraft\(mkDay\(\)\);flash\('Видалено'\)\}"
new_deleteDay = r"  function deleteDay(k){const key = typeof k === 'string' ? k : selected; if(!window.confirm('Дійсно видалити це тренування?')) return; setData(p=>{const n={...p};delete n[key];return n});if(selected===key)setDraft(mkDay());setHistoryDetail(null);flash('Видалено')}"
js = re.sub(old_deleteDay, new_deleteDay, js)

# 2. Remove delete button from draft view
old_draft_del = r"hasData&&React\.createElement\('button',\{className:'del-day-btn',onClick:deleteDay\},React\.createElement\('div', \{style:\{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'\}\}, React\.createElement\(TrashIcon\), 'Видалити'\)\)"
new_draft_del = r"null"
js = re.sub(old_draft_del, new_draft_del, js)

# 3. Add delete button to history detail view
old_hist_edit = r"""      \}\},React\.createElement\('div', \{style:\{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'\}\}, React\.createElement\(EditIcon\), 'Редагувати тренування'\)\)"""
new_hist_edit = r"""      }},React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'}}, React.createElement(EditIcon), 'Редагувати тренування')),
      React.createElement('button',{className:'del-day-btn',style:{marginTop:'12px'},onClick:()=>deleteDay(k)},React.createElement('div', {style:{display:'flex',alignItems:'center',justifyContent:'center',gap:'6px'}}, React.createElement(TrashIcon), 'Видалити'))"""
js = re.sub(old_hist_edit, new_hist_edit, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Delete button moved.")
