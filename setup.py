import mysql.connector
from mysql.connector import errorcode
from database import cursor

DB_NAME = 'photo_album'

# define tables
TABLES = {}

TABLES['logs'] = (
    "CREATE TABLE `logs` ("
    " `id` INT(11) NOT NULL AUTO_INCREMENT,"
    " `user` VARCHAR(250) NOT NULL,"
    " `text` VARCHAR(250) NOT NULL,"
    " `created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
    " PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB"
)

# users foreign key later (login/signup)
TABLES['photos'] = (
    "CREATE TABLE `photos` ("
    " `photo_id` INT NOT NULL AUTO_INCREMENT,"
    " `file_path` TEXT NOT NULL,"
    " `user` VARCHAR(250) NOT NULL,"
    " `name` VARCHAR(250),"
    " `title` VARCHAR(250),"
    " `description` TEXT,"
    " `category` VARCHAR(100),"
    " `date_taken` DATE,"
    " `time_taken` TIME,"
    " `upload_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
    " `hash` VARCHAR(255),"
    " PRIMARY KEY (`photo_id`)"
    ") ENGINE=InnoDB"
)


def create_database():
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
    print(f"Database {DB_NAME} created!")

def create_tables():
    cursor.execute(f"USE {DB_NAME}")

    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print(f"Creating table ({table_name}) ", end="")
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Already Exists")
            else:
                print(err.msg)




# setup
create_database()
create_tables()