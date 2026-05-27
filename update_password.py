# update_password.py
from werkzeug.security import generate_password_hash
import mysql.connector

conn = mysql.connector.connect(host='localhost', user='root', password='Your_Password', database='health_tracker')
cur = conn.cursor()
users = [(1,'alice123'), (2,'bob123')]
for uid, pwd in users:
    cur.execute("UPDATE users SET password=%s WHERE user_id=%s", (generate_password_hash(pwd), uid))
conn.commit()
cur.close(); conn.close()
print("Passwords updated")
