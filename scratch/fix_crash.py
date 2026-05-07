import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Replace useState declaration
js = re.sub(
    r"const \[showEasterEgg, setShowEasterEgg\] = useState\(false\);",
    r"const [adminTaps, setAdminTaps] = useState({logo: false, sync: false});",
    js
)

# Replace the showEasterEgg render block
js = re.sub(
    r"showEasterEgg\s*&&\s*React\.createElement\('div',\s*\{className:'cc-overlay',onClick:\(\)=>setShowEasterEgg\(false\)\},[\s\S]*?React\.createElement\('img',\{src:'assets/easter_egg\.jpg', style:\{maxWidth:'90%',maxHeight:'90%',borderRadius:'10px'\}\}\)\s*\)",
    "null",
    js
)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Crash fixed.")
