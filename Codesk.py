import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import mysql.connector as sqLtor
import os
import matplotlib.pyplot as plt

# =========================================================
# DATABASE SETTINGS
# =========================================================
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "YnR#2039`~@"
DB_NAME = "studio"

VALID_STATUS = ["Draft", "Planning", "In-Progress", "Complete"]

mycon = None


def connect_database():
    global mycon

    try:
        # Connect to MySQL server first
        mycon = sqLtor.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWORD
        )

        cur = mycon.cursor()

        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cur.execute(f"USE {DB_NAME}")

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
        cur.close()
        return True

    except sqLtor.Error as e:
        messagebox.showerror(
            "Database Error",
            "Could not connect to MySQL.\n\n" + str(e)
        )
        return False


# =========================================================
# DATABASE FUNCTIONS
# =========================================================
def signup_user(username, password):
    if not username or not password:
        return False, "Username and password cannot be empty."

    cur = mycon.cursor()

    try:
        qry = """
        INSERT INTO Users (Username, Password)
        VALUES (%s, %s)
        """
        cur.execute(qry, (username, password))
        mycon.commit()
        return True, "Account created successfully!"

    except sqLtor.IntegrityError:
        return False, "Username already exists."

    except sqLtor.Error as e:
        return False, str(e)

    finally:
        cur.close()


def signin_user(username, password):
    cur = mycon.cursor()

    try:
        qry = """
        SELECT User_ID
        FROM Users
        WHERE Username = %s AND Password = %s
        """
        cur.execute(qry, (username, password))
        user = cur.fetchone()

        if user:
            return user[0]

        return None

    finally:
        cur.close()


def get_projects(user_id, search_field=None, search_value=None):
    columns = """
        Project_ID, Title, Category, Langs, Status,
        Description, Date_created, File_Path
    """

    qry = f"""
    SELECT {columns}
    FROM Projects
    WHERE User_ID = %s
    """

    params = [user_id]

    if search_field:
        qry += f" AND {search_field} LIKE %s"
        params.append("%" + search_value + "%")

    qry += " ORDER BY Project_ID"

    cur = mycon.cursor()
    try:
        cur.execute(qry, tuple(params))
        return cur.fetchall()
    finally:
        cur.close()


# =========================================================
# SIGN UP WINDOW
# =========================================================
class SignupWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Create Account")
        self.geometry("400x300")
        self.resizable(False, False)

        ttk.Label(
            self,
            text="CREATE ACCOUNT",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        form = ttk.Frame(self)
        form.pack(pady=10)

        ttk.Label(form, text="Username:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.username = ttk.Entry(form, width=28)
        self.username.grid(row=0, column=1)

        ttk.Label(form, text="Password:").grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )
        self.password = ttk.Entry(form, width=28, show="*")
        self.password.grid(row=1, column=1)

        ttk.Label(form, text="Confirm Password:").grid(
            row=2, column=0, padx=10, pady=10, sticky="w"
        )
        self.confirm = ttk.Entry(form, width=28, show="*")
        self.confirm.grid(row=2, column=1)

        ttk.Button(
            self,
            text="Create Account",
            command=self.create_account
        ).pack(pady=20)

    def create_account(self):
        username = self.username.get().strip()
        password = self.password.get()
        confirm = self.confirm.get()

        if password != confirm:
            messagebox.showerror(
                "Error",
                "Passwords do not match.",
                parent=self
            )
            return

        success, message = signup_user(username, password)

        if success:
            messagebox.showinfo(
                "Success",
                message,
                parent=self
            )
            self.destroy()
        else:
            messagebox.showerror(
                "Sign Up Failed",
                message,
                parent=self
            )


# =========================================================
# LOGIN WINDOW
# =========================================================
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Coding Portfolio Management System")
        self.geometry("500x430")
        self.resizable(False, False)

        self.dashboard = None

        ttk.Label(
            self,
            text="CODING PORTFOLIO",
            font=("Arial", 24, "bold")
        ).pack(pady=(45, 5))

        ttk.Label(
            self,
            text="MANAGEMENT SYSTEM",
            font=("Arial", 15)
        ).pack(pady=(0, 30))

        form = ttk.Frame(self)
        form.pack()

        ttk.Label(form, text="Username:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )

        self.username = ttk.Entry(form, width=30)
        self.username.grid(row=0, column=1, padx=10)

        ttk.Label(form, text="Password:").grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )

        self.password = ttk.Entry(form, width=30, show="*")
        self.password.grid(row=1, column=1, padx=10)

        ttk.Button(
            self,
            text="Sign In",
            command=self.signin
        ).pack(pady=(25, 8))

        ttk.Button(
            self,
            text="Create New Account",
            command=self.open_signup
        ).pack()

        ttk.Button(
            self,
            text="Exit",
            command=self.destroy
        ).pack(pady=15)

    def open_signup(self):
        SignupWindow(self)

    def signin(self):
        username = self.username.get().strip()
        password = self.password.get()

        if not username or not password:
            messagebox.showwarning(
                "Missing Information",
                "Enter both username and password.",
                parent=self
            )
            return

        user_id = signin_user(username, password)

        if user_id is None:
            messagebox.showerror(
                "Sign In Failed",
                "Incorrect username or password.",
                parent=self
            )
            return

        self.withdraw()

        self.dashboard = PortfolioWindow(
            self,
            user_id,
            username
        )


# =========================================================
# MAIN PORTFOLIO WINDOW
# =========================================================
class PortfolioWindow(tk.Toplevel):
    def __init__(self, login_window, user_id, username):
        super().__init__(login_window)

        self.login_window = login_window
        self.user_id = user_id
        self.username = username

        self.title("Coding Portfolio Management System")
        self.geometry("1250x700")
        self.minsize(1000, 600)

        self.protocol("WM_DELETE_WINDOW", self.logout)

        self.create_widgets()
        self.load_projects()

    # -----------------------------------------------------
    # GUI
    # -----------------------------------------------------
    def create_widgets(self):
        header = ttk.Frame(self, padding=15)
        header.pack(fill="x")

        ttk.Label(
            header,
            text="CODING PORTFOLIO MANAGEMENT SYSTEM",
            font=("Arial", 20, "bold")
        ).pack(side="left")

        ttk.Label(
            header,
            text=f"Welcome, {self.username}!",
            font=("Arial", 11)
        ).pack(side="right")

        toolbar = ttk.Frame(self, padding=(15, 0, 15, 10))
        toolbar.pack(fill="x")

        ttk.Button(
            toolbar,
            text="Add Project",
            command=self.add_project
        ).pack(side="left", padx=3)

        ttk.Button(
            toolbar,
            text="Modify",
            command=self.modify_project
        ).pack(side="left", padx=3)

        ttk.Button(
            toolbar,
            text="Delete",
            command=self.delete_project
        ).pack(side="left", padx=3)

        ttk.Button(
            toolbar,
            text="Open File",
            command=self.open_file
        ).pack(side="left", padx=3)

        ttk.Button(
            toolbar,
            text="Statistics",
            command=self.statistics
        ).pack(side="left", padx=3)

        ttk.Button(
            toolbar,
            text="Export CSV",
            command=self.export_csv
        ).pack(side="left", padx=3)

        ttk.Button(
            toolbar,
            text="Refresh",
            command=self.load_projects
        ).pack(side="left", padx=3)

        ttk.Button(
            toolbar,
            text="Logout",
            command=self.logout
        ).pack(side="right", padx=3)

        # Search area
        search_frame = ttk.LabelFrame(
            self,
            text="Search Projects",
            padding=10
        )
        search_frame.pack(fill="x", padx=15, pady=5)

        self.search_type = ttk.Combobox(
            search_frame,
            values=[
                "Project ID",
                "Title",
                "Category",
                "Language",
                "Status"
            ],
            state="readonly",
            width=18
        )
        self.search_type.set("Title")
        self.search_type.pack(side="left", padx=5)

        self.search_entry = ttk.Entry(
            search_frame,
            width=40
        )
        self.search_entry.pack(side="left", padx=5)

        ttk.Button(
            search_frame,
            text="Search",
            command=self.search_projects
        ).pack(side="left", padx=5)

        ttk.Button(
            search_frame,
            text="Show All",
            command=self.load_projects
        ).pack(side="left", padx=5)

        # Table
        table_frame = ttk.Frame(self, padding=15)
        table_frame.pack(fill="both", expand=True)

        columns = (
            "Project_ID",
            "Title",
            "Category",
            "Langs",
            "Status",
            "Description",
            "Date_created",
            "File_Path"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "Project_ID": "ID",
            "Title": "Title",
            "Category": "Category",
            "Langs": "Languages",
            "Status": "Status",
            "Description": "Description",
            "Date_created": "Date Created",
            "File_Path": "File Path"
        }

        widths = {
            "Project_ID": 60,
            "Title": 150,
            "Category": 110,
            "Langs": 120,
            "Status": 100,
            "Description": 220,
            "Date_created": 100,
            "File_Path": 260
        }

        for column in columns:
            self.tree.heading(
                column,
                text=headings[column]
            )
            self.tree.column(
                column,
                width=widths[column],
                anchor="w"
            )

        y_scroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        x_scroll = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        y_scroll.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        x_scroll.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree.bind(
            "<Double-1>",
            lambda event: self.modify_project()
        )

    # -----------------------------------------------------
    # PROJECT TABLE
    # -----------------------------------------------------
    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def insert_records(self, records):
        self.clear_table()

        for row in records:
            self.tree.insert(
                "",
                "end",
                values=row
            )

    def load_projects(self):
        try:
            records = get_projects(self.user_id)
            self.insert_records(records)

        except sqLtor.Error as e:
            messagebox.showerror(
                "Database Error",
                str(e),
                parent=self
            )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------
    def search_projects(self):
        value = self.search_entry.get().strip()

        if not value:
            self.load_projects()
            return

        field_map = {
            "Project ID": "Project_ID",
            "Title": "Title",
            "Category": "Category",
            "Language": "Langs",
            "Status": "Status"
        }

        field = field_map[self.search_type.get()]

        records = get_projects(
            self.user_id,
            field,
            value
        )

        self.insert_records(records)

        if not records:
            messagebox.showinfo(
                "Search",
                "No projects found.",
                parent=self
            )

    # -----------------------------------------------------
    # GET SELECTED PROJECT
    # -----------------------------------------------------
    def get_selected_project(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Project Selected",
                "Select a project first.",
                parent=self
            )
            return None

        values = self.tree.item(
            selected[0],
            "values"
        )

        return values

    # -----------------------------------------------------
    # ADD PROJECT
    # -----------------------------------------------------
    def add_project(self):
        ProjectDialog(
            self,
            "Add Project",
            self.user_id,
            self.refresh_after_change
        )

    # -----------------------------------------------------
    # MODIFY PROJECT
    # -----------------------------------------------------
    def modify_project(self):
        project = self.get_selected_project()

        if project is None:
            return

        ProjectDialog(
            self,
            "Modify Project",
            self.user_id,
            self.refresh_after_change,
            project
        )

    # -----------------------------------------------------
    # DELETE PROJECT
    # -----------------------------------------------------
    def delete_project(self):
        project = self.get_selected_project()

        if project is None:
            return

        project_id = project[0]
        title = project[1]

        answer = messagebox.askyesno(
            "Delete Project",
            f"Delete project '{title}' (ID {project_id})?",
            parent=self
        )

        if not answer:
            return

        cur = mycon.cursor()

        try:
            qry = """
            DELETE FROM Projects
            WHERE Project_ID = %s AND User_ID = %s
            """

            cur.execute(
                qry,
                (project_id, self.user_id)
            )

            mycon.commit()

            if cur.rowcount > 0:
                messagebox.showinfo(
                    "Deleted",
                    "Project deleted successfully.",
                    parent=self
                )
                self.load_projects()
            else:
                messagebox.showwarning(
                    "Not Found",
                    "Project was not found.",
                    parent=self
                )

        except sqLtor.Error as e:
            messagebox.showerror(
                "Database Error",
                str(e),
                parent=self
            )

        finally:
            cur.close()

    # -----------------------------------------------------
    # OPEN FILE
    # -----------------------------------------------------
    def open_file(self):
        project = self.get_selected_project()

        if project is None:
            return

        file_path = project[7]

        if not file_path:
            messagebox.showinfo(
                "No File",
                "No file is associated with this project.",
                parent=self
            )
            return

        if not os.path.exists(file_path):
            messagebox.showerror(
                "File Not Found",
                "The associated file could not be found.",
                parent=self
            )
            return

        try:
            os.startfile(file_path)
        except Exception as e:
            messagebox.showerror(
                "Open File Error",
                str(e),
                parent=self
            )

    # -----------------------------------------------------
    # STATISTICS
    # -----------------------------------------------------
    def statistics(self):
        records = get_projects(self.user_id)

        if not records:
            messagebox.showinfo(
                "Statistics",
                "No projects available.",
                parent=self
            )
            return

        columns = [
            "Project_ID",
            "Title",
            "Category",
            "Langs",
            "Status",
            "Description",
            "Date_created",
            "File_Path"
        ]

        mydf = pd.DataFrame(
            records,
            columns=columns
        )

        mydf["Date_created"] = pd.to_datetime(
            mydf["Date_created"]
        )

        total = len(mydf)

        status_text = mydf["Status"].value_counts().to_string()
        category_text = mydf["Category"].value_counts().to_string()
        language_text = mydf["Langs"].value_counts().to_string()

        latest = mydf.loc[
            mydf["Date_created"].idxmax()
        ]

        oldest = mydf.loc[
            mydf["Date_created"].idxmin()
        ]

        message = (
            f"Total Projects: {total}\n\n"
            f"Projects by Status:\n{status_text}\n\n"
            f"Projects by Category:\n{category_text}\n\n"
            f"Projects by Programming Language:\n{language_text}\n\n"
            f"Latest Project:\n"
            f"{latest['Title']} - {latest['Date_created'].date()}\n\n"
            f"Oldest Project:\n"
            f"{oldest['Title']} - {oldest['Date_created'].date()}"
        )

        StatisticsWindow(
            self,
            mydf,
            message
        )

    # -----------------------------------------------------
    # EXPORT CSV
    # -----------------------------------------------------
    def export_csv(self):
        records = get_projects(self.user_id)

        if not records:
            messagebox.showinfo(
                "Export",
                "There are no projects to export.",
                parent=self
            )
            return

        columns = [
            "Project_ID",
            "Title",
            "Category",
            "Langs",
            "Status",
            "Description",
            "Date_created",
            "File_Path"
        ]

        mydf = pd.DataFrame(
            records,
            columns=columns
        )

        filename = filedialog.asksaveasfilename(
            parent=self,
            title="Export Portfolio",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )

        if not filename:
            return

        mydf.to_csv(
            filename,
            index=False
        )

        messagebox.showinfo(
            "Export Successful",
            f"Projects exported to:\n{filename}",
            parent=self
        )

    # -----------------------------------------------------
    # REFRESH
    # -----------------------------------------------------
    def refresh_after_change(self):
        self.load_projects()

    # -----------------------------------------------------
    # LOGOUT
    # -----------------------------------------------------
    def logout(self):
        answer = messagebox.askyesno(
            "Logout",
            "Do you want to log out?",
            parent=self
        )

        if answer:
            self.destroy()
            self.login_window.deiconify()


# =========================================================
# ADD / MODIFY PROJECT DIALOG
# =========================================================
class ProjectDialog(tk.Toplevel):
    def __init__(
        self,
        parent,
        title,
        user_id,
        refresh_callback,
        project=None
    ):
        super().__init__(parent)

        self.parent = parent
        self.user_id = user_id
        self.refresh_callback = refresh_callback
        self.project = project

        self.title(title)
        self.geometry("550x550")
        self.resizable(False, False)

        self.create_widgets()

        if project:
            self.load_project(project)

    def create_widgets(self):
        ttk.Label(
            self,
            text=self.title(),
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        form = ttk.Frame(self, padding=15)
        form.pack(fill="both", expand=True)

        labels = [
            "Project ID:",
            "Title:",
            "Category:",
            "Languages:",
            "Status:",
            "Description:",
            "Date Created:",
            "File Path:"
        ]

        self.entries = {}

        for row, label in enumerate(labels):
            ttk.Label(
                form,
                text=label
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=8,
                pady=8
            )

        self.entries["Project_ID"] = ttk.Entry(
            form,
            width=38
        )
        self.entries["Project_ID"].grid(row=0, column=1)

        self.entries["Title"] = ttk.Entry(
            form,
            width=38
        )
        self.entries["Title"].grid(row=1, column=1)

        self.entries["Category"] = ttk.Entry(
            form,
            width=38
        )
        self.entries["Category"].grid(row=2, column=1)

        self.entries["Langs"] = ttk.Entry(
            form,
            width=38
        )
        self.entries["Langs"].grid(row=3, column=1)

        self.status = ttk.Combobox(
            form,
            values=VALID_STATUS,
            state="readonly",
            width=35
        )
        self.status.set("Draft")
        self.status.grid(row=4, column=1)

        self.entries["Description"] = ttk.Entry(
            form,
            width=38
        )
        self.entries["Description"].grid(row=5, column=1)

        self.entries["Date_created"] = ttk.Entry(
            form,
            width=38
        )
        self.entries["Date_created"].grid(row=6, column=1)

        path_frame = ttk.Frame(form)
        path_frame.grid(
            row=7,
            column=1,
            sticky="ew"
        )

        self.entries["File_Path"] = ttk.Entry(
            path_frame,
            width=28
        )
        self.entries["File_Path"].pack(
            side="left"
        )

        ttk.Button(
            path_frame,
            text="Browse",
            command=self.browse_file
        ).pack(
            side="left",
            padx=5
        )

        if self.project:
            self.entries["Project_ID"].configure(
                state="disabled"
            )

        ttk.Button(
            self,
            text="Save",
            command=self.save
        ).pack(
            pady=20
        )

    def load_project(self, project):
        names = [
            "Project_ID",
            "Title",
            "Category",
            "Langs",
            "Status",
            "Description",
            "Date_created",
            "File_Path"
        ]

        for i, name in enumerate(names):
            if name == "Status":
                self.status.set(project[i])
            else:
                self.entries[name].insert(
                    0,
                    "" if project[i] is None else str(project[i])
                )

    def browse_file(self):
        filename = filedialog.askopenfilename(
            parent=self
        )

        if filename:
            self.entries["File_Path"].delete(
                0,
                tk.END
            )
            self.entries["File_Path"].insert(
                0,
                filename
            )

    def save(self):
        project_id = self.entries["Project_ID"].get().strip()
        title = self.entries["Title"].get().strip()
        category = self.entries["Category"].get().strip()
        langs = self.entries["Langs"].get().strip()
        status = self.status.get()
        description = self.entries["Description"].get().strip()
        date_created = self.entries["Date_created"].get().strip()
        file_path = self.entries["File_Path"].get().strip()

        if not project_id:
            messagebox.showerror(
                "Error",
                "Project ID is required.",
                parent=self
            )
            return

        try:
            project_id = int(project_id)
        except ValueError:
            messagebox.showerror(
                "Error",
                "Project ID must be a number.",
                parent=self
            )
            return

        if status not in VALID_STATUS:
            messagebox.showerror(
                "Error",
                "Please select a valid status.",
                parent=self
            )
            return

        if not description:
            messagebox.showerror(
                "Error",
                "Description is required.",
                parent=self
            )
            return

        if not date_created:
            messagebox.showerror(
                "Error",
                "Date Created is required.",
                parent=self
            )
            return

        cur = mycon.cursor()

        try:
            if self.project is None:
                qry = """
                INSERT INTO Projects
                (
                    Project_ID,
                    User_ID,
                    Title,
                    Category,
                    Langs,
                    Status,
                    Description,
                    Date_created,
                    File_Path
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """

                cur.execute(
                    qry,
                    (
                        project_id,
                        self.user_id,
                        title,
                        category,
                        langs,
                        status,
                        description,
                        date_created,
                        file_path
                    )
                )

                mycon.commit()

                messagebox.showinfo(
                    "Success",
                    "Project added successfully.",
                    parent=self
                )

            else:
                qry = """
                UPDATE Projects
                SET
                    Title = %s,
                    Category = %s,
                    Langs = %s,
                    Status = %s,
                    Description = %s,
                    Date_created = %s,
                    File_Path = %s
                WHERE Project_ID = %s
                AND User_ID = %s
                """

                cur.execute(
                    qry,
                    (
                        title,
                        category,
                        langs,
                        status,
                        description,
                        date_created,
                        file_path,
                        project_id,
                        self.user_id
                    )
                )

                mycon.commit()

                messagebox.showinfo(
                    "Success",
                    "Project modified successfully.",
                    parent=self
                )

            self.refresh_callback()
            self.destroy()

        except sqLtor.IntegrityError as e:
            messagebox.showerror(
                "Database Error",
                "Project ID may already exist.\n\n" + str(e),
                parent=self
            )

        except sqLtor.Error as e:
            messagebox.showerror(
                "Database Error",
                str(e),
                parent=self
            )

        finally:
            cur.close()


# =========================================================
# STATISTICS WINDOW
# =========================================================
class StatisticsWindow(tk.Toplevel):
    def __init__(self, parent, mydf, summary):
        super().__init__(parent)

        self.title("Portfolio Statistics")
        self.geometry("700x600")

        self.mydf = mydf

        ttk.Label(
            self,
            text="PORTFOLIO STATISTICS",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        text = tk.Text(
            self,
            width=75,
            height=20,
            wrap="word"
        )
        text.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        text.insert(
            "1.0",
            summary
        )

        text.configure(
            state="disabled"
        )

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Status Graph",
            command=self.status_graph
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Category Graph",
            command=self.category_graph
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Language Graph",
            command=self.language_graph
        ).pack(side="left", padx=5)

    def status_graph(self):
        counts = self.mydf["Status"].value_counts()

        plt.figure()
        plt.bar(
            counts.index,
            counts.values
        )
        plt.title("Projects by Status")
        plt.xlabel("Status")
        plt.ylabel("No. of Projects")
        plt.xticks(rotation=20)
        plt.tight_layout()
        plt.show()

    def category_graph(self):
        counts = self.mydf["Category"].value_counts()

        plt.figure()
        plt.pie(
            counts.values,
            labels=counts.index,
            autopct="%1.1f%%"
        )
        plt.title("Category of Projects")
        plt.show()

    def language_graph(self):
        counts = self.mydf["Langs"].value_counts()

        plt.figure()
        plt.pie(
            counts.values,
            labels=counts.index,
            autopct="%1.1f%%"
        )
        plt.title("Languages Used")
        plt.show()


# =========================================================
# PROGRAM START
# =========================================================
if __name__ == "__main__":

    if connect_database():

        app = LoginWindow()

        def close_program():
            try:
                if mycon and mycon.is_connected():
                    mycon.close()
            except Exception:
                pass
            app.destroy()

        app.protocol(
            "WM_DELETE_WINDOW",
            close_program
        )

        app.mainloop()
