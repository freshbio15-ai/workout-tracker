with open('/Users/mfolwh/Desktop/TRA/app.js', 'r') as f:
    text = f.read()

old_adv = "advice: 'Нормальна втома для гіпертрофії. Тримай відпочинок 2-3 хв.'"
new_adv = "advice: 'Нормальна втома для гіпертрофії. Тримай поточну вагу та час відпочинку.'"

text = text.replace(old_adv, new_adv)

with open('/Users/mfolwh/Desktop/TRA/app.js', 'w') as f:
    f.write(text)

print("Changed advice.")
