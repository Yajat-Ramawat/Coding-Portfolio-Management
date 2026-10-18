import pandas as pd
import mysql.connector as sqLtor
import os
import matplotlib.pyplot as plt

mycon = sqLtor.connect(host = "localhost", user="root",passwd = "YOUR_MYSQL_PASSWORD")

cur = mycon.cursor()

cur.execute("CREATE DATABASE IF NOT EXISTS studio")
cur.execute("USE studio")

cur.execute("""
CREATE TABLE IF NOT EXISTS Users (
    User_ID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(30) UNIQUE NOT NULL,
    Password VARCHAR(50) NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Projects (
    Project_ID INT PRIMARY KEY,
    User_ID INT NOT NULL,
    Title VARCHAR(50) DEFAULT 'Unnamed project',
    Category VARCHAR(30) DEFAULT 'Not defined',
    Langs VARCHAR(50),
    Status VARCHAR(30) NOT NULL DEFAULT 'Draft',
    Description VARCHAR(100) NOT NULL,
    Date_created DATE NOT NULL,
    File_Path VARCHAR(260),
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID)
)
""")

mycon.commit()

valid_status = ['Draft','Planning', 'In-Progress', 'Complete']

def main_menu():
    while True:
        print("======================================\nCODING PORTFOLIO MANAGEMENT SYSTEM\n======================================\n")
        choice = int(input("Enter You Choice: \n 1. Sign Up \n 2. Sign In \n 3. Exit\n"))
        print("\n========================================")
        if choice == 1:
            signup()
        elif choice == 2:
            return signin()
        else:
            break

def signup():
    print("\n========== SIGN UP ==========")

    username = input("Create Username: ")
    password = input("Create Password: ")

    cur = mycon.cursor()

    try:
        qry = """
        INSERT INTO Users (Username, Password)
        VALUES (%s, %s)
        """

        cur.execute(qry, (username, password))

        mycon.commit()

        print("Account created successfully!")

    except sqLtor.IntegrityError:
        print("Username already exists!")

    print("=============================")

def signin():
    print("\n========== SIGN IN ==========")

    username = input("Username: ")
    password = input("Password: ")

    cur = mycon.cursor()

    qry = """
    SELECT User_ID FROM Users
    WHERE Username = %s AND Password = %s
    """

    cur.execute(qry, (username, password))

    user = cur.fetchone()

    if user:
        return user[0]
    else:
        return None


def seeall(user_id):
    print("========== PROJECTs ==========")
    mydf = pd.read_sql("SELECT Project_ID, Title, Category, Langs, Status,Description, Date_created, File_Path FROM Projects WHERE User_ID = %s",mycon,params=(user_id,))
    print(mydf)
    print("\n========================================")

def search(user_id):

    print("========== SEARCH PROJECTS ==========")
    print("1. Search by Project ID")
    print("2. Search by Title")
    print("3. Search by Category")
    print("4. Search by Language")
    print("5. Search by Status")

    choice = int(input("Enter your choice: "))

    cur = mycon.cursor()

    if choice == 1:
        project_id = int(input("Enter Project ID: "))

        qry = """
        SELECT Project_ID, Title, Category, Langs, Status,Description, Date_created, File_Path FROM Projects
        WHERE Project_ID = %s AND User_ID = %s
        """

        cur.execute(qry, (project_id, user_id))

    elif choice == 2:
        title = input("Enter Title: ")

        qry = """
        SELECT Project_ID, Title, Category, Langs, Status,Description, Date_created, File_Path FROM Projects
        WHERE Title LIKE %s AND User_ID = %s
        """

        cur.execute(qry, ("%" + title + "%", user_id))

    elif choice == 3:
        category = input("Enter Category: ")

        qry = """
        SELECT Project_ID, Title, Category, Langs, Status,Description, Date_created, File_Path FROM Projects
        WHERE Category LIKE %s AND User_ID = %s
        """

        cur.execute(qry, ("%" + category + "%", user_id))

    elif choice == 4:
        langs = input("Enter Programming Language: ")

        qry = """
        SELECT Project_ID, Title, Category, Langs, Status,Description, Date_created, File_Path FROM Projects
        WHERE Langs LIKE %s AND User_ID = %s
        """

        cur.execute(qry, ("%" + langs + "%", user_id))

    elif choice == 5:
        status = input("Enter Status: ")

        qry = """
        SELECT Project_ID, Title, Category, Langs, Status,Description, Date_created, File_Path FROM Projects
        WHERE Status LIKE %s AND User_ID = %s
        """

        cur.execute(qry, ("%" + status + "%", user_id))

    else:
        print("Invalid choice!")
        return

    records = cur.fetchall()

    if len(records) == 0:

        print("No projects found!")

    else:

        print("\n========== SEARCH RESULTS ==========")

        for i, row in enumerate(records, start=1):
            print("\n", i, ".", row)

        print("\n========================================")

        # If there is only one result, select it automatically
        if len(records) == 1:

            selected_project = records[0]

        else:

            project_choice = int(
                input("\nWhich project do you want to select? ")
            )

            if project_choice < 1 or project_choice > len(records):
                print("Invalid project choice!")
                return

            selected_project = records[project_choice - 1]

        print("\nSelected Project:")
        print(selected_project)

        search_choice = input(
            "\nNext Step?:\n"
            "1. Open File\n"
            "2. Modify\n"
            "3. Back\n"
            "Enter choice: "
        )

        if search_choice == "1":

            file_path = selected_project[-1]

            if file_path:

                if os.path.exists(file_path):

                    os.startfile(file_path)
                    print("File opened successfully!")

                else:

                    print("The associated file could not be found!")

            else:

                print("No file is associated with this project!")

        elif search_choice == "2":

            modify(user_id, selected_project[0])

        elif search_choice == "3":

            return

        else:

            print("Invalid choice!")

    print("\n========================================")

def add(user_id):
    print("========== ADD PROJECT ==========")
    project_id = int(input("Enter Project ID: "))
    title = input("Enter Project Title: ")
    category = input("Enter Category: ")
    langs = input("Enter Languages Used: ")
    status = input("Enter Status: ")

    if status not in valid_status:
        print("Error! Invalid Status!")
        print("Failed to add the Project!")
        return

    description = input("Enter description: ")
    date_created = input("Enter Date Created (YYYY-MM-DD): ")
    file_path = input("Enter the File Path: ")

    qry = """INSERT INTO Projects(Project_ID, User_ID, Title, Category, Langs, Status, description, Date_created, file_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    cur = mycon.cursor()
    cur.execute(qry, (project_id, user_id, title, category, langs, status, description, date_created, file_path))
    mycon.commit()

    print("Project added successfully!")
    print("\n========================================")

def modify(user_id, project_id = None):
    print("========== MODIFY PROJECT ==========")
    if project_id is None:
        project_id = int(input("Enter Project ID of the project to modify: "))

    print("What do you want to modify?\n1. Title\n2. Category\n3. Language\n4. Status\n5. description\n6. Date Created\n 7. File Path")

    choice = int(input("Enter your choice: "))

    cur = mycon.cursor()

    if choice == 1:
        new_value = input("Enter new Title: ")
        qry = "UPDATE Projects SET Title = %s WHERE Project_ID = %s AND User_ID = %s"
        cur.execute(qry, (new_value, project_id,user_id))

    elif choice == 2:
        new_value = input("Enter new Category: ")
        qry = "UPDATE Projects SET Category = %s WHERE Project_ID = %s AND User_ID = %s"
        cur.execute(qry, (new_value, project_id,user_id))

    elif choice == 3:
        new_value = input("Enter new Language: ")
        qry = "UPDATE Projects SET Langs = %s WHERE Project_ID = %s AND User_ID = %s"
        cur.execute(qry, (new_value, project_id,user_id))

    elif choice == 4:
        new_value = input("Enter new Status: ")
        
        if new_value not in valid_status:
            print("Error! Invalid Status! \n Modify to correct!")
            return

        qry = "UPDATE Projects SET Status = %s WHERE Project_ID = %s AND User_ID = %s"
        cur.execute(qry, (new_value, project_id,user_id))

    elif choice == 5:
        new_value = input("Enter new description: ")
        qry = "UPDATE Projects SET description = %s WHERE Project_ID = %s AND User_ID = %s"
        cur.execute(qry, (new_value, project_id,user_id))

    elif choice == 6:
        new_value = input("Enter new Date (YYYY-MM-DD): ")
        qry = "UPDATE Projects SET Date_created = %s WHERE Project_ID = %s AND User_ID = %s"
        cur.execute(qry, (new_value, project_id,user_id))

    elif choice == 7:
        new_value = input("Enter new File Path: ")
        qry = "UPDATE Projects SET file_path = %s WHERE Project_ID = %s AND User_ID = %s"
        cur.execute(qry, (new_value, project_id,user_id))

    else:
        print("Invalid choice!")
        return

    mycon.commit()

    if cur.rowcount > 0:
        print("Project modified successfully!")
    else:
        print("Project ID not found!")
    print("\n========================================")

def statistics(user_id):

    mydf = pd.read_sql("SELECT * FROM Projects WHERE user_id = %s", mycon, params=(user_id,))

    print("========== PORTFOLIO STATISTICS ==========")

    # Total projects
    print("Total Projects:", len(mydf))

    # Projects by status
    print("\nProjects by Status:")
    print(mydf["Status"].value_counts())

    # Projects by category
    print("\nProjects by Category:")
    print(mydf["Category"].value_counts())

    print("\nProjects by Programming languages:")
    print(mydf["Langs"].value_counts())

    # Latest project
    if not mydf.empty:
        latest = mydf.loc[mydf["Date_created"].idxmax()]
        print("\nLatest Project:")
        print(latest["Title"])
        print("Created:", latest["Date_created"])

    # Oldest project
    if not mydf.empty:
        oldest = mydf.loc[mydf["Date_created"].idxmin()]
        print("\nOldest Project:")
        print(oldest["Title"])
        print("Created:", oldest["Date_created"])

    grf = input("Show the Graph? (Y/N): ")
    if grf.upper() == 'Y':
        grf_choice = int(input("Select one of the following: \n 1. Status \n 2. Category\n 3. Languages used\n"))
        if grf_choice == 1:
            status_counts =mydf["Status"].value_counts()
            plt.bar(status_counts.index, status_counts.values)
            plt.title("Project by Status")
            plt.xlabel("Status")
            plt.ylabel("No. of Projects")
            plt.grid(True)
            save_ask = input("Show this Graph? (Y/N):")
            if save_ask.upper() == 'Y':
                plt.savefig('status_graph.pdf')
            else:
                return
            plt.show()


        elif grf_choice == 2:
            category_counts = mydf["Category"].value_counts()
            plt.pie(category_counts.values, labels = category_counts.index, autopct="%1.1f%%")
            plt.title("Category of Projects")
            save_ask = input("Show this Graph (Y/N):")
            if save_ask.upper() == 'Y':
                plt.savefig('category_graph.pdf')
            else:
                return
            plt.show()

        elif grf_choice == 3:
            language_counts = mydf["Langs"].value_counts()
            plt.pie(language_counts.values, labels = language_counts.index, autopct="%1.1f%%")
            plt.title("Languages Used")
            save_ask = input("Show this Graph (Y/N):")
            if save_ask.upper() == 'Y':
                plt.savefig('langs_graph.pdf')
            else:
                return
            plt.show()

        else:
            print("Invaild input!")

    else:
        return

    print("\n========================================")

def export(user_id):
    mydf = pd.read_sql("SELECT * FROM Projects WHERE user_ID = %s", mycon, params=(user_id,))
    mydf.to_csv("Projects.csv", index=False)
    print("Projects exported to Projects.csv successfully!")

def delete(user_id):
    print("========== DELETE PROJECT ==========")
    project_id = int(input("Enter Project ID of the project to delete: "))

    qry = "DELETE FROM Projects WHERE Project_ID = %s AND User_ID = %s"

    cur = mycon.cursor()
    cur.execute(qry, (project_id, user_id))
    mycon.commit()

    if cur.rowcount > 0:
        print("Project deleted successfully!")
    else:
        print("Project ID not found!")
    print("\n========================================")

if mycon.is_connected():
    print("Connection Successful!")
    user_id = main_menu()
    if user_id is not None:
      
        print("Entry granted!")
        running = True

        while running == True:
            print(f"Welcome :D!")
            print("======================================\nCODING PORTFOLIO MANAGEMENT SYSTEM\n======================================\n")
            choice = int(input("Enter You Choice: \n 1. See All \n 2. Search \n 3. Add \n 4. Modify\n5. Delete\n6.Statistics\n7.Export in CSV.\n8.Exit\n"))
            if choice == 1:
                seeall(user_id)
            elif choice == 2:
                search(user_id)
            elif choice == 3:
                add(user_id)
            elif choice == 4:
                modify(user_id)
            elif choice == 5:
                delete(user_id)
            elif choice == 6:
                statistics(user_id)
            elif choice == 7:
                export(user_id)
            elif choice == 8:
                running = False
                break
            else:
                print("Wrong Input!")

        
    else:
        print("Incorrect Username or password!")


else:
    print("Error")