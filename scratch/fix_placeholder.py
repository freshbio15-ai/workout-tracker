import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

js = js.replace("placeholder:'Нова група…'", "placeholder:'Назва…'")

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Placeholder fixed.")
