with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    text = f.read()

# 1. Add state variables
old_state = "  const [uid,setUid]=useState(null);"
new_state = "  const [uid,setUid]=useState(null);\n  const [showAdminModal, setShowAdminModal] = useState(false);\n  const [adminAccounts, setAdminAccounts] = useState([]);"
text = text.replace(old_state, new_state)

# 2. Update auth listener
old_auth = """    const unsub = auth.onAuthStateChanged(async (user)=>{
      if(user){
        setUid(user.uid);
        // load from cloud on first auth
        setCloudStatus('connecting');
        const cloud = await loadFromCloud(user.uid);"""

new_auth = """    const unsub = auth.onAuthStateChanged(async (user)=>{
      if(user){
        const override = localStorage.getItem('override_uid');
        const activeUid = override || user.uid;
        setUid(activeUid);
        // load from cloud on first auth
        setCloudStatus('connecting');
        const cloud = await loadFromCloud(activeUid);"""

if old_auth in text:
    text = text.replace(old_auth, new_auth)
else:
    print("WARNING: Old auth block not found")

# 3. Add admin panel
old_stats = "        // stats\n        React.createElement('div',{className:'settings-card'},"
admin_panel = """        // admin panel
        (settings.userWeight === '175' || localStorage.getItem('override_uid')) && React.createElement('div',{className:'settings-card'},
          React.createElement('h3',null,'👑 Admin Panel'),
          React.createElement('button',{className:'save-btn',onClick:async()=>{
            try {
              const snap = await db.collection('users').get();
              const accs = [];
              snap.forEach(d => {
                accs.push({ uid: d.id, ...d.data() });
              });
              setAdminAccounts(accs);
              setShowAdminModal(true);
            } catch(e) { alert('Помилка: ' + e.message); }
          }},'Змінити акаунт'),
          localStorage.getItem('override_uid') && React.createElement('button',{className:'del-day-btn',onClick:()=>{
            localStorage.removeItem('override_uid');
            window.location.reload();
          }},'Повернутись у свій акаунт')
        ),
"""
if admin_panel not in text:
    text = text.replace(old_stats, admin_panel + old_stats)

# 4. Add renderAdminModal method
render_admin_method = """
  function renderAdminModal(){
    if(!showAdminModal) return null;
    return React.createElement('div', {className:'cc-overlay', onClick:()=>setShowAdminModal(false)},
      React.createElement('div', {className:'cc-modal', onClick:e=>e.stopPropagation(), style:{maxHeight:'80vh',overflow:'auto'}},
        React.createElement('div', {className:'cc-header'},
          React.createElement('div', {className:'cc-title'}, 'Вибір акаунту'),
          React.createElement('button', {className:'cc-btn', onClick:()=>setShowAdminModal(false)}, React.createElement(XIcon))
        ),
        adminAccounts.map(acc => React.createElement('div', {
          key: acc.uid,
          style: {padding:'12px', borderBottom:'1px solid var(--border)', cursor:'pointer', background: uid === acc.uid ? 'var(--bg3)' : 'transparent', borderRadius:'8px'},
          onClick: async () => {
            localStorage.setItem('override_uid', acc.uid);
            setUid(acc.uid);
            const cloud = await loadFromCloud(acc.uid);
            if(cloud) {
              setData(cloud.data);
              setSettings(cloud.settings);
              persist('gymbook-data', cloud.data);
              persist('gymbook-settings', cloud.settings);
            } else {
              setData({});
              setSettings({});
            }
            setShowAdminModal(false);
            flash('Акаунт змінено');
          }
        }, 
          React.createElement('div', {style:{fontWeight:'bold', fontSize:'14px', marginBottom:'4px', wordBreak:'break-all'}}, acc.uid),
          React.createElement('div', {style:{fontSize:'12px', color:'var(--text3)'}}, 
            'Вага: ', acc.settings?.userWeight || '—', ' кг',
            React.createElement('br'),
            'Оновлено: ', acc.updatedAt?.toDate ? acc.updatedAt.toDate().toLocaleString() : '—'
          )
        ))
      )
    );
  }
"""

if "function renderAdminModal()" not in text:
    old_hasdata = "  const hasData = !!data[selected];"
    text = text.replace(old_hasdata, render_admin_method + "\n  const hasData = !!data[selected];")

# 5. Insert in render tree
if "renderAdminModal()" not in text.split("renderCustomPicker()")[1]:
    text = text.replace("renderCustomPicker(),", "renderCustomPicker(),\n      renderAdminModal(),")


with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(text)

print("Modifications done")
