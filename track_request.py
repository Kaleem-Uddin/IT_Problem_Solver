
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3


def get_request(request_id):
    connection = sqlite3.connect("requests.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT request_id, employee_name, category,
               related_item, problem, priority,
               status, created_at, remarks
        FROM requests
        WHERE UPPER(request_id) = ?
    """, (request_id.upper(),))

    request = cursor.fetchone()
    connection.close()

    return request


def track_request():
    global current_request_id

    request_id = request_id_entry.get().strip().upper()

    if not request_id:
        messagebox.showwarning(
            "Missing Request ID",
            "Please enter your Request ID.",
            parent=window
        )
        return

    try:
        request = get_request(request_id)

        if request is None:
            current_request_id = None
            result_label.config(
                text="No request found. Please check your Request ID.",
                fg="red"
            )
            history_button.config(state="disabled")
            return

        current_request_id = request[0]

        result_text = (
            f"Request ID: {request[0]}\n"
            f"Employee Name: {request[1]}\n"
            f"Category: {request[2]}\n"
            f"Related Item: {request[3]}\n"
            f"Priority: {request[5]}\n"
            f"Status: {request[6]}\n"
            f"Created At: {request[7]}\n\n"
            f"Problem Description:\n{request[4]}\n\n"
            f"IT Remarks:\n{request[8] or 'No remarks added yet.'}"
        )

        result_label.config(
            text=result_text,
            fg="#1f2937",
            justify="left",
            anchor="nw"
        )

        history_button.config(state="normal")

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            str(error),
            parent=window
        )


def view_request_history():
    if not current_request_id:
        messagebox.showwarning(
            "Track Request First",
            "Please track a valid Request ID first.",
            parent=window
        )
        return

    history_window = tk.Toplevel(window)
    history_window.title(f"Request History - {current_request_id}")
    history_window.geometry("750x400")
    history_window.minsize(550, 300)
    history_window.configure(bg="#f3f4f6")

    tk.Label(
        history_window,
        text=f"Request History - {current_request_id}",
        font=("Arial", 17, "bold"),
        bg="#f3f4f6",
        fg="#1e3a8a"
    ).pack(pady=15)

    table_frame = tk.Frame(history_window)
    table_frame.pack(fill="both", expand=True, padx=15, pady=10)

    columns = ("Date & Time", "Action", "Details")

    history_table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    history_table.heading("Date & Time", text="Date & Time")
    history_table.heading("Action", text="Action")
    history_table.heading("Details", text="Details")

    history_table.column("Date & Time", width=160, anchor="center")
    history_table.column("Action", width=170, anchor="w")
    history_table.column("Details", width=350, anchor="w")

    vertical_scroll = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=history_table.yview
    )

    horizontal_scroll = ttk.Scrollbar(
        history_window,
        orient="horizontal",
        command=history_table.xview
    )

    history_table.configure(
        yscrollcommand=vertical_scroll.set,
        xscrollcommand=horizontal_scroll.set
    )

    history_table.pack(side="left", fill="both", expand=True)
    vertical_scroll.pack(side="right", fill="y")
    horizontal_scroll.pack(fill="x", padx=15, pady=(0, 10))

    try:
        connection = sqlite3.connect("requests.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT changed_at, action, details
            FROM request_history
            WHERE request_id = ?
            ORDER BY id ASC
        """, (current_request_id,))

        records = cursor.fetchall()
        connection.close()

        for record in records:
            history_table.insert("", "end", values=record)

        if not records:
            history_table.insert(
                "",
                "end",
                values=("-", "No History", "No history records found.")
            )

    except sqlite3.Error as error:
        history_window.destroy()
        messagebox.showerror(
            "Database Error",
            str(error),
            parent=window
        )


# Main Window
current_request_id = None

window = tk.Tk()
window.title("IT Support - Track Request")
window.geometry("700x720")
window.minsize(550, 550)
window.configure(bg="#f3f4f6")

tk.Label(
    window,
    text="Track Your IT Request",
    font=("Arial", 22, "bold"),
    bg="#f3f4f6",
    fg="#1e3a8a"
).pack(pady=(25, 10))

tk.Label(
    window,
    text="Enter your Request ID to check the latest status.",
    font=("Arial", 11),
    bg="#f3f4f6",
    fg="#4b5563"
).pack(pady=5)

search_frame = tk.Frame(window, bg="#f3f4f6")
search_frame.pack(pady=20)

request_id_entry = tk.Entry(
    search_frame,
    font=("Arial", 13),
    width=25
)
request_id_entry.pack(side="left", padx=5)
request_id_entry.bind("<Return>", lambda event: track_request())

tk.Button(
    search_frame,
    text="Track Request",
    font=("Arial", 11, "bold"),
    bg="#2563eb",
    fg="white",
    activebackground="#1d4ed8",
    activeforeground="white",
    command=track_request,
    padx=10,
    pady=5
).pack(side="left", padx=5)

result_frame = tk.Frame(
    window,
    bg="white",
    bd=1,
    relief="solid"
)
result_frame.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=(5, 15)
)

result_label = tk.Label(
    result_frame,
    text="Your request details will appear here.",
    font=("Arial", 11),
    bg="white",
    fg="#6b7280",
    justify="left",
    anchor="nw",
    padx=20,
    pady=20,
    wraplength=600
)
result_label.pack(fill="both", expand=True)

history_button = tk.Button(
    window,
    text="View Request History",
    font=("Arial", 11, "bold"),
    bg="#0f766e",
    fg="white",
    activebackground="#115e59",
    activeforeground="white",
    command=view_request_history,
    state="disabled",
    padx=15,
    pady=8
)
history_button.pack(pady=(0, 20))

window.mainloop()
