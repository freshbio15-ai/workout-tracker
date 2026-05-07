import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# 1. Update trend logic inside weightChartData.map
old_map_start = r"""              weightChartData\.map\(\(d, i\) => \{
                const h = Math\.max\(5, Math\.round\(\(\(d\.weight - wBase\) / \(wMax - wBase \+ wRange\*0\.2\)\) \* 100\)\);
                const prev = i > 0 \? weightChartData\[i-1\]\.weight : d\.weight;
                const isDrop = d\.weight < prev;
                const isGain = d\.weight > prev;"""

new_map_start = r"""              weightChartData.map((d, i) => {
                const h = Math.max(5, Math.round(((d.weight - wBase) / (wMax - wBase + wRange*0.2)) * 100));
                
                const gIdx = allWeightKeys.indexOf(d.date);
                const pDate = gIdx > 0 ? allWeightKeys[gIdx - 1] : null;
                const pW = pDate ? (bwUnit === 'lbs' ? weightHistory[pDate]/0.453592 : weightHistory[pDate]) : d.weight;
                
                const isDrop = d.weight < pW;
                const isGain = d.weight > pW;"""

js = re.sub(old_map_start, new_map_start, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Trend logic fixed.")
