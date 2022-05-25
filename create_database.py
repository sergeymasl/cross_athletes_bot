import sqlite3

# первичное создание баз данных
conn = sqlite3.connect('test.db', timeout=1)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users(
pri_user_id INTEGER PRIMARY KEY,
user_id INTEGER,
fname TEXT,
sname TEXT)
''')
conn.commit()
cursor.execute('''
CREATE TABLE IF NOT EXISTS traning(
pri_trening_id INTEGER PRIMARY KEY,
pri_user_id INTEGER FOREIGH KEY,
date_trening DATE)
''')
conn.commit()
cursor.execute('''
CREATE TABLE IF NOT EXISTS packages(
pri_packages_id INTEGER PRIMARY KEY,
pri_user_id INTEGER FOREIGH KEY,
package TEXT,
date_begin DATE,
date_final DATE,
quantity_left INTEGER,
quantity_begin INTEGER)
''')
conn.commit()
conn.close()
