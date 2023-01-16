from database import create_database
import sqlite3

if __name__ == '__main__':
    database_name = 'database.db'
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    create_database(cursor)
    conn.commit()
    conn.close()
