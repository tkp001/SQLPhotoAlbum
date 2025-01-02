from database import cursor, db
import os
import shutil
import hashlib

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
def get_photos(user_id):
    sql = "SELECT * FROM photos WHERE user_id=%s ORDER BY upload_date DESC"
    cursor.execute(sql, (user_id,))
    result = cursor.fetchall()

    for row in result:
        print(row)

    if result == []:
        print("No photos.")

def get_photo(id, user_id):
    sql = "SELECT * FROM photos WHERE photo_id=%s AND user_id=%s"
    cursor.execute(sql, (id, user_id))
    result = cursor.fetchone()
    return result

def get_photo_byname(name, user_id):
    sql = "SELECT * FROM photos WHERE name=%s AND user_id=%s"
    cursor.execute(sql, (name, user_id))
    result = cursor.fetchone()
    return result

def delete_photo(id, user_id):
    sql = "DELETE FROM photos WHERE photo_id=%s AND user_id=%s"
    cursor.execute(sql, (id, user_id))
    db.commit()
    print("photo deleted from database")
    add_log("system", f"photo photo-id:{id}, user-id:{user_id} deleted from database")


# advanced commands
def insert_photo(user_id, file_path, name, title, description, category, date_taken, time_taken, hash):
    sql = """
    INSERT INTO photos(user_id, file_path, name, title, description, category, date_taken, time_taken, hash)
     VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = (user_id, file_path, name, title, description, category, date_taken, time_taken, hash)

    cursor.execute(sql, data)
    db.commit()
    print("photo inserted into database")
    
    photo_id = cursor.lastrowid
    add_log("system", f"photo {name} inserted as photo-id:{photo_id}, user-id:{user_id}")
    return photo_id

def update_photo(photo_id, user_id, title, description, category, date_taken, time_taken):
    sql = """
    UPDATE photos
    SET title=%s, description=%s, category=%s, date_taken=%s, time_taken=%s
    WHERE photo_id=%s AND user_id=%s
    """
    data = (title, description, category, date_taken, time_taken, photo_id, user_id)
    
    cursor.execute(sql, data)
    db.commit()

    add_log("system", f"photo info photo-id:{photo_id}, user-id:{user_id} updated")

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
def add_form(user_id):
    file_path = input("Enter the file path for the photo (required): ")
    if not file_path or not os.path.exists(file_path):
        print("valid file path is required.")
        return

    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads", "uploaded_photos", f"{user_id}")
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)
    file_name = os.path.basename(file_path)
    name = file_name 
    new_file_path = os.path.join(downloads_folder, file_name)

    # if get_photo_byname(name) != None:
    #     print("duplicate name detected, please have unique file names")
    #     return

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
    
    photo_id = insert_photo(user_id, new_file_path, name, title, description, category, date_taken, time_taken, hash)

    shutil.copy(file_path, new_file_path)
    
    print("photo added to disk")

    a = get_file_extension(new_file_path)
    formatted_name = f"{photo_id}{a}"
    rename_file(new_file_path, formatted_name)
    print("photo formatted")
    new_formatted_path = os.path.join(downloads_folder, formatted_name)

    # print(photo_id)
    # print(formatted_name)
    # print(new_file_path)
    # print(new_formatted_path)
    sql = "UPDATE photos SET file_path=%s WHERE photo_id=%s"
    data = (new_formatted_path , photo_id)
    cursor.execute(sql, data)
    db.commit()

def delete_form(user_id):
    get_photos(user_id)
    id = input("Enter photo id: ")
    
    if get_photo(id, user_id) != None:
        data = get_photo(id, user_id)
        file_path = data[2]
    else:
        print("id does not exist")
        return
    
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Photo file {file_path} deleted from disk.")
    else:
        print(f"The file {file_path} does not exist on the disk.")

    delete_photo(id, user_id)

def update_form(user_id):
    get_photos(user_id)
    id = input("Enter photo id: ")

    if get_photo(id, user_id) != None:
        data = get_photo(id, user_id)
    else:
        print("id does not exist")
        return
    
    print(data)

    title = input(f"Enter new photo title (Current: {data[4]}): ")
    description = input(f"Enter new photo description (Current: {data[5]}): ")
    category = input(f"Enter new photo category (Current: {data[6]}): ")

    
    update_photo(data[0], data[1], title, description, category, data[7], data[8])
    print("photo updated")

    get_photos(user_id)

def download_form(user_id):
    # ONLY SIMULATES A DONWLOAD
    get_photos(user_id)
    id = input("Enter photo id: ")

    if get_photo(id, user_id) != None:
        data = get_photo(id, user_id)
    else:
        print("id does not exist")
        return

    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    if not os.path.isfile(data[2]):
            print("file not found on disk")
            return

    file_name = os.path.basename(data[2])
    destination_path = os.path.join(downloads_folder, f"{data[10]}{file_name}")
    shutil.copy(data[2], destination_path)
    print("photo downloaded")

    add_log("system", f"photo {data[2]}, photo-id:{data[0]}, user-id:{data[1]} downloaded from disk")

def checkauth(email, password):
    sql = "SELECT * FROM users WHERE email=%s"
    cursor.execute(sql, (email,))
    result = cursor.fetchone()
    # print(result)
    # return result

    if result == None:
        print("Invalid email")
        return
    else:
        sql = "SELECT * FROM users WHERE email=%s AND password=%s"
        cursor.execute(sql, (email, password))
        result = cursor.fetchone()

        if result == None:
            print("Invalid password")
            return
        else:
            return result

exit = 0
auth = 0
user_details = None

print("Photo Album Project in SQL")

while exit == 0:
    create = input("Create new account? [Y/N]: ")
    if create.upper() == "Y":
        username = input("Enter account username: ")
        email = input("Enter account email: ")
        password = input("Enter account password: ") 
            
        sql = "INSERT INTO users(username,email,password) VALUES(%s, %s, %s)"
        cursor.execute(sql, (username,email,password))
        db.commit()
        print("Account created, use credientials to login.")

    while user_details == None:


        email = input("Enter your email: ")
        password = input("Enter your password: ")

        user_details = checkauth(email,password)

        if user_details != None:
            auth = 1
            print(f"Welcome {user_details[1]}")
    
    while auth == 1:
        user_id = user_details[0]
        username = user_details[1]
        email = user_details[2]
        password = user_details[3]

        while True:
            print("1. add photo")
            print("2. delete photo")
            print("3. update photo")
            print("4. view photos")
            print("5. download photo")
            print("6. LOGOUT")
            print("7. DELETE ACCOUNT")
            ipt = int(input("Enter option: "))

            match ipt:
                case 1:
                    add_form(user_id)
                case 2:
                    delete_form(user_id)
                case 3:
                    update_form(user_id)
                case 4:
                    get_photos(user_id)
                case 5:
                    download_form(user_id)
                case 6:
                    # print("Exited code")
                    auth = 0
                    user_details = None
                    exit = 1
                    break
                case 7:
                    sql = f"DELETE FROM users WHERE user_id={user_id}"
                    cursor.execute(sql)
                    db.commit()
                    print("database info deleted")

                    auth = 0
                    user_details = None
                    exit = 1
                    break

                    #delete all folder data
                    try:
                        shutil.rmtree(os.path.join(os.path.expanduser("~"), "Downloads", "uploaded_photos", f"{user_id}"))
                        print("user disk data deleted")
                    except Exception as e:
                        print(f"error: {e}")
                case _:
                    print("Invalid Option!!")

print("End of code")