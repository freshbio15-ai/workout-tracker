import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

old_header = r"""              React\.createElement\('span',null,'Вага'\),
              React\.createElement\('span',null,'Повтори'\),
              React\.createElement\('span',null,''\)"""

new_header = r"""              React.createElement('span',null,'Вага'),
              React.createElement('span',null,''),
              React.createElement('span',null,'Повтори'),
              React.createElement('span',null,''),
              React.createElement('span',null,'')"""

js = re.sub(old_header, new_header, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Header fixed.")
