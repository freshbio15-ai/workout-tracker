import re

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

# 1. Center the tab bar inner content
css = re.sub(r"\.tab-bar\{([^}]*)justify-content:space-between;([^}]*)\}", 
             r".tab-bar{\1justify-content:center;\2}", css)

# 2. Ensure tab-bar-inner and tab-btn spread out correctly
# We will use flex-grow and ensure width 100% is respected.
# Also adding some horizontal padding to the bar inner for mobile airiness.
css = re.sub(r"\.tab-bar-inner\{([^}]*)\}", 
             r".tab-bar-inner{display:flex;width:100%;max-width:480px;padding:0 8px}", css)

css = re.sub(r"\.tab-btn\{([^}]*)\}", 
             r".tab-btn{flex:1;display:flex;flex-direction:column;align-items:center;gap:3px;padding:8px 0;background:none;border:none;color:var(--text3);font-size:10px;font-weight:600;font-family:inherit;cursor:pointer;transition:all .2s}", css)

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)

print("Layout CSS updated.")
