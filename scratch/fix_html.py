with open('/Users/mfolwh/Desktop/TRA/index.html', 'r') as f:
    html = f.read()

head_add = """  <link rel="apple-touch-icon" id="dynamic-apple-icon" href="assets/icon_book.png">
  <link rel="icon" id="dynamic-icon" href="assets/icon_book.png">"""

if "dynamic-apple-icon" not in html:
    html = html.replace("  <title>Gym Notebook \U0001f4aa</title>", "  <title>Gym Notebook \U0001f4aa</title>\n" + head_add)

with open('/Users/mfolwh/Desktop/TRA/index.html', 'w') as f:
    f.write(html)

print("HTML updated.")
