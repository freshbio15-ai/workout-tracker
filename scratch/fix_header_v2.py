import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Replace the logo icon and text
old_header = r"""        React\.createElement\('div',\{className:'app-logo'\},
          React\.createElement\('div',\{className:'logo-icon', onClick:\(\)=>setAdminTaps\(p=>\(\{\.\.\.p, logo: true\}\)\), style:\{cursor:'pointer'\}\},React\.createElement\(ActivityIcon, \{size: 20\}\)\),
          React\.createElement\('div',\{className:'logo-text'\},
            React\.createElement\('h1',null,'Gym Notebook'\),
            React\.createElement\('p',null,'Твій щоденник тренувань'\)
          \)
        \),"""

new_header = r"""        React.createElement('div',{className:'app-logo'},
          React.createElement('div',{className:'logo-icon', onClick:()=>setAdminTaps(p=>({...p, logo: true})), style:{cursor:'pointer', background:'none', padding:0}},
            React.createElement('img', {src: 'assets/icon_book.png', style: {width: '40px', height: '40px', borderRadius: '10px'}})
          ),
          React.createElement('div',{className:'logo-text'},
            React.createElement('h1',null,'Gym Notebook'),
            React.createElement('p',null,'by antigravity')
          )
        ),"""

js = re.sub(old_header, new_header, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Header updated.")
