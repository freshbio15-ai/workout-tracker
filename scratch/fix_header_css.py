import re

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

# Current CSS:
# .sets-header{display:grid;grid-template-columns:30px 1fr 1fr 28px;gap:5px;margin-bottom:5px;padding:0 2px}
old_css = r"\.sets-header\{display:grid;grid-template-columns:30px 1fr 1fr 28px;gap:5px;margin-bottom:5px;padding:0 2px\}"
new_css = r".sets-header{display:grid;grid-template-columns:30px 1fr 16px 1fr 32px 28px;gap:5px;margin-bottom:5px;padding:0 2px}"

css = re.sub(old_css, new_css, css)

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)

print("CSS header fixed.")
