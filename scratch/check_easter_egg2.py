import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

matches = re.finditer(r'.{0,50}showEasterEgg.{0,50}', js, re.IGNORECASE)
for m in matches:
    print(m.group(0))

