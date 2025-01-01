from database import cursor, db
import random
import os
import shutil
import hashlib

## hash is currrently random number

# log methods
def add_log(user, text):
    sql = "INSERT INTO logs(user,text) VALUES(%s, %s)"
    cursor.execute(sql, (user, text))
    db.commit()

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


# photo methods
def get_photos():
    sql = "SELECT * FROM photos ORDER BY upload_date DESC"
    cursor.execute(sql)
    result = cursor.fetchall()

    for row in result:
        print(row)

    if result == []:
        print("No photos.")

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

    add_log(f"system", "photo id:{id} deleted")

# advanced commands
def insert_photo(file_path, user, name, title, description, category, date_taken, time_taken, hash):
    sql = """
    INSERT INTO photos(file_path, user, name, title, description, category, date_taken, time_taken, hash)
     VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = (file_path, user, name, title, description, category, date_taken, time_taken, hash)

    cursor.execute(sql, data)
    db.commit()
    print("photo inserted into database")
    log_id = cursor.lastrowid
    add_log("system", f"photo {name} inserted as id:{log_id}")


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

    add_log("system", f"photo info id:{photo_id} updated")

# internet methods
def rename_file(current_path, new_name):
    # Get the directory from the current file path
    directory = os.path.dirname(current_path)
    
    # Create the new file path
    new_path = os.path.join(directory, new_name)
    
    try:
        os.rename(current_path, new_path)
    except Exception as e:
        print(f"error: {e}")

def get_file_extension(file_path):
    _, extension = os.path.splitext(file_path)
    return extension.lower()

def get_image_hash(file_path):
    """Generate a hash for an image file."""
    try:
        with open(file_path, 'rb') as img_file:
            img_data = img_file.read()
            return hashlib.sha256(img_data).hexdigest()
    except FileNotFoundError:
        print("File not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# terminal options
def add_form():
    file_path = input("Enter the file path for the photo (required): ")
    if not file_path or not os.path.exists(file_path):
        print("valid file path is required.")
        return

    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads", "uploaded_photos")
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)
    file_name = os.path.basename(file_path)
    name = file_name 
    new_file_path = os.path.join(downloads_folder, file_name)

    # if get_photo_byname(name) != None:
    #     print("duplicate name detected, please have unique file names")
    #     return


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

    # get real hash
    #hash = str(random.randint(11111, 99999))
    
    hash = get_image_hash(file_path)

    #insert photo, rename to primary key, provide database new file path
    insert_photo(new_file_path, user, name, title, description, category, date_taken, time_taken, hash)
    
    photo_id = cursor.lastrowid
    shutil.copy(file_path, new_file_path)
    print("photo added to disk")

    a = get_file_extension(new_file_path)
    formatted_name = f"{photo_id}{a}"
    rename_file(new_file_path, formatted_name)
    print("photo formatted")

    new_formatted_path = os.path.join(downloads_folder, formatted_name)
    sql = "UPDATE photos SET file_path=%s WHERE photo_id=%s"
    data = (new_formatted_path , photo_id)
    cursor.execute(sql, data)
    db.commit()

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

def download_form():
    # ONLY SIMULATES A DONWLOAD
    get_photos()
    id = input("Enter photo id: ")

    if get_photo(id) != None:
        data = get_photo(id)
    else:
        print("id does not exist")
        return

    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    if not os.path.isfile(data[1]):
            print("file not found on disk")
            return

    file_name = os.path.basename(data[1])
    destination_path = os.path.join(downloads_folder, f"{data[10]}{file_name}")
    shutil.copy(data[1], destination_path)
    print("photo downloaded")

# loop
while True:
    print("1. add photo")
    print("2. delete photo")
    print("3. update photo")
    print("4. view photos")
    print("5. download photo")
    print("6. QUIT")
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
        case 5:
            download_form()
        case 6:
            print("Exited code")
            break
        case _:
            print("Invalid Option!!")