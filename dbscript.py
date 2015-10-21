import os
import sqlite3

# configuration
DATABASE = os.path.join(os.getcwd(), 'db.sqlite')

def connect_db():
	return sqlite3.connect(DATABASE)

con = connect_db()
cur = con.cursor()
cur.execute('select * from users')
for row in cur.fetchall():
	print row