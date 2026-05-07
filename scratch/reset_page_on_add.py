import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Add setWeightPage(0) to the "Add weight" button onClick
js = js.replace("setSettings(s => ({...s, weightHistory: {...(s.weightHistory||{}), [bwDate]: val}}));",
                "setSettings(s => ({...s, weightHistory: {...(s.weightHistory||{}), [bwDate]: val}})); setWeightPage(0);")

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Reset page on add implemented.")
