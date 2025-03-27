import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
from tkcalendar import DateEntry
import tkinter.simpledialog as sd

DATA_FILE = "activity_data.json"
GOAL_FILE = "goal_data.json"

# Load saved activities
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Save activities
def save_data(activities):
    with open(DATA_FILE, "w") as file:
        json.dump(activities, file, indent=2)

# Load goals
def load_goals():
    try:
        with open(GOAL_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save goals
def save_goals(goal_data):
    with open(GOAL_FILE, "w") as file:
        json.dump(goal_data, file)

# Set activity goal
def set_goal():
    activity = simpledialog.askstring("Set Goal", "Enter activity name:")
    if not activity:
        return
    goal_hours = simpledialog.askinteger("Set Goal", "Enter weekly goal (hours):")
    if goal_hours is None:
        return
    
    # Load existing goals
    goal_data = load_goals()
    goal_data[activity] = goal_hours * 60  # Convert to minutes
    save_goals(goal_data)
    messagebox.showinfo("Goal Set", f"Goal for {activity}: {goal_hours} hours per week")

# Show all activity goals
def show_all_goals():
    goal_data = load_goals()
    if not goal_data:
        messagebox.showinfo("No Goals", "No activity goals set!")
        return
    goals = "\n".join([f"{activity}: {goal // 60} hours ({goal % 60} minutes)" for activity, goal in goal_data.items()])
    messagebox.showinfo("Activity Goals", goals)

# Show activity goal progress
def show_goal_progress():
    # Load data
    activity_data = load_data()
    goal_data = load_goals()

    # Create a new window for goal progress
    progress_window = tk.Toplevel(root)
    progress_window.title("Activity Goal Progress")
    progress_window.geometry("500x400")

    # Convert to DataFrame
    df = pd.DataFrame(activity_data)

    if df.empty:
        messagebox.showinfo("No Data", "No activities recorded!")
        progress_window.destroy()
        return
    
    # Ensure start_time is datetime
    df["start_time"] = pd.to_datetime(df["start_time"])
    
    # Calculate weekly progress
    start_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
    weekly_df = df[df["start_time"] >= start_of_week]
    
    # Create Treeview
    columns = ("Activity", "Goal (mins)", "Actual (mins)", "Percentage")
    tree = ttk.Treeview(progress_window, columns=columns, show="headings")
    
    # Define headings
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")
    
    # Populate data
    for activity, goal in goal_data.items():
        actual_time = weekly_df[weekly_df["activity"] == activity]["time_spent"].sum()
        percentage = (actual_time / goal) * 100 if goal else 0
        tree.insert("", "end", values=(
            activity, 
            f"{goal} mins", 
            f"{actual_time} mins", 
            f"{percentage:.1f}%"
        ))
    
    tree.pack(padx=10, pady=10, fill="both", expand=True)

# Show today's graph
def show_today_graph():
    # Load data
    activity_data = load_data()

    # Convert to DataFrame
    df = pd.DataFrame(activity_data)

    if df.empty:
        messagebox.showinfo("No Data", "No activities recorded today!")
        return
    
    # Ensure start_time is datetime
    df["start_time"] = pd.to_datetime(df["start_time"])
    
    today = datetime.now().date()
    today_df = df[df["start_time"].dt.date == today]
    
    if today_df.empty:
        messagebox.showinfo("No Data", "No activities recorded today!")
        return
    
    # Group by activity and sum time spent
    activity_totals = today_df.groupby("activity")["time_spent"].sum()
    
    # Remove any zero values
    activity_totals = activity_totals[activity_totals > 0]
    
    if activity_totals.empty:
        messagebox.showinfo("No Data", "No valid activities to display!")
        return
    
    plt.figure(figsize=(10, 6))
    plt.pie(activity_totals, labels=activity_totals.index, autopct="%1.1f%%", startangle=140)
    plt.title("Today's Activity Breakdown", fontsize=16)
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

# Show weekly graph
def show_weekly_graph():
    # Load data
    activity_data = load_data()

    # Convert to DataFrame
    df = pd.DataFrame(activity_data)

    if df.empty:
        messagebox.showinfo("No Data", "No activities recorded this week!")
        return
    
    # Ensure start_time is datetime
    df["start_time"] = pd.to_datetime(df["start_time"])
    
    start_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
    weekly_df = df[df["start_time"] >= start_of_week]
    
    if weekly_df.empty:
        messagebox.showinfo("No Data", "No activities recorded this week!")
        return
    
    # Group by activity and sum time spent
    weekly_totals = weekly_df.groupby("activity")["time_spent"].sum()
    
    # Remove any zero values
    weekly_totals = weekly_totals[weekly_totals > 0]
    
    if weekly_totals.empty:
        messagebox.showinfo("No Data", "No valid activities to display!")
        return
    
    plt.figure(figsize=(10, 6))
    plt.pie(weekly_totals, labels=weekly_totals.index, autopct="%1.1f%%", startangle=140)
    plt.title("Weekly Activity Breakdown", fontsize=16)
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

# Custom dialog for adding activity with improved date and time selection
class ActivityDialog(sd.Dialog):
    def body(self, master):
        # Activity Name
        tk.Label(master, text="Activity Name:").grid(row=0, column=0, sticky="w")
        self.activity_entry = tk.Entry(master, width=30)
        self.activity_entry.grid(row=0, column=1, padx=5, pady=5)

        # Date Picker
        tk.Label(master, text="Date:").grid(row=1, column=0, sticky="w")
        self.date_picker = DateEntry(master, width=12, background='darkblue', foreground='white', 
                                     date_pattern='y-mm-dd', showweeknumbers=False)
        self.date_picker.grid(row=1, column=1, padx=5, pady=5)

        # Hour Spinbox
        tk.Label(master, text="Hour (24-hour format):").grid(row=2, column=0, sticky="w")
        self.hour_spinbox = tk.Spinbox(master, from_=0, to=23, width=5, format="%02.0f")
        self.hour_spinbox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Minute Spinbox
        tk.Label(master, text="Minute:").grid(row=3, column=0, sticky="w")
        self.minute_spinbox = tk.Spinbox(master, from_=0, to=59, width=5, format="%02.0f")
        self.minute_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Duration
        tk.Label(master, text="Duration (minutes):").grid(row=4, column=0, sticky="w")
        self.duration_entry = tk.Entry(master, width=10)
        self.duration_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        return self.activity_entry  # initial focus

    def apply(self):
        # Validate and collect inputs
        activity = self.activity_entry.get().strip()
        if not activity:
            messagebox.showerror("Error", "Activity name cannot be empty!")
            return

        try:
            duration = int(self.duration_entry.get())
            if duration <= 0:
                raise ValueError("Duration must be positive")
        except ValueError:
            messagebox.showerror("Error", "Invalid duration. Please enter a positive number.")
            return

        # Construct datetime
        selected_date = self.date_picker.get_date()
        hour = int(self.hour_spinbox.get())
        minute = int(self.minute_spinbox.get())
        
        start_time = datetime(
            selected_date.year, 
            selected_date.month, 
            selected_date.day, 
            hour, 
            minute
        )
        
        # Calculate end time
        end_time = start_time + timedelta(minutes=duration)
        
        # Prepare activity entry
        new_activity = {
            "activity": activity,
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_time.strftime("%m/%d/%Y %I:%M %p"),
            "time_spent": float(duration),
            "duration": 0
        }
        
        # Load and save activities
        activities = load_data()
        activities.append(new_activity)
        save_data(activities)
        
        messagebox.showinfo("Success", "Activity added!")

# Add an activity with new dialog
def add_activity():
    dialog = ActivityDialog(root, title="Add Activity")

# Main UI setup
root = tk.Tk()
root.title("Activity Tracker")
root.geometry("300x500")  # Make the window a bit taller

frame = tk.Frame(root)
frame.pack(pady=20)

# Style buttons
style = ttk.Style()
style.configure("TButton", font=("Arial", 10), padding=5)

# Add buttons with consistent styling
btn_add = ttk.Button(frame, text="Add Activity", command=add_activity)
btn_add.pack(pady=5, fill="x")

btn_goal = ttk.Button(frame, text="Set Activity Goal", command=set_goal)
btn_goal.pack(pady=5, fill="x")

btn_goal_progress = ttk.Button(frame, text="Show Goal Progress", command=show_goal_progress)
btn_goal_progress.pack(pady=5, fill="x")

btn_today_graph = ttk.Button(frame, text="Show Today's Graph", command=show_today_graph)
btn_today_graph.pack(pady=5, fill="x")

btn_weekly_graph = ttk.Button(frame, text="Show Weekly Graph", command=show_weekly_graph)
btn_weekly_graph.pack(pady=5, fill="x")

btn_show_goals = ttk.Button(frame, text="Show All Activity Goals", command=show_all_goals)
btn_show_goals.pack(pady=5, fill="x")

root.mainloop()