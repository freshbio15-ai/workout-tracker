import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Remove the duplicate LightbulbIcon that I added right before BookIcon
pattern = r"const LightbulbIcon=\(\{size=24,className=''\}\)=>React\.createElement\('svg',\{xmlns:'http://www\.w3\.org/2000/svg',width:size,height:size,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor',strokeWidth:'2',strokeLinecap:'round',strokeLinejoin:'round',className:className\},React\.createElement\('path',\{d:'M15 14c\.2-1 \.7-1\.7 1\.5-2\.5 1-\.9 1\.5-2\.2 1\.5-3\.5A6 6 0 0 0 6 8c0 1 \.2 2\.2 1\.5 3\.5\.7\.9 1\.2 1\.5 1\.5 2\.5'\}\),React\.createElement\('path',\{d:'M9 18h6'\}\),React\.createElement\('path',\{d:'M10 22h4'\}\)\);\n"

js = re.sub(pattern, "", js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Syntax fixed.")
