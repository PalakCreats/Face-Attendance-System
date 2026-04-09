import cv2
import sqlite3
import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import threading

#from sqlalchemy import delete

# ---------------- Database Setup ----------------
conn = sqlite3.connect("attendance.db",check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    date TEXT,
    time TEXT
)
""")
conn.commit()

# ---------------- Face Detection Setup ----------------
haar_cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(haar_cascade_path)

# ---------------- Functions ----------------
def start_attendance():
    def run_camera():
        name = name_entry.get().strip()
        if name == "":
            messagebox.showerror("Error", "Please enter your name!")
            return

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # DirectShow backend
        detected = False

        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Failed to grab frame")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=3,
                minSize=(50,50)
            )

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 4)
                detected = True

            cv2.imshow("Face Detection Attendance", frame)

            if cv2.waitKey(1) & 0xFF == ord('q') or detected:
                break

        cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)  # ensures window closes

        if detected:
            now = datetime.datetime.now()
            cursor.execute(
                "INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
                (name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"))
            )
            conn.commit()
            messagebox.showinfo("Success", f"Attendance marked for {name}")
        else:
            messagebox.showwarning("Not Detected", "No face detected! Try again.")

    threading.Thread(target=run_camera).start()

def view_attendance():
    cursor.execute("SELECT * FROM attendance")
    records = cursor.fetchall()

    view_win = tk.Toplevel(root)
    view_win.title("Attendance Records")
    view_win.geometry("500x300")

    tree = ttk.Treeview(view_win, columns=("ID", "Name", "Date", "Time"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Date", text="Date")
    tree.heading("Time", text="Time")
    tree.pack(fill="both", expand=True)

    for row in records:
        tree.insert("", tk.END, values=row)


# ---------------- GUI ----------------
root = tk.Tk()
root.title("Face Detection Attendance")
root.geometry("400x250")

tk.Label(root, text="Enter Your Name").pack(pady=10)
name_entry = tk.Entry(root)
name_entry.pack(pady=5)

tk.Button(root, text="Start Attendance", command=start_attendance).pack(pady=10)
tk.Button(root, text="View Attendance", command=view_attendance).pack(pady=5)

root.mainloop()