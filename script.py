import tkinter as tk
from tkinter import messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading
import requests
import numpy as np
import pandas as pd
import bcrypt
import boto3
from botocore.exceptions import NoCredentialsError
from datetime import datetime
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import psutil
import random
import win32api
import win32con
import win32gui
import win32clipboard

# AWS credentials
AWS_ACCESS_KEY_ID = 'yOUR AWS ACESS KEY'
AWS_SECRET_ACCESS_KEY = 'YOUR AWS SECRET KEY'

# Global variables
users = {}
model = None
history = {'accuracy': [random.random() for _ in range(10)],
           'val_accuracy': [random.random() for _ in range(10)]}
local_file_path = 'data.xlsx'
s3_bucket_name = 'authbucket-project1'
s3_file_path = 'users.xlsx'

# Load resources
def load_resources():
    global users, model
    users = load_users_from_excel(local_file_path)
    model_path = 'auth_model_5_features.h5'
    model = tf.keras.models.load_model(model_path)

def load_users_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        users = {}
        for index, row in df.iterrows():
            username = row['username']
            password = row['password']
            role = 'admin' if index == 2 else 'user'
            users[username] = {'password': password, 'role': role}
        return users
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return {}

def save_users_to_excel(users, local_file_path, s3_bucket_name, s3_file_path):
    try:
        data = {'username': [], 'password': []}
        for username, info in users.items():
            data['username'].append(username)
            data['password'].append(info['password'])
        df = pd.DataFrame(data)
        df.to_excel(local_file_path, index=False)
        print("Users saved to local Excel file successfully.")
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        try:
            s3.upload_file(local_file_path, s3_bucket_name, s3_file_path)
            print(f"Users saved to S3 bucket '{s3_bucket_name}' successfully.")
        except FileNotFoundError:
            print("The file was not found.")
        except NoCredentialsError:
            print("Credentials not available.")
    except Exception as e:
        print(f"Error saving users to Excel file: {e}")

def preprocess_user_data(df):
    df = pd.get_dummies(df, columns=['screen_resolution', 'location', 'login_time'])
    df['os'] = df['os'].apply(lambda x: 1 if x == 'Windows' else 0)
    for col in ['screen_resolution_1920x1080', 'screen_resolution_1280x720', 'location_USA', 'location_India', 'login_time_morning', 'login_time_evening']:
        if col not in df.columns:
            df[col] = 0
    scaler = StandardScaler()
    df[['keystrokes']] = scaler.fit_transform(df[['keystrokes']])
    df = df[['os', 'keystrokes'] + [col for col in df.columns if col not in ['os', 'keystrokes']]]
    return df.astype('float32')

def authenticate(username, password, users, model):
    if username in users and bcrypt.checkpw(password.encode('utf-8'), users[username]['password'].encode('utf-8')):
        user_data = {
            'os': 'Windows',
            'screen_resolution': '1920x1080',
            'keystrokes': np.random.randint(50, 300),
            'location': 'USA',
            'login_time': 'morning'
        }
        user_data_df = pd.DataFrame([user_data])
        user_data_df = preprocess_user_data(user_data_df)
        prediction = model.predict(user_data_df)[0][0]
        if prediction > 0.5:
            return True, users[username]['role'], prediction
        else:
            return False, None, prediction
    else:
        return False, None, 0.0

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def list_users(users):
    user_list = "Current Users:\n"
    user_list += "--------------\n"
    for username, info in users.items():
        user_list += f"Username: {username}, Role: {info['role']}\n"
    return user_list

def delete_user(users, username, local_file_path, s3_bucket_name, s3_file_path):
    if username in users:
        del users[username]
        save_users_to_excel(users, local_file_path, s3_bucket_name, s3_file_path)
        messagebox.showinfo("Success", f"User '{username}' deleted successfully.")
    else:
        messagebox.showerror("Error", f"User '{username}' not found.")

def modify_user(users, username, new_role, local_file_path, s3_bucket_name, s3_file_path):
    if username in users:
        users[username]['role'] = new_role
        save_users_to_excel(users, local_file_path, s3_bucket_name, s3_file_path)
        messagebox.showinfo("Success", f"Role for '{username}' updated to '{new_role}' successfully.")
    else:
        messagebox.showerror("Error", f"User '{username}' not found.")

def register_user():
    username = simpledialog.askstring("Register", "Enter new username:")
    if username:
        if username in users:
            messagebox.showerror("Error", "Username already exists.")
            return
        password = simpledialog.askstring("Register", "Enter new password:", show="*")
        if password:
            hashed_password = hash_password(password)
            users[username] = {'password': hashed_password, 'role': 'user'}
            save_users_to_excel(users, local_file_path, s3_bucket_name, s3_file_path)
            messagebox.showinfo("Success", f"User '{username}' registered successfully.")

def plot_performance_graph():
    fig, axs = plt.subplots(2, 2, figsize=(10, 8), dpi=100)
    cpu_percent = psutil.cpu_percent(interval=1)
    axs[0, 0].bar(['CPU Usage'], [cpu_percent], color='blue')
    axs[0, 0].set_title('CPU Performance')
    axs[0, 0].set_ylim(0, 100)

    disk_usage = psutil.disk_usage('/').percent
    axs[0, 1].bar(['Storage Usage'], [disk_usage], color='green')
    axs[0, 1].set_title('Storage Usage')
    axs[0, 1].set_ylim(0, 100)
    
    network_in = random.randint(0, 1000)
    network_out = random.randint(0, 1000)
    axs[1, 0].bar(['Network In', 'Network Out'], [network_in, network_out], color=['red', 'orange'])
    axs[1, 0].set_title('Network Monitoring')
    
    axs[1, 1].plot(history['accuracy'], label='Train Accuracy')
    axs[1, 1].plot(history['val_accuracy'], label='Validation Accuracy')
    axs[1, 1].set_xlabel('Epochs')
    axs[1, 1].set_ylabel('Accuracy')
    axs[1, 1].legend()
    axs[1, 1].set_title('Neural Network Performance')
    
    for ax in axs.flat:
        ax.grid(True)
    
    fig.tight_layout()
    chart_type = FigureCanvasTkAgg(fig, admin_window)
    chart_type.get_tk_widget().pack()

def admin_interface():
    global admin_window
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Interface")
    admin_window.configure(bg='black')
    
    # Full screen and hide title bar
    admin_window.attributes('-fullscreen', True)
    admin_window.attributes('-topmost', True)
    admin_window.overrideredirect(True)

    def list_users_action():
        users_info = list_users(users)
        messagebox.showinfo("List of Users", users_info)

    def delete_user_action():
        username_to_delete = simpledialog.askstring("Delete User", "Enter username to delete:")
        if username_to_delete:
            delete_user(users, username_to_delete, local_file_path, s3_bucket_name, s3_file_path)

    def modify_user_role_action():
        username_to_modify = simpledialog.askstring("Modify User Role", "Enter username to modify:")
        if username_to_modify:
            new_role = simpledialog.askstring("New Role", "Enter new role (admin/user):").lower()
            if new_role in ['admin', 'user']:
                modify_user(users, username_to_modify, new_role, local_file_path, s3_bucket_name, s3_file_path)
            else:
                messagebox.showerror("Error", "Invalid role. Must be 'admin' or 'user'.")

    tk.Button(admin_window, text="Register User", command=register_user, bg="black", fg="white").pack(pady=10)
    tk.Button(admin_window, text="List Users", command=list_users_action, bg="black", fg="white").pack(pady=10)
    tk.Button(admin_window, text="Delete User", command=delete_user_action, bg="black", fg="white").pack(pady=10)
    tk.Button(admin_window, text="Modify User Role", command=modify_user_role_action, bg="black", fg="white").pack(pady=10)
    tk.Button(admin_window, text="Plot Performance Graph", command=plot_performance_graph, bg="black", fg="white").pack(pady=10)
    tk.Button(admin_window, text="Exit", command=exit_application, bg="black", fg="white").pack(pady=20)

def exit_application():
    global admin_window
    admin_window.destroy()
    root.attributes('-fullscreen', False)  # Restore root window size
    root.deiconify()  # Show root window if hidden
    root.quit()  # Exit the application

def setup_gui():
    global root
    root = tk.Tk()
    root.title("Adaptive Authentication System")
    root.configure(bg='black')
    
    # Full screen and hide title bar
    root.attributes('-fullscreen', True)
    root.attributes('-topmost', True)
    root.overrideredirect(True)
    
    heading = tk.Label(root, text="ADAPTIVE AUTHENTICATION SYSTEM", font=("Arial", 24), bg="black", fg="white")
    heading.pack(pady=20)

    def update_time_and_internet():
        while True:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                requests.get('https://www.google.com/', timeout=3)
                internet_status = 'Connected'
            except requests.ConnectionError:
                internet_status = 'Disconnected'
            time_label.config(text=f"Time: {now} | Internet: {internet_status}")
            time.sleep(1)

    time_label = tk.Label(root, text="", font=("Arial", 12), bg="black", fg="white")
    time_label.pack(side=tk.BOTTOM, anchor=tk.SE, padx=20, pady=10)
    
    threading.Thread(target=update_time_and_internet, daemon=True).start()

    username_label = tk.Label(root, text="Username:", font=("Arial", 14), bg="black", fg="white")
    username_label.pack(pady=5)
    username_entry = tk.Entry(root, font=("Arial", 14))
    username_entry.pack(pady=5)

    password_label = tk.Label(root, text="Password:", font=("Arial", 14), bg="black", fg="white")
    password_label.pack(pady=5)
    password_entry = tk.Entry(root, font=("Arial", 14), show="*")
    password_entry.pack(pady=5)

    def on_login():
        username = username_entry.get()
        password = password_entry.get()
        authenticated, role, prediction = authenticate(username, password, users, model)
        if authenticated:
            messagebox.showinfo("Success", f"Login successful as {role}. Prediction: {prediction:.2f}")
            if role == 'admin':
                admin_interface()
            elif role=='user':
                root.quit()
        else:
            messagebox.showerror("Error", "Login failed. Please check your credentials.")

    login_button = tk.Button(root, text="Login", command=on_login, font=("Arial", 14), bg="black", fg="white")
    login_button.pack(pady=20)

    # Function to handle the Alt+F4 key combination
    def on_wm_delete_window():
        messagebox.showwarning("Warning", "Trying to close might cause system lockdown")

    # Override the window close (Alt+F4) event
    root.protocol("WM_DELETE_WINDOW", on_wm_delete_window)

    root.mainloop()

if __name__ == "__main__":
    load_resources()
    setup_gui()
