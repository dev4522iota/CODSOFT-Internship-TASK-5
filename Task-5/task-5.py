import tkinter as tk
from tkinter import messagebox
import sqlite3


class ContactApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Manager")
        self.root.geometry("800x500")
        self.root.configure(bg="#E6F2F8")
        self.root.resizable(False, False)

        # Database setup
        self.conn = sqlite3.connect("contacts.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                email TEXT,
                address TEXT
            )
        """)

        # Build UI
        self.build_ui()
        self.load_contacts()

    def build_ui(self):
        # --- Entry Frame ---
        frame = tk.Frame(self.root, bg="#A9CCE3", bd=2, relief="ridge")
        frame.place(x=10, y=10, width=350, height=480)

        tk.Label(frame, text="Name:", bg="#A9CCE3", font=("Arial", 12)).place(x=10, y=20)
        tk.Label(frame, text="Phone:", bg="#A9CCE3", font=("Arial", 12)).place(x=10, y=70)
        tk.Label(frame, text="Email:", bg="#A9CCE3", font=("Arial", 12)).place(x=10, y=120)
        tk.Label(frame, text="Address:", bg="#A9CCE3", font=("Arial", 12)).place(x=10, y=170)

        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.address_var = tk.StringVar()

        tk.Entry(frame, textvariable=self.name_var, font=("Arial", 12)).place(x=100, y=20, width=200)
        tk.Entry(frame, textvariable=self.phone_var, font=("Arial", 12)).place(x=100, y=70, width=200)
        tk.Entry(frame, textvariable=self.email_var, font=("Arial", 12)).place(x=100, y=120, width=200)
        tk.Entry(frame, textvariable=self.address_var, font=("Arial", 12)).place(x=100, y=170, width=200)

        tk.Button(frame, text="Add Contact", bg="#1ABC9C", fg="white",
                  font=("Arial", 12, "bold"), command=self.add_contact).place(x=20, y=230, width=130)
        tk.Button(frame, text="Update Contact", bg="#F39C12", fg="white",
                  font=("Arial", 12, "bold"), command=self.update_contact).place(x=170, y=230, width=150)
        tk.Button(frame, text="Delete Contact", bg="#E74C3C", fg="white",
                  font=("Arial", 12, "bold"), command=self.delete_contact).place(x=20, y=280, width=130)
        tk.Button(frame, text="Clear", bg="#5D6D7E", fg="white",
                  font=("Arial", 12, "bold"), command=self.clear_fields).place(x=170, y=280, width=150)

        # --- Search Frame ---
        search_frame = tk.Frame(self.root, bg="#D6EAF8", bd=2, relief="ridge")
        search_frame.place(x=370, y=10, width=420, height=60)

        tk.Label(search_frame, text="Search:", font=("Arial", 12), bg="#D6EAF8").place(x=10, y=15)
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 12)).place(x=80, y=15, width=200)
        tk.Button(search_frame, text="Go", bg="#2980B9", fg="white",
                  font=("Arial", 12, "bold"), command=self.search_contact).place(x=300, y=12, width=80)

        # --- Listbox Frame ---
        list_frame = tk.Frame(self.root, bg="#D5DBDB", bd=2, relief="ridge")
        list_frame.place(x=370, y=80, width=420, height=410)

        self.contact_listbox = tk.Listbox(list_frame, font=("Arial", 12), selectmode="SINGLE")
        self.contact_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self.contact_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.contact_listbox.yview)

        self.contact_listbox.bind("<<ListboxSelect>>", self.on_select)

    # --- DB Functions ---
    def add_contact(self):
        name, phone, email, address = self.get_fields()
        if not name or not phone:
            messagebox.showwarning("Error", "Name and Phone are required!")
            return

        with self.conn:
            self.conn.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)",
                              (name, phone, email, address))
        self.load_contacts()
        self.clear_fields()

    def update_contact(self):
        selected = self.get_selected_contact_id()
        if not selected:
            return

        name, phone, email, address = self.get_fields()
        with self.conn:
            self.conn.execute("""UPDATE contacts SET name=?, phone=?, email=?, address=? WHERE id=?""",
                              (name, phone, email, address, selected))
        self.load_contacts()
        self.clear_fields()

    def delete_contact(self):
        selected = self.get_selected_contact_id()
        if not selected:
            return

        confirm = messagebox.askyesno("Delete", "Are you sure you want to delete this contact?")
        if confirm:
            with self.conn:
                self.conn.execute("DELETE FROM contacts WHERE id=?", (selected,))
            self.load_contacts()
            self.clear_fields()

    def search_contact(self):
        query = self.search_var.get().strip()
        self.contact_listbox.delete(0, "end")
        if query:
            for row in self.cursor.execute("SELECT id, name, phone FROM contacts WHERE name LIKE ? OR phone LIKE ?",
                                           (f"%{query}%", f"%{query}%")):
                self.contact_listbox.insert("end", f"{row[0]} - {row[1]} ({row[2]})")
        else:
            self.load_contacts()

    def load_contacts(self):
        self.contact_listbox.delete(0, "end")
        for row in self.cursor.execute("SELECT id, name, phone FROM contacts ORDER BY name"):
            self.contact_listbox.insert("end", f"{row[0]} - {row[1]} ({row[2]})")

    # --- Helper Functions ---
    def on_select(self, event):
        try:
            selected = self.contact_listbox.get(self.contact_listbox.curselection())
            contact_id = int(selected.split(" - ")[0])
            self.cursor.execute("SELECT * FROM contacts WHERE id=?", (contact_id,))
            row = self.cursor.fetchone()
            if row:
                self.name_var.set(row[1])
                self.phone_var.set(row[2])
                self.email_var.set(row[3])
                self.address_var.set(row[4])
        except:
            pass

    def get_selected_contact_id(self):
        try:
            selected = self.contact_listbox.get(self.contact_listbox.curselection())
            return int(selected.split(" - ")[0])
        except:
            messagebox.showwarning("Error", "No contact selected!")
            return None

    def get_fields(self):
        return (self.name_var.get().strip(),
                self.phone_var.get().strip(),
                self.email_var.get().strip(),
                self.address_var.get().strip())

    def clear_fields(self):
        self.name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.address_var.set("")


# --- Run App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ContactApp(root)
    root.mainloop()
