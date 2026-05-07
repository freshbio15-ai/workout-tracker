import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

matches = re.finditer(r'.{0,50}<img.{0,50}', js, re.IGNORECASE)
for m in matches:
    print(m.group(0))

matches2 = re.finditer(r'.{0,50}createElement\(\'img\'.{0,50}', js, re.IGNORECASE)
for m2 in matches2:
    print(m2.group(0))

