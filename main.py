import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime


# ==================================================
# DATABASE
# ==================================================

def create_database():

    connection = sqlite3.connect("requests.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            request_id TEXT,

            employee_name TEXT,

            category TEXT,

            related_item TEXT,

            problem TEXT,

            priority TEXT,

            status TEXT,

            created_at TEXT,

            remarks TEXT

        )
    """)

    connection.commit()
    connection.close()


# ==================================================
# DATABASE MIGRATION
# ==================================================
# Agar purana database hai to missing columns add karenge

def add_missing_columns():

    connection = sqlite3.connect("requests.db")
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(requests)")

    columns = [
        column[1]
        for column in cursor.fetchall()
    ]

    if "priority" not in columns:

        cursor.execute("""
            ALTER TABLE requests
            ADD COLUMN priority TEXT
        """)

    if "created_at" not in columns:

        cursor.execute("""
            ALTER TABLE requests
            ADD COLUMN created_at TEXT
        """)

    if "remarks" not in columns:

        cursor.execute("""
            ALTER TABLE requests
            ADD COLUMN remarks TEXT
        """)

    connection.commit()
    connection.close()


create_database()
add_missing_columns()


# ==================================================
# MAIN WINDOW
# ==================================================

window = tk.Tk()

window.title("IT Problem Solver")

window.geometry("700x800")

window.resizable(False, False)


# ==================================================
# TITLE
# ==================================================

title = tk.Label(
    window,
    text="IT Problem Solver",
    font=("Arial", 24, "bold")
)

title.pack(pady=20)


subtitle = tk.Label(
    window,
    text="Raise your IT problem",
    font=("Arial", 12)
)

subtitle.pack(pady=5)


# ==================================================
# EMPLOYEE NAME
# ==================================================

name_label = tk.Label(
    window,
    text="Employee Name"
)

name_label.pack(
    anchor="w",
    padx=80,
    pady=(20, 5)
)


name_entry = tk.Entry(
    window,
    width=50
)

name_entry.pack(
    padx=80
)


# ==================================================
# CATEGORY
# ==================================================

category_label = tk.Label(
    window,
    text="Problem Category"
)

category_label.pack(
    anchor="w",
    padx=80,
    pady=(20, 5)
)


category_box = ttk.Combobox(
    window,
    values=[
        "Software",
        "Hardware",
        "Network",
        "Email",
        "Other"
    ],
    width=47,
    state="readonly"
)

category_box.pack(
    padx=80
)


# ==================================================
# RELATED ITEM
# ==================================================

related_label = tk.Label(
    window,
    text="Select Related Item"
)

related_label.pack(
    anchor="w",
    padx=80,
    pady=(20, 5)
)


related_box = ttk.Combobox(
    window,
    width=47,
    state="readonly"
)

related_box.pack(
    padx=80
)


# ==================================================
# CATEGORY OPTIONS
# ==================================================

category_options = {

    "Software": [
        "Outlook",
        "OST",
        "RFMS",
        "PlanSwift",
        "Plugins",
        "Adobe",
        "Cliq",
        "Bluebeam",
        "Other"
    ],

    "Hardware": [
        "CPU",
        "Mouse",
        "Keyboard",
        "Monitor",
        "UPS",
        "Extension Board",
        "Charger",
        "Adapter",
        "Wi-Fi Dongle",
        "Laptop",
        "Laptop Stand",
        "Printer",
        "Other"
    ],

    "Network": [
        "Internet",
        "Wi-Fi",
        "LAN",
        "VPN",
        "RDP",
        "Network Drive",
        "Other"
    ],

    "Email": [
        "Outlook Email",
        "Email Login",
        "Send / Receive",
        "Email Attachment",
        "Email Sync",
        "Other"
    ],

    "Other": [
        "Other"
    ]
}


# ==================================================
# CATEGORY CHANGE
# ==================================================

def category_changed(event):

    selected_category = category_box.get()

    options = category_options.get(
        selected_category,
        []
    )

    related_box["values"] = options

    related_box.set("")


category_box.bind(
    "<<ComboboxSelected>>",
    category_changed
)


# ==================================================
# PRIORITY
# ==================================================

priority_label = tk.Label(
    window,
    text="Priority"
)

priority_label.pack(
    anchor="w",
    padx=80,
    pady=(20, 5)
)


priority_box = ttk.Combobox(
    window,
    values=[
        "Low",
        "Medium",
        "High",
        "Critical"
    ],
    width=47,
    state="readonly"
)

priority_box.pack(
    padx=80
)

priority_box.set("Medium")


# ==================================================
# PROBLEM DESCRIPTION
# ==================================================

problem_label = tk.Label(
    window,
    text="Describe Your Problem"
)

problem_label.pack(
    anchor="w",
    padx=80,
    pady=(20, 5)
)


problem_text = tk.Text(
    window,
    width=50,
    height=6
)

problem_text.pack(
    padx=80
)


# ==================================================
# SUBMIT REQUEST
# ==================================================

def submit_request():

    employee_name = name_entry.get().strip()

    category = category_box.get()

    related_item = related_box.get()

    priority = priority_box.get()

    problem = problem_text.get(
        "1.0",
        tk.END
    ).strip()


    # ==================================================
    # VALIDATION
    # ==================================================

    if employee_name == "":

        messagebox.showwarning(
            "Missing Information",
            "Please enter Employee Name."
        )

        return


    if category == "":

        messagebox.showwarning(
            "Missing Information",
            "Please select Problem Category."
        )

        return


    if related_item == "":

        messagebox.showwarning(
            "Missing Information",
            "Please select Related Item."
        )

        return


    if priority == "":

        messagebox.showwarning(
            "Missing Information",
            "Please select Priority."
        )

        return


    if problem == "":

        messagebox.showwarning(
            "Missing Information",
            "Please describe your problem."
        )

        return


    # ==================================================
    # DATE & TIME
    # ==================================================

    created_at = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )


    # ==================================================
    # DATABASE
    # ==================================================

    try:

        connection = sqlite3.connect(
            "requests.db"
        )

        cursor = connection.cursor()


        cursor.execute("""
            INSERT INTO requests (

                employee_name,

                category,

                related_item,

                problem,

                priority,

                status,

                created_at,

                remarks

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            employee_name,

            category,

            related_item,

            problem,

            priority,

            "New",

            created_at,

            ""

        ))


        database_id = cursor.lastrowid


        # ==================================================
        # REQUEST ID
        # ==================================================

        request_id = f"IT-{database_id}"


        cursor.execute("""
            UPDATE requests

            SET request_id = ?

            WHERE id = ?

        """, (

            request_id,

            database_id

        ))


        connection.commit()

        connection.close()


        # ==================================================
        # SUCCESS
        # ==================================================

        messagebox.showinfo(

            "Request Submitted",

            f"Your IT request has been submitted successfully!\n\n"

            f"Request ID: {request_id}\n"

            f"Priority: {priority}"

        )


        # ==================================================
        # CLEAR FORM
        # ==================================================

        name_entry.delete(
            0,
            tk.END
        )

        category_box.set("")

        related_box.set("")

        related_box["values"] = []

        priority_box.set("Medium")

        problem_text.delete(
            "1.0",
            tk.END
        )


    except Exception as error:

        messagebox.showerror(

            "Database Error",

            f"Request save nahi hui.\n\n{error}"

        )


# ==================================================
# BUTTON
# ==================================================

submit_button = tk.Button(

    window,

    text="Raise Request",

    width=20,

    height=2,

    command=submit_request

)

submit_button.pack(
    pady=25
)


# ==================================================
# START
# ==================================================

window.mainloop()