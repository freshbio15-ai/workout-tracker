with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    js = f.read()

target = """      showEasterEgg && React.createElement('div',{className:'cc-overlay',onClick:()=>setShowEasterEgg(false)},
        React.createElement('img',{src:'assets/easter_egg.jpg', style:{maxWidth:'90%',maxHeight:'90vh',borderRadius:'12px',objectFit:'contain'}, onClick:e=>e.stopPropagation()})
      ),"""

js = js.replace(target, "null,")

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(js)

print("Removed showEasterEgg entirely.")
