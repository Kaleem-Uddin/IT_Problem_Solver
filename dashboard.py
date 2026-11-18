import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
# ==================================================
# DATABASE AND HISTORY TABLE
# ==================================================
def setup_database():
    connection = sqlite3.connect("requests.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS request_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT,
            action TEXT,
            details TEXT,
            changed_at TEXT
        )
    """)
    # Add assigned_to to existing databases without deleting any data.
    cursor.execute("PRAGMA table_info(requests)")
    request_columns = [column[1] for column in cursor.fetchall()]
    if "assigned_to" not in request_columns:
        cursor.execute("ALTER TABLE requests ADD COLUMN assigned_to TEXT")

    # Create a Request Created history entry for requests
    # that do not have one yet, including older requests.
    cursor.execute("""
        SELECT request_id, created_at
        FROM requests
    """)
    requests = cursor.fetchall()
    for request_id, created_at in requests:
        cursor.execute("""
            SELECT id
            FROM request_history
            WHERE request_id = ?
            AND action = 'Request Created'
        """, (request_id,))
        if cursor.fetchone() is None:
            history_time = created_at or datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            )
            cursor.execute("""
                INSERT INTO request_history
                (request_id, action, details, changed_at)
                VALUES (?, ?, ?, ?)
            """, (
                request_id,
                "Request Created",
                "Employee raised a new IT request.",
                history_time
            ))
    connection.commit()
    connection.close()
def get_requests():
    connection = sqlite3.connect("requests.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            request_id,
            employee_name,
            category,
            related_item,
            problem,
            priority,
            status,
            created_at,
            remarks,
            assigned_to
        FROM requests
        ORDER BY id DESC
    """)
    requests = cursor.fetchall()
    connection.close()
    return requests
def add_history(request_id, action, details):
    connection = sqlite3.connect("requests.db")
    cursor = connection.cursor()
    changed_at = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    cursor.execute("""
        INSERT INTO request_history
        (request_id, action, details, changed_at)
        VALUES (?, ?, ?, ?)
    """, (
        request_id,
        action,
        details,
        changed_at
    ))
    connection.commit()
    connection.close()
def update_request(request_id, new_status, new_priority, new_remarks, new_assigned_to):
    connection = sqlite3.connect("requests.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT status, priority, remarks, assigned_to
        FROM requests
        WHERE request_id = ?
    """, (request_id,))
    old_values = cursor.fetchone()
    if old_values is None:
        connection.close()
        raise ValueError("Request was not found in the database.")
    old_status, old_priority, old_remarks, old_assigned_to = old_values
    cursor.execute("""
        UPDATE requests
        SET status = ?, priority = ?, remarks = ?, assigned_to = ?
        WHERE request_id = ?
    """, (
        new_status,
        new_priority,
        new_remarks,
        new_assigned_to,
        request_id
    ))
    changed_at = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    # Record status changes
    if old_status != new_status:
        cursor.execute("""
            INSERT INTO request_history
            (request_id, action, details, changed_at)
            VALUES (?, ?, ?, ?)
        """, (
            request_id,
            "Status Changed",
            f"{old_status} -> {new_status}",
            changed_at
        ))
    # Record priority changes
    if old_priority != new_priority:
        cursor.execute("""
            INSERT INTO request_history
            (request_id, action, details, changed_at)
            VALUES (?, ?, ?, ?)
        """, (
            request_id,
            "Priority Changed",
            f"{old_priority} -> {new_priority}",
            changed_at
        ))
    # Record remarks changes
    if (old_remarks or "") != new_remarks:
        cursor.execute("""
            INSERT INTO request_history
            (request_id, action, details, changed_at)
            VALUES (?, ?, ?, ?)
        """, (
            request_id,
            "IT Remarks Updated",
            new_remarks if new_remarks else "Remarks cleared.",
            changed_at
        ))
    # Record assignment changes.
    old_assignee = old_assigned_to or "Unassigned"
    new_assignee = new_assigned_to or "Unassigned"
    if old_assignee != new_assignee:
        cursor.execute("""
            INSERT INTO request_history
            (request_id, action, details, changed_at)
            VALUES (?, ?, ?, ?)
        """, (
            request_id,
            "Request Assigned",
            f"{old_assignee} -> {new_assignee}",
            changed_at
        ))

    connection.commit()
    connection.close()
# Create history table and seed missing creation records
setup_database()
# ==================================================
# MAIN WINDOW
# ==================================================
window = tk.Tk()
window.title("IT Dashboard")
window.geometry("1250x700")
window.minsize(950, 550)
window.resizable(True, True)
# ==================================================
# HEADER
# ==================================================
header = tk.Frame(window)
header.pack(fill="x")
tk.Label(
    header,
    text="IT Team Dashboard",
    font=("Arial", 24, "bold")
).pack(pady=(20, 0))
tk.Label(
    header,
    text="Manage employee IT requests",
    font=("Arial", 11)
).pack()
# ==================================================
# SUMMARY CARDS
# ==================================================
summary_frame = tk.Frame(window)
summary_frame.pack(fill="x", padx=20, pady=10)
total_label = tk.Label(
    summary_frame, text="Total Requests\n0",
    font=("Arial", 14, "bold"),
    relief="groove", width=18, height=3
)
total_label.pack(side="left", padx=10)
new_label = tk.Label(
    summary_frame, text="New Requests\n0",
    font=("Arial", 14, "bold"),
    relief="groove", width=18, height=3
)
new_label.pack(side="left", padx=10)
progress_label = tk.Label(
    summary_frame, text="In Progress\n0",
    font=("Arial", 14, "bold"),
    relief="groove", width=18, height=3
)
progress_label.pack(side="left", padx=10)
resolved_label = tk.Label(
    summary_frame, text="Resolved\n0",
    font=("Arial", 14, "bold"),
    relief="groove", width=18, height=3
)
resolved_label.pack(side="left", padx=10)
# ==================================================
# SEARCH AND FILTER
# ==================================================
search_frame = tk.LabelFrame(
    window,
    text="Search & Filter Requests",
    font=("Arial", 11, "bold"),
    padx=10,
    pady=10
)
search_frame.pack(fill="x", padx=20, pady=5)
tk.Label(search_frame, text="Search:").grid(
    row=0, column=0, padx=5, pady=5, sticky="w"
)
search_entry = ttk.Entry(search_frame, width=25)
search_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Label(search_frame, text="Category:").grid(
    row=0, column=2, padx=5, pady=5, sticky="w"
)
category_filter = ttk.Combobox(
    search_frame,
    values=["All", "Software", "Hardware", "Network", "Email", "Other"],
    width=13,
    state="readonly"
)
category_filter.grid(row=0, column=3, padx=5, pady=5)
category_filter.set("All")
tk.Label(search_frame, text="Priority:").grid(
    row=0, column=4, padx=5, pady=5, sticky="w"
)
priority_filter = ttk.Combobox(
    search_frame,
    values=["All", "Low", "Medium", "High", "Critical"],
    width=12,
    state="readonly"
)
priority_filter.grid(row=0, column=5, padx=5, pady=5)
priority_filter.set("All")
tk.Label(search_frame, text="Status:").grid(
    row=1, column=0, padx=5, pady=5, sticky="w"
)
status_filter = ttk.Combobox(
    search_frame,
    values=["All", "New", "In Progress", "Resolved"],
    width=15,
    state="readonly"
)
status_filter.grid(row=1, column=1, padx=5, pady=5, sticky="w")
status_filter.set("All")

tk.Label(search_frame, text="Assigned To:").grid(
    row=2, column=0, padx=5, pady=5, sticky="w"
)

assigned_filter = ttk.Combobox(
    search_frame,
    values=["All", "Unassigned", "Mohit Boora", "Kaleem"],
    width=15,
    state="readonly"
)
assigned_filter.grid(row=2, column=1, padx=5, pady=5, sticky="w")
assigned_filter.set("All")
# ==================================================
# REQUEST TABLE
# ==================================================
table_frame = tk.Frame(window)
table_frame.pack(fill="both", expand=True, padx=20, pady=10)
vertical_scroll = ttk.Scrollbar(table_frame, orient="vertical")
horizontal_scroll = ttk.Scrollbar(table_frame, orient="horizontal")
columns = (
    "Request ID", "Employee", "Category", "Item",
    "Problem", "Priority", "Status", "Created", "Assigned To"
)
request_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    yscrollcommand=vertical_scroll.set,
    xscrollcommand=horizontal_scroll.set
)
vertical_scroll.config(command=request_table.yview)
horizontal_scroll.config(command=request_table.xview)
for column in columns:
    request_table.heading(column, text=column)
request_table.column("Request ID", width=90)
request_table.column("Employee", width=130)
request_table.column("Category", width=110)
request_table.column("Item", width=140)
request_table.column("Problem", width=350)
request_table.column("Priority", width=100)
request_table.column("Status", width=120)
request_table.column("Created", width=150)
request_table.column("Assigned To", width=140)
request_table.pack(side="left", fill="both", expand=True)
vertical_scroll.pack(side="right", fill="y")
horizontal_scroll.pack(side="bottom", fill="x")
# ==================================================
# SUMMARY COUNTS
# ==================================================
def update_summary(requests):
    total = len(requests)
    new_requests = 0
    in_progress = 0
    resolved = 0
    for request in requests:
        if request[6] == "New":
            new_requests += 1
        elif request[6] == "In Progress":
            in_progress += 1
        elif request[6] == "Resolved":
            resolved += 1
    total_label.config(text=f"Total Requests\n{total}")
    new_label.config(text=f"New Requests\n{new_requests}")
    progress_label.config(text=f"In Progress\n{in_progress}")
    resolved_label.config(text=f"Resolved\n{resolved}")
# ==================================================
# LOAD AND FILTER REQUESTS
# ==================================================
def load_requests():
    for row in request_table.get_children():
        request_table.delete(row)
    requests = get_requests()
    search_text = search_entry.get().strip().lower()
    selected_category = category_filter.get()
    selected_priority = priority_filter.get()
    selected_status = status_filter.get()
    selected_assignee = assigned_filter.get()
    visible_requests = []
    for request in requests:
        request_id = str(request[0] or "").lower()
        employee_name = str(request[1] or "").lower()
        assigned_to = str(request[9] or "Unassigned").lower()
        category = str(request[2] or "")
        priority = str(request[5] or "")
        status = str(request[6] or "")
        if (
            search_text
            and search_text not in request_id
            and search_text not in employee_name
            and search_text not in assigned_to
        ):
            continue
        if selected_category != "All" and category != selected_category:
            continue
        if selected_priority != "All" and priority != selected_priority:
            continue
        if selected_status != "All" and status != selected_status:
            continue

        current_assignee = request[9] or "Unassigned"
        if selected_assignee != "All" and current_assignee != selected_assignee:
            continue

        visible_requests.append(request)
    for request in visible_requests:
        display_values = list(request[:8])
        display_values.append(request[9] or "Unassigned")
        request_table.insert("", "end", values=display_values)
    update_summary(requests)
    result_label.config(
        text=f"Showing {len(visible_requests)} of {len(requests)} requests"
    )
def reset_filters():
    search_entry.delete(0, tk.END)
    category_filter.set("All")
    priority_filter.set("All")
    status_filter.set("All")
    assigned_filter.set("All")
    load_requests()


def show_member_requests(member_name):
    search_entry.delete(0, tk.END)
    category_filter.set("All")
    priority_filter.set("All")
    status_filter.set("All")
    assigned_filter.set(member_name)
    load_requests()
tk.Button(
    search_frame,
    text="Search",
    width=12,
    command=load_requests
).grid(row=1, column=2, padx=5, pady=5)
tk.Button(
    search_frame,
    text="Reset Filters",
    width=12,
    command=reset_filters
).grid(row=1, column=3, padx=5, pady=5)
result_label = tk.Label(
    search_frame,
    text="Showing 0 of 0 requests",
    font=("Arial", 10)
)
result_label.grid(row=2, column=2, columnspan=4, padx=10, pady=5)
# ==================================================
# VIEW REQUEST HISTORY
# ==================================================
def view_history():
    selected_item = request_table.selection()
    if not selected_item:
        messagebox.showwarning(
            "Select Request",
            "Please select a request from the table first.",
            parent=window
        )
        return
    values = request_table.item(selected_item[0])["values"]
    request_id = values[0]
    history_window = tk.Toplevel(window)
    history_window.title(f"Request History - {request_id}")
    history_window.geometry("800x450")
    history_window.minsize(600, 300)
    tk.Label(
        history_window,
        text=f"Request History - {request_id}",
        font=("Arial", 18, "bold")
    ).pack(pady=15)
    history_frame = tk.Frame(history_window)
    history_frame.pack(fill="both", expand=True, padx=15, pady=10)
    history_columns = ("Date & Time", "Action", "Details")
    history_table = ttk.Treeview(
        history_frame,
        columns=history_columns,
        show="headings"
    )
    history_table.heading("Date & Time", text="Date & Time")
    history_table.heading("Action", text="Action")
    history_table.heading("Details", text="Details")
    history_table.column("Date & Time", width=160)
    history_table.column("Action", width=180)
    history_table.column("Details", width=400)
    history_scroll = ttk.Scrollbar(
        history_frame,
        orient="vertical",
        command=history_table.yview
    )
    history_table.configure(yscrollcommand=history_scroll.set)
    history_table.pack(side="left", fill="both", expand=True)
    history_scroll.pack(side="right", fill="y")
    connection = sqlite3.connect("requests.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT changed_at, action, details
        FROM request_history
        WHERE request_id = ?
        ORDER BY id ASC
    """, (request_id,))
    history_records = cursor.fetchall()
    connection.close()
    for record in history_records:
        history_table.insert("", "end", values=record)
    if not history_records:
        history_table.insert(
            "",
            "end",
            values=("-", "No History", "No history records found.")
        )
# ==================================================
# REQUEST DETAILS
# ==================================================
def open_request_details(event=None):
    selected_item = request_table.selection()
    if not selected_item:
        return
    values = request_table.item(selected_item[0])["values"]
    request_id = values[0]
    employee_name = values[1]
    category = values[2]
    related_item = values[3]
    problem = values[4]
    priority = values[5]
    status = values[6]
    created_at = values[7]
    assigned_to = values[8] if len(values) > 8 else "Unassigned"
    detail_window = tk.Toplevel(window)
    detail_window.title(f"Request Details - {request_id}")
    detail_window.geometry("650x700")
    detail_window.minsize(550, 450)
    detail_window.resizable(True, True)

    # Keep the Save Changes button outside the scrollable area.
    # This ensures it remains fully visible at the bottom.
    details_footer = tk.Frame(detail_window, relief="raised", bd=1)
    details_footer.pack(side="bottom", fill="x", padx=0, pady=0)

    content_frame = tk.Frame(detail_window)
    content_frame.pack(side="top", fill="both", expand=True)

    canvas = tk.Canvas(content_frame, highlightthickness=0)
    scrollbar = ttk.Scrollbar(
        content_frame,
        orient="vertical",
        command=canvas.yview
    )
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda event: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    canvas_window = canvas.create_window(
        (0, 0),
        window=scrollable_frame,
        anchor="nw"
    )
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind(
        "<Configure>",
        lambda event: canvas.itemconfigure(
            canvas_window,
            width=event.width
        )
    )
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    tk.Label(
        scrollable_frame,
        text=f"Request Details - {request_id}",
        font=("Arial", 20, "bold")
    ).pack(pady=20)
    info_frame = tk.Frame(scrollable_frame)
    info_frame.pack(padx=40, fill="x")
    information = [
        ("Request ID:", request_id),
        ("Employee:", employee_name),
        ("Category:", category),
        ("Related Item:", related_item),
        ("Created:", created_at)
    ]
    for index, (label, value) in enumerate(information):
        tk.Label(
            info_frame,
            text=label,
            font=("Arial", 11, "bold")
        ).grid(row=index, column=0, sticky="w", pady=7)
        tk.Label(
            info_frame,
            text=value,
            font=("Arial", 11),
            wraplength=380,
            justify="left"
        ).grid(row=index, column=1, sticky="w", padx=20)
    tk.Label(
        scrollable_frame,
        text="Problem Description",
        font=("Arial", 11, "bold")
    ).pack(anchor="w", padx=40, pady=(20, 5))
    problem_box = tk.Text(
        scrollable_frame,
        width=65,
        height=6,
        wrap="word"
    )
    problem_box.pack(padx=40, fill="x")
    problem_box.insert("1.0", problem)
    problem_box.config(state="disabled")
    tk.Label(
        scrollable_frame,
        text="Priority",
        font=("Arial", 11, "bold")
    ).pack(anchor="w", padx=40, pady=(20, 5))
    priority_box = ttk.Combobox(
        scrollable_frame,
        values=["Low", "Medium", "High", "Critical"],
        width=30,
        state="readonly"
    )
    priority_box.pack(padx=40, anchor="w")
    priority_box.set(priority)
    tk.Label(
        scrollable_frame,
        text="Status",
        font=("Arial", 11, "bold")
    ).pack(anchor="w", padx=40, pady=(20, 5))
    status_box = ttk.Combobox(
        scrollable_frame,
        values=["New", "In Progress", "Resolved"],
        width=30,
        state="readonly"
    )
    status_box.pack(padx=40, anchor="w")
    status_box.set(status)
    tk.Label(
        scrollable_frame,
        text="Assign To",
        font=("Arial", 11, "bold")
    ).pack(anchor="w", padx=40, pady=(20, 5))
    assigned_box = ttk.Combobox(
        scrollable_frame,
        values=["Unassigned", "Mohit Boora", "Kaleem"],
        width=30,
        state="readonly"
    )
    assigned_box.pack(padx=40, anchor="w")
    assigned_box.set(assigned_to or "Unassigned")
    tk.Label(
        scrollable_frame,
        text="IT Remarks",
        font=("Arial", 11, "bold")
    ).pack(anchor="w", padx=40, pady=(20, 5))
    remarks_box = tk.Text(
        scrollable_frame,
        width=65,
        height=5,
        wrap="word"
    )
    remarks_box.pack(padx=40, fill="x")
    connection = sqlite3.connect("requests.db")
    cursor = connection.cursor()
    cursor.execute(
        "SELECT remarks FROM requests WHERE request_id = ?",
        (request_id,)
    )
    result = cursor.fetchone()
    connection.close()
    if result and result[0]:
        remarks_box.insert("1.0", result[0])
    # Save updates and record history
    def save_changes():
        new_status = status_box.get()
        new_priority = priority_box.get()
        new_remarks = remarks_box.get("1.0", tk.END).strip()
        new_assigned_to = assigned_box.get()
        if not new_status or not new_priority or not new_assigned_to:
            messagebox.showwarning(
                "Missing Information",
                "Please select a status and priority.",
                parent=detail_window
            )
            return
        try:
            update_request(
                request_id,
                new_status,
                new_priority,
                new_remarks,
                new_assigned_to
            )
            messagebox.showinfo(
                "Updated",
                f"{request_id} updated successfully.",
                parent=detail_window
            )
            detail_window.destroy()
            load_requests()
        except (sqlite3.Error, ValueError) as error:
            messagebox.showerror(
                "Update Error",
                str(error),
                parent=detail_window
            )
    tk.Button(
        details_footer,
        text="Save Changes",
        width=20,
        height=2,
        command=save_changes
    ).pack(pady=8)
# ==================================================
# BUTTONS
# ==================================================
request_table.bind("<Double-1>", open_request_details)
button_frame = tk.Frame(window)
button_frame.pack(pady=10)
tk.Button(
    button_frame,
    text="View History",
    width=18,
    height=2,
    command=view_history
).pack(side="left", padx=8)
tk.Button(
    button_frame,
    text="Refresh / All Requests",
    width=20,
    height=2,
    command=reset_filters
).pack(side="left", padx=8)

tk.Button(
    button_frame,
    text="Mohit's Requests",
    width=18,
    height=2,
    command=lambda: show_member_requests("Mohit Boora")
).pack(side="left", padx=8)

tk.Button(
    button_frame,
    text="Kaleem's Requests",
    width=18,
    height=2,
    command=lambda: show_member_requests("Kaleem")
).pack(side="left", padx=8)
# ==================================================
# START APPLICATION
# ==================================================
load_requests()
window.mainloop()
