import sqlite3
from icecream import ic as print

def get_connection(db_name):
    try:
        return sqlite3.connect(db_name)
    except Exception as e:
        print(f"erroe:{e}")
        raise

def create_table(connection):
    query = """
            CREATE  TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY ,
            name TEXT NOT NULL,
            age INTEGER,
            email TEXT UNIQUE
            )
"""
    try:
        with connection:
            connection.execute(query)
        print("table is created")
    except Exception as e:
        print(e)

def insert_user(connection , name:str , age:int , email:str):
    query = "INSERT INTO users (name , age, email ) VALUES(?, ?, ?)"
    try:
        with connection:
            connection.execute(query,(name,age,email))
        print(f"User {name} added to ur database")
    except Exception as e:
        print(e)

def fetch_users(connection, condition: str=None) -> list[tuple]:
    query = "SELECT * FROM users"
    if condition:
        query += f"WHERE{condition}"
    try:
        with connection: 
            rows = connection.execute(query).fetchall()
        return rows
    except Exception as e:
        print(e)

def delete_user(connection, user_id:int):
    query = "DELETE FROM users WHERE id = ?"
    try:
        with connection:
            connection.execute(query,(user_id,))
        print(f"USER_ID: {user_id} was deleted")
    except Exception as e:
        print(e)

def update_user(connection, user_id:int ,email:str):
    query = "UPDATE users SET email = ? WHERE id = ?"
    try:
        with connection:
            connection.execute(query,(email,user_id))
        print(f"user id{user_id} has been updated")
    except Exception as e:
        print(e)

def insert_users(connection, users:list[(tuple[str, int ,str])]):
    query = " INSERT INTO users (name,age,email) VALUES (?,?,?)"
    try:
        with connection:
            connection.executemany(query,users)
        print(f"{len(users)} users are added")
    except Exception as e:
        print(e)

def main():
    connection = get_connection("subscribe.db")
    try:
        create_table(connection)

        start = input("enter option (add,delete,update,search,add many): ").lower()
        if start=="add":
            name = input("enter name: ")
            age = int(input("enter age: "))
            email = input("enter email: ") 
            insert_user(connection, name , age , email)
        elif start=="search":
            print("all users: ")
            for user in fetch_users(connection):
                print(user)

        elif start=="delete":
            user_id = int(input("enter user id: "))
            delete_user(connection,user_id)
        
        elif start=="update":
             user_id = int(input("enter user id: "))
             new_email = input("enter new email: ")
             update_user(connection,user_id,new_email)
        
        elif start=="add many":
            users = [("sachin",19,"sachin@gmail.com"),("tarun",19,"tarun@gmail.com")]
            insert_users(connection,users)


    finally:
        connection.close()

if __name__ == "__main__":
    main()