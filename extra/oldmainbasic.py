from database import cursor, db
import os
import shutil
import random
import mysql.connector
from mysql.connector import errorcode

## hash is currrently random number

# log commands
def add_log(user, text):
    sql = "INSERT INTO logs(user,text) VALUES(%s, %s)"
    cursor.execute(sql, (user, text))
    db.commit()
    log_id = cursor.lastrowid
    print(f"Added log id:{log_id}, context:{text}")

def get_logs():
    sql = "SELECT * FROM logs ORDER BY created DESC"
    cursor.execute(sql)
    result = cursor.fetchall()

    for row in result:
        # print(row[1])
        print(row)

def get_log(id):
    sql = "SELECT * FROM logs WHERE id=%s"
    cursor.execute(sql, (id,))
    result = cursor.fetchone()

    for row in result:
        print(row)

def update_log(id, text):
    sql = "UPDATE logs SET text=%s WHERE id=%s"
    cursor.execute(sql, (text, id))
    db.commit()
    print(f"log id:{id} updated")

def delete_log(id):
    sql = "DELETE FROM logs WHERE id=%s"
    cursor.execute(sql, (id,))
    db.commit()
    print(f"log id:{id} removed")


# image commands
def get_photos():
    sql = "SELECT * FROM photos ORDER BY upload_date DESC"
    cursor.execute(sql)
    result = cursor.fetchall()

    for row in result:
        print(row)

def get_photo(id):
    sql = "SELECT * FROM photos WHERE photo_id=%s"
    cursor.execute(sql, (id,))
    result = cursor.fetchone()
    return result

def get_photo_byname(name):
    sql = "SELECT * FROM photos WHERE name=%s"
    cursor.execute(sql, (name,))
    result = cursor.fetchone()
    return result

def delete_photo(id):
    sql = "DELETE FROM photos WHERE photo_id=%s"
    cursor.execute(sql, (id,))
    db.commit()
    print("photo deleted from database")

def insert_photo(file_path, user, name, title, description, category, date_taken, time_taken, hash):
    sql = """
    INSERT INTO photos(file_path, user, name, title, description, category, date_taken, time_taken, hash)
     VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = (file_path, user, name, title, description, category, date_taken, time_taken, hash)

    cursor.execute(sql, data)
    db.commit()
    print("photo inserted into database")

def update_photo(photo_id, file_path, user, name, title, description, category, date_taken, time_taken, hash):
    sql = """
    UPDATE photos
    SET file_path=%s, user=%s, name=%s, title=%s, description=%s, category=%s, date_taken=%s, time_taken=%s, hash=%s
    WHERE photo_id=%s
    """
    data = (file_path, user, name, title, description, category, date_taken, time_taken, hash, photo_id)
    
    cursor.execute(sql, data)
    db.commit()
    print(f"photo id:{photo_id} updated")

def add_form():
    file_path = input("Enter the file path for the photo (required): ")
    if not file_path or not os.path.exists(file_path):
        print("valid file path is required.")
        return

    home_dir = os.path.expanduser("~")
    downloads_folder = os.path.join(home_dir, "Downloads", "uploaded_photos")
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)
    file_name = os.path.basename(file_path)
    name = file_name ##
    new_file_path = os.path.join(downloads_folder, file_name)

    if get_photo_byname(name) != None:
        print("duplicate name detected, please have unique file names")
        return


    user = input("Enter user (required): ")
    if not user:
        print("user is required.")
        return
    
    # name = input("Enter photo name: ")
    title = input("Enter photo title: ")
    description = input("Enter photo description: ")
    category = input("Enter photo category: ")
    date_taken = input("Enter date taken (YYYY-MM-DD): ")
    time_taken = input("Enter time taken (HH:MM:SS): ")

    if date_taken == "":
        date_taken = None

    if time_taken == "":
        time_taken = None

    hash = str(random.randint(11111, 99999))
    
    insert_photo(new_file_path, user, name, title, description, category, date_taken, time_taken, hash)
    shutil.copy(file_path, new_file_path)
    print("photo added to disk")

def delete_form():
    get_photos()
    id = input("Enter photo id: ")
    
    if get_photo(id) != None:
        data = get_photo(id)
        file_path = data[1]
    else:
        print("id does not exist")
        return
    
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Photo file {file_path} deleted from disk.")
    else:
        print(f"The file {file_path} does not exist on the disk.")

    delete_photo(id)

def update_form():
    get_photos()
    id = input("Enter photo id: ")

    if get_photo(id) != None:
        data = get_photo(id)
    else:
        print("id does not exist")
        return
    
    print(data)

    title = input(f"Enter new photo title (Current: {data[4]}): ")
    description = input(f"Enter new photo description (Current: {data[5]}): ")
    category = input(f"Enter new photo category (Current: {data[6]}): ")

    update_photo(data[0], data[1], data[2], data[3], title, description, category, data[7], data[8], data[10])
    print("photo updated")

    get_photos()


while True:
    print("1. add photo")
    print("2. delete photo")
    print("3. update photo")
    print("4. view photos")
    ipt = int(input("Enter option: "))

    match ipt:
        case 1:
            add_form()
        case 2:
            delete_form()
        case 3:
            update_form()
        case 4:
            get_photos()
        case _:
            print("Invalid Option!!")