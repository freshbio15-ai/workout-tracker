import re

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

# Revert tab-bar and tab-bar-inner
css = re.sub(r"\.tab-bar\{([^}]*)justify-content:center;([^}]*)\}", 
             r".tab-bar{\1justify-content:space-between;\2}", css)
css = re.sub(r"\.tab-bar-inner\{([^}]*)max-width:340px;([^}]*)\}", 
             r".tab-bar-inner{\1max-width:480px;\2}", css)

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)

print("Nav CSS reverted.")
