import re

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

# Update .logo-icon to be a simple container for the image
old_logo_css = r"\.logo-icon\{width:38px;height:38px;border-radius:11px;background:linear-gradient\(135deg,var\(--accent\),#6d28d9\);display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:var\(--glow\)\}"
new_logo_css = r".logo-icon{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;overflow:hidden}"

css = re.sub(old_logo_css, new_logo_css, css)

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)

print("Logo CSS cleaned.")
