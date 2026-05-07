import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Rename Трицепс to Тріцепс
js = js.replace("label:'Трицепс'", "label:'Тріцепс'")
js = js.replace("label: 'Трицепс'", "label: 'Тріцепс'")

# 2. Change `X підх. · Y кг` to `X х Y кг`
old_str = r"${ex.sets.length} підх. · ${et>1000?(et/1000).toFixed(1)+'т':et+'кг'}"
new_str = r"${ex.sets.length} х ${et>1000?(et/1000).toFixed(1)+'т':et+'кг'}"
js = js.replace(old_str, new_str)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

# 3. Center hc-stats
# Current css:
# .hc-stats {
#   display: flex;
#   gap: 16px;
#   margin-bottom: 12px;
#   padding-bottom: 12px;
#   border-bottom: 1px dashed var(--border2);
# }
old_css = r"""\.hc-stats \{
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed var\(--border2\);
\}"""

new_css = r""".hc-stats {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed var(--border2);
}"""
css = re.sub(old_css, new_css, css)

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)

print("All updates applied.")
