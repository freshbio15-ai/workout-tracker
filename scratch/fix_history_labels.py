import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Remove "Тоннаж за день" in renderHistoryDetail
# The line is: React.createElement('div',{className:'tonnage-label'},'Тоннаж за день'),
js = js.replace("React.createElement('div',{className:'tonnage-label'},'Тоннаж за день'),", "")

# 2. Change "Загальний тоннаж" to "Загальний об'єм" in renderHistory
js = js.replace("React.createElement('div',{className:'tonnage-label'},'Загальний тоннаж'),", "React.createElement('div',{className:'tonnage-label'},'Загальний об\\'єм'),")

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Labels updated.")
