with open('/Users/mfolwh/Desktop/TRA/styles.css', 'a') as f:
    f.write("""
/* ===== REHAB MODE ===== */
.rehab-mode {
  --accent: #14b8a6;
  --accent2: #2dd4bf;
  --accent3: #5eead4;
  --glow: 0 0 30px rgba(45,212,191,0.15);
}
.rehab-mode .logo-icon {
  background: linear-gradient(135deg, var(--accent), #0f766e);
}
.rehab-mode .logo-icon svg {
  color: #fff;
}

/* Rehab Progress Bar */
.rehab-progress-wrapper {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.rehab-progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.rehab-progress-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--accent2);
  display: flex;
  align-items: center;
  gap: 6px;
}
.rehab-progress-text {
  font-size: 11px;
  color: var(--text2);
  font-weight: 600;
}
.rehab-progress-bar-bg {
  width: 100%;
  height: 8px;
  background: var(--bg);
  border-radius: 4px;
  overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.5);
}
.rehab-progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #14b8a6, #34d399);
  border-radius: 4px;
  transition: width 0.5s ease-out;
  box-shadow: 0 0 10px rgba(52, 211, 153, 0.4);
}
.rehab-success-banner {
  background: linear-gradient(135deg, rgba(20,184,166,0.15), rgba(52,211,153,0.15));
  border: 1px solid rgba(52,211,153,0.3);
  border-radius: var(--radius-sm);
  padding: 16px;
  text-align: center;
  margin-bottom: 16px;
  box-shadow: 0 0 20px rgba(52,211,153,0.1);
}
.rehab-success-text {
  font-size: 14px;
  font-weight: 700;
  color: var(--green2);
  line-height: 1.4;
}

.rehab-warning {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--red);
  padding: 8px 12px;
  border-radius: var(--radius-xs);
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}
""")
print("CSS appended.")
