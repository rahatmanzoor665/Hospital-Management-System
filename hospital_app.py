import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'hospital_db'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        messagebox.showerror("DB Connection Error", str(e))
        return None

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def ensure_admin_exists():
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    if count == 0:
        pwd = hash_password("admin123")
        cur.execute("INSERT INTO users (username,password_hash,role,full_name) VALUES (%s,%s,%s,%s)",
                    ("admin", pwd, "admin", "System Admin"))
        conn.commit()
    cur.close()
    conn.close()

# ---------- APP ----------
class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Management System")
        self.geometry("650x650")
        self.resizable(True, True)

        # user info after login
        self.current_user = None

        # container frames
        self.frames = {}
        self.create_login_frame()

    # ---------- LOGIN ----------
    def create_login_frame(self):
        frm = ttk.Frame(self)
        frm.pack(fill='both', expand=True)
        self.frames['login'] = frm
        lbl_title = ttk.Label(frm, text="Hospital Management System - Login", font=("TkDefaultFont", 18))
        lbl_title.pack(pady=20)

        inner = ttk.Frame(frm)
        inner.pack(pady=10)

        ttk.Label(inner, text="Username:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.login_username = ttk.Entry(inner)
        self.login_username.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(inner, text="Password:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.login_password = ttk.Entry(inner, show='*')
        self.login_password.grid(row=1, column=1, padx=5, pady=5)
        login_btn = ttk.Button(inner, text="Login", command=self.do_login)
        login_btn.grid(row=2, column=0, columnspan=2, pady=10)

    def do_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        if not username or not password:
            messagebox.showwarning("Login", "Please enter username and password")
            return

        conn = get_db_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, password_hash, role, full_name FROM users WHERE username=%s", (username,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            messagebox.showerror("Login Failed", "User not found")
            return
        user_id, uname, pw_hash, role, full_name = row
        if hash_password(password) == pw_hash:
            self.current_user = {'user_id': user_id, 'username': uname, 'role': role, 'full_name': full_name}
            # destroy login and load main UI
            self.frames['login'].destroy()
            self.create_main_ui()
        else:
            messagebox.showerror("Login Failed", "Incorrect password")

    # ---------- MAIN UI ----------
    def create_main_ui(self):
        # top menu
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="MENU", menu=file_menu)

        # welcome
        top = ttk.Frame(self)
        top.pack(fill='x')
        ttk.Label(top, text=f"Welcome, {self.current_user['full_name']} ({self.current_user['role']})", font=("TkDefaultFont", 12)).pack(side='left', padx=10, pady=8)

        # notebook tabs for modules
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # create module frames
        self.patients_frame = PatientsFrame(notebook)
        self.doctors_frame = DoctorsFrame(notebook)
        self.appointments_frame = AppointmentsFrame(notebook)
        self.rooms_frame = RoomsFrame(notebook)
        self.billing_frame = BillingFrame(notebook)
        self.staff_frame = StaffFrame(notebook)
        self.users_frame = UsersFrame(notebook)

        notebook.add(self.patients_frame, text="Patients")
        notebook.add(self.doctors_frame, text="Doctors")
        notebook.add(self.appointments_frame, text="Appointments")
        notebook.add(self.rooms_frame, text="Rooms")
        notebook.add(self.billing_frame, text="Billing")
        notebook.add(self.staff_frame, text="Staff")
        # only admin sees user management
        if self.current_user['role'] == 'admin':
            notebook.add(self.users_frame, text="Users")
    def logout(self):
        answer = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if answer:
            self.destroy()
            # start a new app instance to show login again
            app = HospitalApp()
            app.mainloop()
# ---------- MODULE FRAMES ----------
class PatientsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # left form
        left = ttk.Frame(self)
        left.pack(side='left', fill='y', padx=10, pady=10)
        fields = [
            ('Full Name','full_name'),
            ('Gender','gender'),
            ('DOB (YYYY-MM-DD)','dob'),
            ('Age','age'),
            ('Phone','phone'),
            ('Address','address'),
            ('Disease','disease'),
            ('Admit Date (YYYY-MM-DD)','admit_date'),
            ('Discharge Date (YYYY-MM-DD)','discharge_date'),
            ('Doctor ID','doctor_id'),
            ('Room ID','room_id')
        ]
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(left, text=label).grid(row=i, column=0, sticky='w', pady=3)

            if key == 'Gender':
                options = ttk.Combobox(left, values=["Male", "Female", "Others"], width=28, state='readonly')
                options.set("Select Gender")
                options.grid(row=i, column=1, pady=3, padx=5)
                self.entries[key] = options
            else:
                ent = ttk.Entry(left, width=30)
                ent.grid(row=i, column=1, pady=3, padx=5)
                self.entries[key] = ent

        btn_frame = ttk.Frame(left)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=8)
        ttk.Button(btn_frame, text="Add", command=self.add_patient).pack(side='left', padx=4)
        ttk.Button(btn_frame, text="Update", command=self.update_patient).pack(side='left', padx=4)
        ttk.Button(btn_frame, text="Delete", command=self.delete_patient).pack(side='left', padx=4)
        ttk.Button(btn_frame, text="Clear", command=self.clear_form).pack(side='left', padx=4)

        # right: list
        right = ttk.Frame(self)
        right.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        searchbar = ttk.Frame(right)
        searchbar.pack(fill='x', pady=5)
        self.search_var = tk.StringVar()
        ttk.Entry(searchbar, textvariable=self.search_var).pack(side='left', fill='x', expand=True, padx=5)
        ttk.Button(searchbar, text="Search", command=self.search_patients).pack(side='left', padx=5)
        ttk.Button(searchbar, text="Refresh", command=self.load_patients).pack(side='left', padx=5)

        cols = ('patient_id','full_name','gender','age','phone','disease','admit_date','discharge_date','doctor_id','room_id')
        self.tree = ttk.Treeview(right, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=110, anchor='center')
            self.tree.pack(fill='both', expand=True)
        scrollbar_x = ttk.Scrollbar(right, orient='horizontal', command=self.tree.xview)
        self.tree.configure(xscrollcommand=scrollbar_x.set)
        scrollbar_x.pack(side='bottom', fill='x')

        scrollbar_y = ttk.Scrollbar(right, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side='right', fill='y')

    def run_query(self, query, params=None, fetch=False):
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        cur.execute(query,params or ())
        if fetch:
            res = cur.fetchall()
            cur.close()
            conn.close()
            return res
        else:
            conn.commit()
            cur.close()
            conn.close()
            return True

    def add_patient(self):
        try:
            data = {k:v.get().strip() for k,v in self.entries.items()}
            # convert empty to None
            for k in data:
                if data[k] == '':
                    data[k] = None
            q = """INSERT INTO patients (full_name, gender, dob, age, phone, address, disease, admit_date, discharge_date, doctor_id, room_id)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            params =(
                data['full_name'],
                data['gender'],
                data['dob'],
                data['age'],
                data['phone'],
                data['address'],
                data['disease'],
                data['admit_date'],
                data['discharge_date'],
                data['doctor_id'],
                data['room_id'])
            ok = self.run_query(q, params)
            if ok:
                messagebox.showinfo("Success", "Patient added")
                self.load_patients()
                self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected Error: {e}")


    def load_patients(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = self.run_query("SELECT patient_id, full_name, gender, age, phone, disease, admit_date, discharge_date, doctor_id, room_id FROM patients ORDER BY patient_id", fetch=True)
        if rows:
            for row in rows:
                self.tree.insert('', 'end', values=row)

    def search_patients(self):
        term = self.search_var.get().strip()
        if not term:
            self.load_patients()
            return
        q = "SELECT patient_id, full_name, gender, age, phone, disease, admit_date, discharge_date, doctor_id, room_id FROM patients WHERE full_name LIKE %s OR phone LIKE %s"
        rows = self.run_query(q, ('%'+term+'%', '%'+term+'%'), fetch=True)
        for r in self.tree.get_children():
            self.tree.delete(r)
        if rows:
            for row in rows:
                self.tree.insert('', 'end', values=row)

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])['values']
        # map to entries
        keys = ['patient_id','full_name','gender','age','phone','disease','admit_date','discharge_date','doctor_id','room_id']
        mapping = dict(zip(keys, vals))
        # set entries (some keys like patient_id not editable here)
        self.entries['full_name'].delete(0, tk.END); self.entries['full_name'].insert(0, mapping['full_name'])
        self.entries['gender'].delete(0, tk.END); self.entries['gender'].insert(0, mapping['gender'] or '')
        # dob not returned in tree -> keep blank
        self.entries['age'].delete(0, tk.END); self.entries['age'].insert(0, mapping['age'] or '')
        self.entries['phone'].delete(0, tk.END); self.entries['phone'].insert(0, mapping['phone'] or '')
        self.entries['address'].delete(0, tk.END)  # address may not be shown
        self.entries['disease'].delete(0, tk.END); self.entries['disease'].insert(0, mapping['disease'] or '')
        self.entries['admit_date'].delete(0, tk.END); self.entries['admit_date'].insert(0, mapping['admit_date'] or '')
        self.entries['discharge_date'].delete(0, tk.END); self.entries['discharge_date'].insert(0, mapping['discharge_date'] or '')
        self.entries['doctor_id'].delete(0, tk.END); self.entries['doctor_id'].insert(0, mapping['doctor_id'] or '')
        self.entries['room_id'].delete(0, tk.END); self.entries['room_id'].insert(0, mapping['room_id'] or '')

    def update_patient(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a patient from the list to update")
            return
        pid = self.tree.item(sel[0])['values'][0]
        data = {k: v.get().strip() for k,v in self.entries.items()}
        for k in data:
            if data[k] == '':
                data[k] = None
                q = """UPDATE patients SET full_name=%s, gender=%s, dob=%s, age=%s, phone=%s, address=%s, disease=%s, admit_date=%s, discharge_date=%s, doctor_id=%s, room_id=%s WHERE patient_id=%s"""
                params = (data['full_name'], data['gender'], data['dob'], data['age'], data['phone'], data['address'],
                data['disease'], data['admit_date'], data['discharge_date'], data['doctor_id'], data['room_id'], pid)
                ok = self.run_query(q, params)
        if ok:
            messagebox.showinfo("Updated", "Patient record updated")
            self.load_patients()

    def delete_patient(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a patient to delete")
            return
        pid = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete patient ID {pid}?"):
            self.run_query("DELETE FROM patients WHERE patient_id=%s", (pid,))
            messagebox.showinfo("Deleted", "Patient deleted")
            self.load_patients()
            self.clear_form()

    def clear_form(self):
        for e in self.entries.values():
            e.delete(0, tk.END)

class DoctorsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        left = ttk.Frame(self)
        left.pack(side='left', fill='y', padx=10, pady=10)
        labels = ['Full Name','Specialization','Phone','Email','Room No']
        self.ent = {}
        for i,l in enumerate(labels):
            ttk.Label(left, text=l).grid(row=i, column=0, sticky='w', pady=3)
            e = ttk.Entry(left)
            e.grid(row=i, column=1, pady=3, padx=5)
            self.ent[l] = e
        btns = ttk.Frame(left); btns.grid(row=len(labels), column=0, columnspan=2, pady=8)
        ttk.Button(btns, text="Add", command=self.add_doctor).pack(side='left', padx=4)
        ttk.Button(btns, text="Update", command=self.update_doctor).pack(side='left', padx=4)
        ttk.Button(btns, text="Delete", command=self.delete_doctor).pack(side='left', padx=4)
        ttk.Button(btns, text="Clear", command=self.clear_form).pack(side='left', padx=4)

        right = ttk.Frame(self); right.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(right, columns=('id','name','spec','phone','email','room'), show='headings')
        for c, h in zip(('id','name','spec','phone','email','room'), ('ID','Name','Specialization','Phone','Email','Room')):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=120)
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.load_doctors()

    def run(self, q, p=None, fetch=False):
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        cur.execute(q, p or ())
        if fetch:
            rows = cur.fetchall()
            cur.close(); conn.close(); return rows
        conn.commit(); cur.close(); conn.close(); return True

    def add_doctor(self):
        name = self.ent['Full Name'].get().strip()
        if not name:
            messagebox.showwarning("Input", "Name required")
            return
        self.run("INSERT INTO doctors (full_name,specialization,phone,email,room_no) VALUES (%s,%s,%s,%s,%s)",
                 (name, self.ent['Specialization'].get(), self.ent['Phone'].get(), self.ent['Email'].get(), self.ent['Room No'].get()))
        messagebox.showinfo("Added", "Doctor added")
        self.load_doctors()
        self.clear_form()

    def load_doctors(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows = self.run("SELECT doctor_id, full_name, specialization, phone, email, room_no FROM doctors ORDER BY doctor_id DESC", fetch=True)
        if rows:
            for r in rows: self.tree.insert('', 'end', values=r)

    def on_select(self, evt):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])['values']
        self.ent['Full Name'].delete(0,tk.END); self.ent['Full Name'].insert(0, vals[1])
        self.ent['Specialization'].delete(0,tk.END); self.ent['Specialization'].insert(0, vals[2] or '')
        self.ent['Phone'].delete(0,tk.END); self.ent['Phone'].insert(0, vals[3] or '')
        self.ent['Email'].delete(0,tk.END); self.ent['Email'].insert(0, vals[4] or '')
        self.ent['Room No'].delete(0,tk.END); self.ent['Room No'].insert(0, vals[5] or '')

    def update_doctor(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Choose a doctor to update")
            return
        doc_id = self.tree.item(sel[0])['values'][0]
        self.run("UPDATE doctors SET full_name=%s, specialization=%s, phone=%s, email=%s, room_no=%s WHERE doctor_id=%s",
                 (self.ent['Full Name'].get(), self.ent['Specialization'].get(), self.ent['Phone'].get(),
                  self.ent['Email'].get(), self.ent['Room No'].get(), doc_id))
        messagebox.showinfo("Updated", "Doctor updated")
        self.load_doctors()

    def delete_doctor(self):
        sel = self.tree.selection()
        if not sel: return
        doc_id = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Delete doctor ID {doc_id}?"):
            self.run("DELETE FROM doctors WHERE doctor_id=%s", (doc_id,))
            messagebox.showinfo("Deleted", "Doctor deleted")
            self.load_doctors()
            self.clear_form()

    def clear_form(self):
        for e in self.ent.values():
            e.delete(0,tk.END)

class AppointmentsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        left = ttk.Frame(self); left.pack(side='left', fill='y', padx=10, pady=10)
        field =[
            ('Patient ID','P_ID'),
            ('Doctor ID','D_id'),
            ('Date (YYYY-MM-DD)','Date'),
            ('Time (HH:MM)','Time'),
            ('Status','Status'),
            ('Notes','Notes')
        ]
        self.e = {}
        for i,(l,key) in enumerate(field):
            ttk.Label(left, text=l).grid(row=i, column=0, sticky='w', pady=3,padx=3)
            if(key=='Status'):
                options=ttk.Combobox(left,values=["scheduled",'completed','cancelled'])
                options.grid(row=i,column=1,pady=3,padx=3)
                self.e[key]=options
            else:
                en = ttk.Entry(left)
                en.grid(row=i, column=1, pady=3)
                self.e[l] = en
        btns = ttk.Frame(left); btns.grid(row=len(field), column=0, columnspan=2, pady=8)
        ttk.Button(btns, text="Schedule", command=self.add_appt).pack(side='left', padx=4)
        ttk.Button(btns, text="Update", command=self.update_appt).pack(side='left', padx=4)
        ttk.Button(btns, text="Cancel", command=self.cancel_appt).pack(side='left', padx=4)
        ttk.Button(btns, text="Clear", command=self.clear_form).pack(side='left', padx=4)

        right = ttk.Frame(self); right.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(right, columns=('id','patient','doctor','date','time','status'), show='headings')
        for c,h in zip(('id','patient','doctor','date','time','status'), ('ID','Patient','Doctor','Date','Time','Status')):
            self.tree.heading(c, text=h); self.tree.column(c, width=120)
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.load_appts()

    def run(self, q, p=None, fetch=False):
        conn = get_db_connection()
        if not conn: return None
        cur = conn.cursor()
        cur.execute(q, p or ())
        if fetch:
            rows = cur.fetchall(); cur.close(); conn.close(); return rows
        conn.commit(); cur.close(); conn.close(); return True

    def add_appt(self):
        pid = self.e['Patient ID'].get().strip()
        did = self.e['Doctor ID'].get().strip()
        if not pid or not did:
            messagebox.showwarning("Input", "Patient ID and Doctor ID required")
            return
        self.run("INSERT INTO appointments (patient_id, doctor_id, appt_date, appt_time, status, notes) VALUES (%s,%s,%s,%s,%s,%s)",
                 (pid, did, self.e['Date (YYYY-MM-DD)'].get(), self.e['Time (HH:MM)'].get(), self.e['Status'].get() or 'scheduled', self.e['Notes'].get()))
        messagebox.showinfo("Scheduled", "Appointment scheduled")
        self.load_appts(); self.clear_form()

    def load_appts(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows = self.run("SELECT appointment_id, patient_id, doctor_id, appt_date, appt_time, status FROM appointments ORDER BY appt_date DESC", fetch=True)
        if rows:
            for r in rows: self.tree.insert('', 'end', values=r)

    def on_select(self, evt):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])['values']
        self.e['Patient ID'].delete(0,tk.END); self.e['Patient ID'].insert(0, vals[1])
        self.e['Doctor ID'].delete(0,tk.END); self.e['Doctor ID'].insert(0, vals[2])
        self.e['Date (YYYY-MM-DD)'].delete(0,tk.END); self.e['Date (YYYY-MM-DD)'].insert(0, vals[3] or '')
        self.e['Time (HH:MM)'].delete(0,tk.END); self.e['Time (HH:MM)'].insert(0, vals[4] or '')
        self.e['Status'].delete(0,tk.END); self.e['Status'].insert(0, vals[5] or '')

    def update_appt(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Select", "Select appointment"); return
        aid = self.tree.item(sel[0])['values'][0]
        self.run("UPDATE appointments SET patient_id=%s, doctor_id=%s, appt_date=%s, appt_time=%s, status=%s, notes=%s WHERE appointment_id=%s",
                 (self.e['Patient ID'].get(), self.e['Doctor ID'].get(), self.e['Date (YYYY-MM-DD)'].get(), self.e['Time (HH:MM)'].get(), self.e['Status'].get(), self.e['Notes'].get(), aid))
        messagebox.showinfo("Updated", "Appointment updated"); self.load_appts()

    def cancel_appt(self):
        sel = self.tree.selection()
        if not sel: return
        aid = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", "Cancel appointment?"):
            self.run("UPDATE appointments SET status='cancelled' WHERE appointment_id=%s", (aid,))
            self.load_appts()

    def clear_form(self):
        for e in self.e.values(): e.delete(0, tk.END)

class RoomsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        left = ttk.Frame(self); left.pack(side='left', fill='y', padx=10, pady=10)
        labels = ['Room No','Type','Status','Price Per Day','Current Patient ID']
        self.e = {}
        for i,l in enumerate(labels):
            ttk.Label(left, text=l).grid(row=i, column=0, sticky='w', pady=3)
            en = ttk.Entry(left)
            en.grid(row=i, column=1, pady=3)
            self.e[l] = en
        btns = ttk.Frame(left); btns.grid(row=len(labels), column=0, columnspan=2, pady=8)
        ttk.Button(btns, text="Add", command=self.add_room).pack(side='left', padx=4)
        ttk.Button(btns, text="Update", command=self.update_room).pack(side='left', padx=4)
        ttk.Button(btns, text="Delete", command=self.delete_room).pack(side='left', padx=4)
        ttk.Button(btns, text="Clear", command=self.clear_form).pack(side='left', padx=4)

        right = ttk.Frame(self); right.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(right, columns=('id','room_no','type','status','price','patient'), show='headings')
        for c,h in zip(('id','room_no','type','status','price','patient'), ('ID','Room No','Type','Status','Price','Patient')):
            self.tree.heading(c, text=h); self.tree.column(c, width=120)
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.load_rooms()

    def run(self, q, p=None, fetch=False):
        conn = get_db_connection()
        if not conn: return None
        cur = conn.cursor()
        cur.execute(q, p or ())
        if fetch:
            rows = cur.fetchall(); cur.close(); conn.close(); return rows
        conn.commit(); cur.close(); conn.close(); return True

    def add_room(self):
        self.run("INSERT INTO rooms (room_no,type,status,price_per_day,current_patient_id) VALUES (%s,%s,%s,%s,%s)",
                 (self.e['Room No'].get(), self.e['Type'].get() or 'General', self.e['Status'].get() or 'free', self.e['Price Per Day'].get() or 0.0, self.e['Current Patient ID'].get() or None))
        messagebox.showinfo("Added", "Room added"); self.load_rooms(); self.clear_form()

    def load_rooms(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows = self.run("SELECT room_id, room_no, type, status, price_per_day, current_patient_id FROM rooms ORDER BY room_id DESC", fetch=True)
        if rows:
            for r in rows: self.tree.insert('', 'end', values=r)

    def on_select(self, evt):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])['values']
        self.e['Room No'].delete(0,tk.END); self.e['Room No'].insert(0, vals[1])
        self.e['Type'].delete(0,tk.END); self.e['Type'].insert(0, vals[2] or '')
        self.e['Status'].delete(0,tk.END); self.e['Status'].insert(0, vals[3] or '')
        self.e['Price Per Day'].delete(0,tk.END); self.e['Price Per Day'].insert(0, vals[4] or '')
        self.e['Current Patient ID'].delete(0,tk.END); self.e['Current Patient ID'].insert(0, vals[5] or '')

    def update_room(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Select","Select a room"); return
        rid = self.tree.item(sel[0])['values'][0]
        self.run("UPDATE rooms SET room_no=%s, type=%s, status=%s, price_per_day=%s, current_patient_id=%s WHERE room_id=%s",
                 (self.e['Room No'].get(), self.e['Type'].get(), self.e['Status'].get(), self.e['Price Per Day'].get() or 0.0, self.e['Current Patient ID'].get() or None, rid))
        messagebox.showinfo("Updated","Room updated"); self.load_rooms()

    def delete_room(self):
        sel = self.tree.selection()
        if not sel: return
        rid = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm","Delete room?"):
            self.run("DELETE FROM rooms WHERE room_id=%s", (rid,))
            messagebox.showinfo("Deleted","Room deleted"); self.load_rooms(); self.clear_form()

    def clear_form(self):
        for e in self.e.values(): e.delete(0, tk.END)

class BillingFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        left = ttk.Frame(self); left.pack(side='left', fill='y', padx=10, pady=10)
        labels = ['Patient ID','Doctor Charge','Room Charge','Medicine Charge','Other Charge','Payment Status','Paid Amount']
        self.e = {}
        for i,l in enumerate(labels):
            ttk.Label(left, text=l).grid(row=i, column=0, sticky='w', pady=3)
            en = ttk.Entry(left)
            en.grid(row=i, column=1, pady=3)
            self.e[l] = en
        ttk.Button(left, text="Generate Bill", command=self.generate_bill).grid(row=len(labels), column=0, columnspan=2, pady=8)

        right = ttk.Frame(self); right.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(right, columns=('id','patient','date','total','status','paid'), show='headings')
        for c,h in zip(('id','patient','date','total','status','paid'), ('Bill ID','Patient','Date','Total','Status','Paid')):
            self.tree.heading(c, text=h); self.tree.column(c, width=130)
        self.tree.pack(fill='both', expand=True)
        self.load_bills()

    def run(self, q, p=None, fetch=False):
        conn = get_db_connection()
        if not conn: return None
        cur = conn.cursor()
        cur.execute(q, p or ())
        if fetch:
            rows = cur.fetchall(); cur.close(); conn.close(); return rows
        conn.commit(); cur.close(); conn.close(); return True

    def generate_bill(self):
        pid = self.e['Patient ID'].get().strip()
        if not pid:
            messagebox.showwarning("Input","Patient ID required"); return
        dc = float(self.e['Doctor Charge'].get() or 0)
        rc = float(self.e['Room Charge'].get() or 0)
        mc = float(self.e['Medicine Charge'].get() or 0)
        oc = float(self.e['Other Charge'].get() or 0)
        ps = self.e['Payment Status'].get() or 'unpaid'
        paid = float(self.e['Paid Amount'].get() or 0)
        # total computed in DB (if supported), else compute here
        total = dc + rc + mc + oc
        self.run("INSERT INTO bills (patient_id, bill_date, doctor_charge, room_charge, medicine_charge, other_charge, paid_amount, payment_status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                 (pid, datetime.today().date(), dc, rc, mc, oc, paid, ps))
        messagebox.showinfo("Bill", f"Bill generated, total {total}")
        self.load_bills()

    def load_bills(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows = self.run("SELECT bill_id, patient_id, bill_date, total_amount, payment_status, paid_amount FROM bills ORDER BY bill_date DESC", fetch=True)
        if rows:
            for r in rows: self.tree.insert('', 'end', values=r)

class StaffFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        left = ttk.Frame(self); left.pack(side='left', fill='y', padx=10, pady=10)
        labels = ['Full Name','Role','Phone','Shift']
        self.e = {}
        for i,l in enumerate(labels):
            ttk.Label(left, text=l).grid(row=i, column=0, sticky='w', pady=3)
            en = ttk.Entry(left)
            en.grid(row=i, column=1, pady=3)
            self.e[l] = en
        btns = ttk.Frame(left); btns.grid(row=len(labels), column=0, columnspan=2, pady=8)
        ttk.Button(btns, text="Add", command=self.add_staff).pack(side='left', padx=4)
        ttk.Button(btns, text="Update", command=self.update_staff).pack(side='left', padx=4)
        ttk.Button(btns, text="Delete", command=self.delete_staff).pack(side='left', padx=4)
        ttk.Button(btns, text="Clear", command=self.clear_form).pack(side='left', padx=4)

        right = ttk.Frame(self); right.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(right, columns=('id','name','role','phone','shift'), show='headings')
        for c,h in zip(('id','name','role','phone','shift'), ('ID','Name','Role','Phone','Shift')):
            self.tree.heading(c, text=h); self.tree.column(c, width=120)
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.load_staff()

    def run(self,q,p=None,fetch=False):
        conn = get_db_connection()
        if not conn: return None
        cur = conn.cursor()
        cur.execute(q,p or ())
        if fetch:
            rows = cur.fetchall(); cur.close(); conn.close(); return rows
        conn.commit(); cur.close(); conn.close(); return True

    def add_staff(self):
        self.run("INSERT INTO staff (full_name, role, phone, shift) VALUES (%s,%s,%s,%s)",
                 (self.e['Full Name'].get(), self.e['Role'].get(), self.e['Phone'].get(), self.e['Shift'].get()))
        messagebox.showinfo("Added","Staff added"); self.load_staff(); self.clear_form()

    def load_staff(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows = self.run("SELECT staff_id, full_name, role, phone, shift FROM staff ORDER BY staff_id DESC", fetch=True)
        if rows:
            for r in rows: self.tree.insert('', 'end', values=r)

    def on_select(self, evt):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])['values']
        self.e['Full Name'].delete(0,tk.END); self.e['Full Name'].insert(0, vals[1])
        self.e['Role'].delete(0,tk.END); self.e['Role'].insert(0, vals[2] or '')
        self.e['Phone'].delete(0,tk.END); self.e['Phone'].insert(0, vals[3] or '')
        self.e['Shift'].delete(0,tk.END); self.e['Shift'].insert(0, vals[4] or '')

    def update_staff(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Select","Choose staff"); return
        sid = self.tree.item(sel[0])['values'][0]
        self.run("UPDATE staff SET full_name=%s, role=%s, phone=%s, shift=%s WHERE staff_id=%s",
                 (self.e['Full Name'].get(), self.e['Role'].get(), self.e['Phone'].get(), self.e['Shift'].get(), sid))
        messagebox.showinfo("Updated","Staff updated"); self.load_staff()

    def delete_staff(self):
        sel = self.tree.selection()
        if not sel: return
        sid = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm","Delete staff?"):
            self.run("DELETE FROM staff WHERE staff_id=%s", (sid,))
            messagebox.showinfo("Deleted","Staff deleted"); self.load_staff()

    def clear_form(self):
        for e in self.e.values():
            e.delete(0, tk.END)
            self.e['gender'].set("Select Gender")
            self.tree.selection_remove(self.tree.selection())


class UsersFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        left = ttk.Frame(self); left.pack(side='left', fill='y', padx=10, pady=10)
        labels = ['Username','Password','Role','Full Name']
        self.e = {}
        for i,l in enumerate(labels):
            ttk.Label(left, text=l).grid(row=i, column=0, sticky='w', pady=3)
            en = ttk.Entry(left, show='*' if l=='Password' else None)
            en.grid(row=i, column=1, pady=3)
            self.e[l] = en
        ttk.Button(left, text="Create User", command=self.create_user).grid(row=len(labels), column=0, columnspan=2, pady=8)

        right = ttk.Frame(self); right.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(right, columns=('id','username','role','name','created'), show='headings')
        for c,h in zip(('id','username','role','name','created'), ('ID','Username','Role','Full Name','Created')):
            self.tree.heading(c, text=h); self.tree.column(c, width=150)
        self.tree.pack(fill='both', expand=True)
        self.load_users()

    def run(self,q,p=None,fetch=False):
        conn = get_db_connection()
        if not conn: return None
        cur = conn.cursor()
        cur.execute(q,p or ())
        if fetch:
            rows = cur.fetchall(); cur.close(); conn.close(); return rows
        conn.commit(); cur.close(); conn.close(); return True

    def create_user(self):
        username = self.e['Username'].get().strip()
        pwd = self.e['Password'].get().strip()
        role = self.e['Role'].get().strip() or 'reception'
        full = self.e['Full Name'].get().strip()
        if not username or not pwd:
            messagebox.showwarning("Input","Username and password required"); return
        ph = hash_password(pwd)
        try:
            self.run("INSERT INTO users (username, password_hash, role, full_name) VALUES (%s,%s,%s,%s)",
                     (username, ph, role, full))
            messagebox.showinfo("Created","User created"); self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_users(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows = self.run("SELECT user_id, username, role, full_name, created_at FROM users ORDER BY user_id DESC", fetch=True)
        if rows:
            for r in rows: self.tree.insert('', 'end', values=r)
            
if __name__ == "__main__":
    ensure_admin_exists()
    app = HospitalApp()
    app.mainloop()

