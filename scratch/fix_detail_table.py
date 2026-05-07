import re

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

# Add nth-child rules for detail-table
css_add = """
.detail-table th:nth-child(2), .detail-table td:nth-child(2) {
  width: 60px;
}
.detail-table th:nth-child(3), .detail-table td:nth-child(3) {
  width: 20px;
  text-align: center;
  padding-left: 0;
  padding-right: 0;
  color: var(--text3);
}
"""

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'a') as f:
    f.write(css_add)

print("Detail table CSS updated.")
