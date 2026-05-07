with open('/Users/mfolwh/Desktop/TRA/styles.css', 'a') as f:
    f.write("""
/* ===== INSIGHT BOX ===== */
.insight-box {
  padding: 16px;
  border-radius: var(--radius-sm);
  border: 1px solid;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  animation: slideUp 0.3s ease-out;
  box-shadow: 0 4px 15px rgba(0,0,0,0.15);
  position: relative;
  overflow: hidden;
}
.insight-box::before {
  content: '';
  position: absolute;
  top: 0; left: 0; bottom: 0;
  width: 4px;
  background: currentColor;
  opacity: 0.5;
}
.insight-icon {
  font-size: 20px;
  line-height: 1;
}
.insight-content {
  flex: 1;
}
.insight-title {
  font-size: 14px;
  font-weight: 800;
  margin: 0 0 6px;
  letter-spacing: 0.3px;
}
.insight-text {
  font-size: 13px;
  color: var(--text1);
  margin: 0;
  line-height: 1.5;
}
.insight-text strong {
  font-weight: 700;
}
""")

print("CSS appended.")
