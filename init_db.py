import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO urls (filename, url) VALUES (?, ?)",
            ('test1', 'www.test.com')
            )

cur.execute("INSERT INTO urls (filename, url) VALUES (?, ?)",
            ('test2', 'www.test.com')
            )

connection.commit()
connection.close()