import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# The current broken block:
# weightChartData.map(...) }), allWeightKeys.length > 10 && React.createElement(...) ) ) : ...

# Let's fix the nesting
pattern = r"(\s*)allWeightKeys\.length > 10 && React\.createElement\('div', \{style:\{display:'flex', justifyContent:'center', gap:'16px', marginTop:'8px'\}\},"

# We need to ensure Child 1 (the chart-container div) is closed before the pagination child
# So we look for the line before this pattern

js = js.replace("            }),\n            allWeightKeys.length > 10",
                "            }),\n            ),\n            allWeightKeys.length > 10")

# Wait, if I added a '),' then I need to make sure I don't have too many at the end
# Currently line 882 is: ) : React.createElement
# If I added a closing paren at line 877, I still need to close the Fragment at line 882.

# Let's verify the whole ternary structure
# Ternary ? Fragment(Div(map), Pagination) : EmptyDiv

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Attempting fix...")
