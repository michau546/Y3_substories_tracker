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
def filter_substories(query, substories, filter_by, status_filter, chapter_filter):
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
    
    if chapter_filter != 'All':
        filtered = [substory for substory in filtered if substory.get('available from', '') == chapter_filter]

    return filtered

# Function to mark substory as completed
def mark_as_completed(substory_id, completed, substories):
    for substory in substories:
        if substory['id'] == substory_id:
            substory['completed'] = completed
            break

# Function to refresh the table view
def refresh_table(tree, substories):
    for row in tree.get_children():
        tree.delete(row)

    for substory in substories:
        status = "Completed" if substory['completed'] else "Not Completed"
        available_from = substory.get('available from', '')
        tree.insert("", "end", values=(substory['id'], substory['title'], substory['description'], available_from, status))

# Function to handle filtering
def on_filter():
    query = entry_search.get()
    filter_by = filter_option.get()
    status_filter = status_option.get()
    chapter_filter = chapter_option.get()
    filtered_substories = filter_substories(query, substories, filter_by, status_filter, chapter_filter)
    refresh_table(tree, filtered_substories)

# Function to handle checkbox toggling
def on_toggle_completed(event):
    selected_item = tree.selection()
    if selected_item:
        col = tree.identify_column(event.x)
        if col == "#5":  # Only toggle if the "Status" column is clicked
            substory_id = int(tree.item(selected_item, 'values')[0])
            substory = next(sub for sub in substories if sub['id'] == substory_id)
            substory['completed'] = not substory['completed']
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
    elif column_index == 3:  # Sort by Available From
        substories = sorted(substories, key=lambda x: x.get('available from', ''), reverse=sort_reverse[column_index])
    elif column_index == 4:  # Sort by Status
        substories = sorted(substories, key=lambda x: x['completed'], reverse=sort_reverse[column_index])
    
    sort_reverse[column_index] = not sort_reverse[column_index]
    refresh_table(tree, substories)

# Function to change font size only for the Treeview
def change_font_size(delta):
    global current_font_size
    current_font_size += delta
    new_font = (current_font_family, current_font_size)
    style.configure("Treeview", font=new_font)
    style.configure("Treeview.Heading", font=new_font)

# Function to reset font size to default
def reset_font_size():
    global current_font_size
    current_font_size = default_font_size
    new_font = (current_font_family, current_font_size)
    style.configure("Treeview", font=new_font)
    style.configure("Treeview.Heading", font=new_font)

# Function to change font size for the detail window
def change_detail_font_size(detail_frame, description_text, delta):
    global detail_font_size
    detail_font_size += delta
    new_font = (current_font_family, detail_font_size)
    for widget in detail_frame.winfo_children():
        widget.configure(font=new_font)
    description_text.configure(font=new_font)

# Function to reset font size for the detail window
def reset_detail_font_size(detail_frame, description_text):
    global detail_font_size
    detail_font_size = default_font_size
    new_font = (current_font_family, detail_font_size)
    for widget in detail_frame.winfo_children():
        widget.configure(font=new_font)
    description_text.configure(font=new_font)

# Function to open a new window with substory details
def show_details(event):
    selected_item = tree.selection()
    if selected_item:
        substory_id = int(tree.item(selected_item, 'values')[0])
        substory = next(sub for sub in substories if sub['id'] == substory_id)
        
        detail_window = tk.Toplevel(root)
        detail_window.title(f"Details of Substory {substory['id']}")
        detail_window.geometry('900x400')
        detail_window.resizable(False, False)  # Disable resizing
        
        # Use grid layout
        detail_window.grid_columnconfigure(0, weight=1)
        detail_window.grid_rowconfigure(0, weight=1)

        detail_frame = tk.Frame(detail_window)
        detail_frame.grid(sticky='nsew')
        detail_frame.grid_columnconfigure(1, weight=1)

        tk.Label(detail_frame, text="ID:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        tk.Label(detail_frame, text=substory['id']).grid(row=0, column=1, sticky='w', padx=5, pady=5)

        tk.Label(detail_frame, text="Title:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        tk.Label(detail_frame, text=substory['title']).grid(row=1, column=1, sticky='w', padx=5, pady=5)

        tk.Label(detail_frame, text="Description:").grid(row=2, column=0, sticky='ne', padx=5, pady=5)
        description_text = tk.Text(detail_frame, wrap=tk.WORD, height=10, width=80)
        description_text.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        description_text.insert(tk.END, substory['description'])
        description_text.configure(state='disabled')

        tk.Label(detail_frame, text="Available From:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        tk.Label(detail_frame, text=substory.get('available from', '')).grid(row=3, column=1, sticky='w', padx=5, pady=5)

        status = "Completed" if substory['completed'] else "Not Completed"
        tk.Label(detail_frame, text="Status:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
        tk.Label(detail_frame, text=status).grid(row=4, column=1, sticky='w', padx=5, pady=5)

        # Adding font size controls for the detail window
        button_frame = tk.Frame(detail_window)
        button_frame.grid(sticky='ew', pady=10)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        button_increase_font = tk.Button(button_frame, text="Increase Font Size", command=lambda: change_detail_font_size(detail_frame, description_text, 2))
        button_increase_font.grid(row=0, column=0, padx=5)

        button_decrease_font = tk.Button(button_frame, text="Decrease Font Size", command=lambda: change_detail_font_size(detail_frame, description_text, -2))
        button_decrease_font.grid(row=0, column=1, padx=5)

        button_reset_font = tk.Button(button_frame, text="Reset Font Size", command=lambda: reset_detail_font_size(detail_frame, description_text))
        button_reset_font.grid(row=0, column=2, padx=5)

# Loading data
substories = load_data()
sort_reverse = [False, False, False, False, False]  # Sorting flags for columns
current_font_family = 'Helvetica'
default_font_size = 12  # Default font size
current_font_size = default_font_size
detail_font_size = default_font_size

# Creating the main application window
root = tk.Tk()
root.title("Yakuza 3 Substories Manager")
root.geometry('1024x768')  # Set default window size

# Creating the style
style = ttk.Style()
style.configure("Treeview", font=(current_font_family, current_font_size))
style.configure("Treeview.Heading", font=(current_font_family, current_font_size))

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

# Adding Status Filter
label_status = tk.Label(frame_filter, text="Status:")
label_status.pack(side=tk.LEFT, padx=5)
status_option = ttk.Combobox(frame_filter, values=['All', 'Completed', 'Not Completed'])
status_option.set('All')
status_option.pack(side=tk.LEFT, padx=5)

# Adding Chapter Filter
label_chapter = tk.Label(frame_filter, text="Chapter:")
label_chapter.pack(side=tk.LEFT, padx=5)
chapter_option = ttk.Combobox(frame_filter, values=['All', 'chapter 1', 'chapter 2', 'chapter 3', 'chapter 4', 'chapter 5'])
chapter_option.set('All')
chapter_option.pack(side=tk.LEFT, padx=5)

button_filter = tk.Button(frame_filter, text="Filter", command=on_filter)
button_filter.pack(side=tk.LEFT, padx=5)

# Adding font size controls for the Treeview
button_increase_font = tk.Button(frame_filter, text="Increase Font Size", command=lambda: change_font_size(2))
button_increase_font.pack(side=tk.LEFT, padx=5)

button_decrease_font = tk.Button(frame_filter, text="Decrease Font Size", command=lambda: change_font_size(-2))
button_decrease_font.pack(side=tk.LEFT, padx=5)

# Adding reset font size button
button_reset_font = tk.Button(frame_filter, text="Reset Font Size", command=reset_font_size)
button_reset_font.pack(side=tk.LEFT, padx=5)

# Creating a frame for the Treeview and scrollbars
frame_tree = tk.Frame(root)
frame_tree.pack(expand=True, fill=tk.BOTH)

# Creating the table to display substories
columns = ("ID", "Title", "Description", "Available From", "Status")
tree = ttk.Treeview(frame_tree, columns=columns, show='headings')
tree.heading("ID", text="ID", command=lambda: sort_by_column(0))
tree.heading("Title", text="Title", command=lambda: sort_by_column(1))
tree.heading("Description", text="Description", command=lambda: sort_by_column(2))
tree.heading("Available From", text="Available From", command=lambda: sort_by_column(3))
tree.heading("Status", text="Status", command=lambda: sort_by_column(4))

# Set column widths
tree.column("ID", width=50)
tree.column("Title", width=200)
tree.column("Description", width=300)
tree.column("Available From", width=100)
tree.column("Status", width=100)

# Creating scrollbars
vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
hsb = ttk.Scrollbar(frame_tree, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

# Placing the Treeview and scrollbars in the frame
tree.grid(row=0, column=0, sticky='nsew')
vsb.grid(row=0, column=1, sticky='ns')
hsb.grid(row=1, column=0, sticky='ew')

# Configure the frame to expand with the window
frame_tree.grid_rowconfigure(0, weight=1)
frame_tree.grid_columnconfigure(0, weight=1)

# Initial table refresh
refresh_table(tree, substories)

# Binding events
tree.bind("<Double-1>", show_details)
tree.bind("<Button-1>", on_toggle_completed)

# Running the main application loop
root.mainloop()
