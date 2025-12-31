import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",          # Your MySQL username
        password="",          # Your MySQL password (leave empty if none)
        database="online_banking"
    )
    return connection
