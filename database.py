import mysql.connector

config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'photo_album_2'
}

db = mysql.connector.connect(**config)
cursor = db.cursor()