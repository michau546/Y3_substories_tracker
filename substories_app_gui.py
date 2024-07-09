import json
import tkinter as tk
from tkinter import ttk

# Function to load data from JSON file
def load_data():
    with open('substories.json', 'r') as file:
        return json.load(file)

# Function to save data to JSON file
def save_data(substories):
    with open('substories.json', 'w') as file:
        json.dump(substories, file, indent=4)

# Function to filter substories
def filter_substories(query, substories, filter_by, status_filter):
    filtered = substories
    if filter_by == 'ID':
        filtered = [substory for substory in substories if query in str(substory['id'])]
    elif filter_by == 'Title':
        filtered = [substory for substory in substories if query.lower() in substory['title'].lower()]
    elif filter_by == 'Description':
        filtered = [substory for substory in substories if query.lower() in substory['description'].lower()]

    if status_filter == 'Completed':
        filtered = [substory for substory in filtered if substory['completed']]
    elif status_filter == 'Not Completed':
        filtered = [substory for substory in filtered if not substory['completed']]

    return filtered

# Function to mark substory as completed
def mark_as_completed(substory_id, substories):
    for substory in substories:
        if substory['id'] == substory_id:
            substory['completed'] = not substory['completed']
            break

# Function to refresh the table view
def refresh_table(tree, substories):
    for row in tree.get_children():
        tree.delete(row)
    for substory in substories:
        status = "Completed" if substory['completed'] else "Not Completed"
        tree.insert("", "end", values=(substory['id'], substory['title'], substory['description'], status))

# Function to handle filtering
def on_filter():
    query = entry_search.get()
    filter_by = filter_option.get()
    status_filter = status_option.get()
    filtered_substories = filter_substories(query, substories, filter_by, status_filter)
    refresh_table(tree, filtered_substories)

# Function to handle toggling completion of substory
def on_toggle_completed(event):
    selected_item = tree.selection()[0]
    selected_substory_id = int(tree.item(selected_item, 'values')[0])
    mark_as_completed(selected_substory_id, substories)
    save_data(substories)
    refresh_table(tree, substories)

# Function to handle sorting columns
def sort_by_column(column_index):
    global substories
    if column_index == 0:  # Sort by ID
        substories = sorted(substories, key=lambda x: x['id'], reverse=sort_reverse[column_index])
    elif column_index == 1:  # Sort by Title
        substories = sorted(substories, key=lambda x: x['title'], reverse=sort_reverse[column_index])
    elif column_index == 2:  # Sort by Description
        substories = sorted(substories, key=lambda x: x['description'], reverse=sort_reverse[column_index])
    elif column_index == 3:  # Sort by Status
        substories = sorted(substories, key=lambda x: x['completed'], reverse=sort_reverse[column_index])
    
    sort_reverse[column_index] = not sort_reverse[column_index]
    refresh_table(tree, substories)

# Loading data
substories = load_data()
sort_reverse = [False, False, False, False]  # Sorting flags for columns

# Creating the main application window
root = tk.Tk()
root.title("Yakuza 3 Substories Manager")
root.geometry('1024x768')  # Set default window size

# Creating the frame for filtering options
frame_filter = tk.Frame(root)
frame_filter.pack(pady=10)

label_search = tk.Label(frame_filter, text="Search:")
label_search.pack(side=tk.LEFT)

entry_search = tk.Entry(frame_filter)
entry_search.pack(side=tk.LEFT, padx=5)

filter_option = ttk.Combobox(frame_filter, values=['ID', 'Title', 'Description'])
filter_option.set('Title')
filter_option.pack(side=tk.LEFT)

status_option = ttk.Combobox(frame_filter, values=['All', 'Completed', 'Not Completed'])
status_option.set('All')
status_option.pack(side=tk.LEFT, padx=5)

button_filter = tk.Button(frame_filter, text="Filter", command=on_filter)
button_filter.pack(side=tk.LEFT, padx=5)

# Creating the table to display substories
columns = ("ID", "Title", "Description", "Status")
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading("ID", text="ID", command=lambda: sort_by_column(0))
tree.heading("Title", text="Title", command=lambda: sort_by_column(1))
tree.heading("Description", text="Description", command=lambda: sort_by_column(2))
tree.heading("Status", text="Status", command=lambda: sort_by_column(3))

# Set column widths
tree.column("ID", width=50)
tree.column("Title", width=200)
tree.column("Description", width=500)
tree.column("Status", width=100)

tree.pack(expand=True, fill=tk.BOTH)

# Initial table refresh
refresh_table(tree, substories)

# Binding events
tree.bind("<Double-1>", on_toggle_completed)

# Running the main application loop
root.mainloop()
