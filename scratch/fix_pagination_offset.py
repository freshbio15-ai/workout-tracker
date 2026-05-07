import re

with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

# Update the slicing logic in renderAnalytics
old_slicing = r"""    const totalWPages = Math\.ceil\(allWeightKeys\.length / 10\);
    const wStart = Math\.max\(0, allWeightKeys\.length - \(weightPage \+ 1\) \* 10\);
    const wEnd = allWeightKeys\.length - weightPage \* 10;
    const weightKeys = allWeightKeys\.slice\(wStart, wEnd\);"""

new_slicing = r"""    const totalWPages = Math.ceil(allWeightKeys.length / 10);
    const remainder = allWeightKeys.length % 10 || 10;
    let wEnd, wStart;
    if (weightPage === 0) {
      wEnd = allWeightKeys.length;
      wStart = Math.max(0, allWeightKeys.length - remainder);
    } else {
      wEnd = allWeightKeys.length - remainder - (weightPage - 1) * 10;
      wStart = Math.max(0, wEnd - 10);
    }
    const weightKeys = allWeightKeys.slice(wStart, wEnd);"""

js = re.sub(old_slicing, new_slicing, js)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Pagination offset logic updated.")
