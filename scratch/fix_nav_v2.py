import re

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

# Adjust tab-bar and tab-bar-inner
css = re.sub(r"\.tab-bar\{([^}]*)justify-content:space-between;([^}]*)\}", 
             r".tab-bar{\1justify-content:center;\2}", css)
css = re.sub(r"\.tab-bar-inner\{([^}]*)max-width:480px;([^}]*)\}", 
             r".tab-bar-inner{\1max-width:340px;\2}", css)

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)

print("Nav CSS updated.")
