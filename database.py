import mysql.connector

config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'photo_album'
}

db = mysql.connector.connect(**config)
cursor = db.cursor()