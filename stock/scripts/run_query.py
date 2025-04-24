import mysql.connector
from datetime import datetime

def execute_query():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="S1tty1$great",
        database="stock"
    )
    cursor = conn.cursor()

    query = "DELETE FROM company_stock"
    cursor.execute(query)
    conn.commit()
    print(f"Query executed at {datetime.now()}")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    execute_query()
