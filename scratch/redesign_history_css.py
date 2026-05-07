import re

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'r') as f:
    css = f.read()

# 1. Remove old history styles
start_marker = r"\.tonnage-card\{"
end_marker = r"\/\* ===== WORKOUT DETAIL VIEW ===== \*\/"

# Use regex to remove everything between start_marker and end_marker
pattern = re.compile(start_marker + r"[\s\S]*?(?=" + end_marker + ")")
css = pattern.sub("", css)

# 2. Define new history styles
new_css = """/* ===== HISTORY (DIARY) REDESIGN ===== */

/* Dashboard Card */
.tonnage-card {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px 20px;
  margin-bottom: 24px;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
.tonnage-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 100%;
  background: radial-gradient(circle at top, rgba(124,58,237,0.1) 0%, transparent 70%);
  pointer-events: none;
}
.tonnage-value {
  font-size: 42px;
  font-weight: 900;
  letter-spacing: -1px;
  background: linear-gradient(135deg, #fff 30%, var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
  position: relative;
  z-index: 1;
}
.tonnage-label {
  font-size: 11px;
  color: var(--text3);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-top: 4px;
  position: relative;
  z-index: 1;
}
.tonnage-row {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255,255,255,0.05);
  position: relative;
  z-index: 1;
}
.tonnage-item {
  flex: 1;
  text-align: center;
}
.tonnage-item:not(:last-child) {
  border-right: 1px solid rgba(255,255,255,0.05);
}
.tonnage-item-val {
  font-size: 18px;
  font-weight: 800;
  color: var(--text1);
}
.tonnage-item-lbl {
  font-size: 10px;
  color: var(--text3);
  margin-top: 2px;
  font-weight: 500;
}

/* Muscle Activity Progress Bars */
.muscle-tonnage-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}
.mt-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.mt-emoji {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--bg3);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.mt-emoji img {
  width: 20px;
  height: 20px;
}
.mt-bar-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.mt-bar-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}
.mt-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text1);
}
.mt-tonnage {
  font-size: 13px;
  font-weight: 700;
  color: var(--accent2);
}
.mt-bar-bg {
  width: 100%;
  height: 6px;
  background: var(--bg3);
  border-radius: 3px;
  overflow: hidden;
}
.mt-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--cyan));
  border-radius: 3px;
  transition: width 0.8s ease-out;
}

/* Workout Feed (Receipt Style) */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.history-card {
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}
.history-card:active {
  transform: scale(0.98);
  background: var(--bg3);
}
.hc-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.hc-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text1);
}
.hc-date {
  font-size: 11px;
  color: var(--text3);
  margin-top: 2px;
}
.hc-muscle {
  background: var(--bg3);
  color: var(--text2);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid var(--border);
}
.hc-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed var(--border2);
}
.hc-stat {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text2);
  font-weight: 500;
}
.hc-stat strong {
  color: var(--text1);
  font-weight: 700;
}
.hc-stat-icon {
  color: var(--accent2);
}
.hc-exercises {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.hc-ex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}
.hc-ex-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text1);
  font-weight: 500;
}
.hc-ex-right {
  color: var(--text3);
  font-size: 12px;
  font-weight: 500;
}

"""

# Insert new css right before the end marker
css = css.replace("/* ===== WORKOUT DETAIL VIEW ===== */", new_css + "/* ===== WORKOUT DETAIL VIEW ===== */")

with open('/Users/mfolwh/Desktop/TRA/styles.css', 'w') as f:
    f.write(css)

print("CSS updated.")
