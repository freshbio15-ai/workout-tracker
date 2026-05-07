import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Update text for labels
js = js.replace("React.createElement('div',{className:'section-label'},'Активність м\\'язів'),", "React.createElement('div',{className:'section-label'},'Активність'),")
js = js.replace("React.createElement('div',{className:'section-label'},'Всі тренування ('+history.length+')'),", "React.createElement('div',{className:'section-label'},'Тренування ('+history.length+')'),")

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)


# 2. Add .section-label to styles.css
css_add = """
/* ===== SECTION LABELS ===== */
.section-label {
  font-size: 16px;
  font-weight: 800;
  color: var(--text1);
  margin-top: 4px;
  margin-bottom: 14px;
  letter-spacing: 0.5px;
}
"""

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'a') as f:
    f.write(css_add)

print("Labels and CSS updated.")
