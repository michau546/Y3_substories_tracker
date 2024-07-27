import json
import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import configparser

# Define the resource path function
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Function to load data from JSON file
def load_data(json_filename):
    json_path = resource_path(json_filename)
    with open(json_path, 'r') as file:
        return json.load(file)

# Function to save data to JSON file
def save_data(substories, json_filename):
    json_path = resource_path(json_filename)
    with open(json_path, 'w') as file:
        json.dump(substories, file, indent=4)

# Function to load revelations from JSON file
def load_revelations(json_filename):
    json_path = resource_path(json_filename)
    with open(json_path, 'r') as file:
        return json.load(file)

# Function to save revelations data to JSON file
def save_revelations(revelations, json_filename):
    json_path = resource_path(json_filename)
    with open(json_path, 'w') as file:
        json.dump(revelations, file, indent=4)

# Function to filter substories
def filter_substories(query, substories, filter_by, status_filters, chapter_filters, character_filters=[]):
    filtered = substories
    if filter_by == 'ID':
        filtered = [substory for substory in substories if query in str(substory['id'])]
    elif filter_by == 'Title':
        filtered = [substory for substory in filtered if query.lower() in substory['title'].lower()]
    elif filter_by == 'Description':
        filtered = [substory for substory in filtered if query.lower() in substory['description'].lower()]

    if 'All' not in status_filters:
        filtered = [substory for substory in filtered if substory['status'] in status_filters]
    
    if 'All' not in chapter_filters:
        filtered = [substory for substory in filtered if substory.get('available from', '') in chapter_filters]

    if 'All' not in character_filters:
        filtered = [substory for substory in filtered if substory.get('character', '') in character_filters]

    return filtered

# Function to refresh the table view
def refresh_table(tree, substories):
    for row in tree.get_children():
        tree.delete(row)
    for substory in substories:
        if json_filename == 'y4subst.json':
            values = (substory['id'], substory['title'], substory['description'], substory['available from'], substory['status'], substory['character'])
        else:
            values = (substory['id'], substory['title'], substory['description'], substory['available from'], substory['status'])
        tree.insert("", "end", values=values)

# Function to handle filtering
def on_filter():
    query, filter_by, status_filters, chapter_filters, character_filters = get_current_filters()
    if not status_filters:
        status_filters = ['All']
    if not chapter_filters:
        chapter_filters = ['All']
    if not character_filters:
        character_filters = ['All']
    filtered_substories = filter_substories(query, substories, filter_by, status_filters, chapter_filters, character_filters)
    if 'chapter 10' in chapter_filters:
        messagebox.showinfo("Chapter 10 Reminder", "Remember to check substories started previously, some of them can only be completed from now on !!!")
    if not filtered_substories:
        messagebox.showinfo("No Substories Found", "No substories found matching the filters.")
    refresh_table(tree, filtered_substories)

# Function to get current filter settings
def get_current_filters():
    return (entry_search.get(), filter_option.get(),
            [status_listbox.get(i) for i in status_listbox.curselection()],
            [chapter_listbox.get(i) for i in chapter_listbox.curselection()],
            [character_listbox.get(i) for i in character_listbox.curselection()] if json_filename == 'y4subst.json' else [])

# Function to handle status change
def change_status(event):
    selected_items = tree.selection()
    if selected_items:
        new_status = status_combobox.get()
        selected_ids = [int(tree.item(item, 'values')[0]) for item in selected_items]
        for substory_id in selected_ids:
            substory = next(sub for sub in substories if sub['id'] == substory_id)
            substory['status'] = new_status
        save_data(substories, json_filename)

        # Get current filters and reapply them after saving data
        query, filter_by, status_filters, chapter_filters, character_filters = get_current_filters()
        filtered_substories = filter_substories(query, substories, filter_by, status_filters, chapter_filters, character_filters)
        refresh_table(tree, filtered_substories)

        # Re-select the items based on their IDs
        for item in tree.get_children():
            if int(tree.item(item, 'values')[0]) in selected_ids:
                tree.selection_add(item)
                tree.focus(item)

# Function to handle sorting columns
def sort_by_column(column_index):
    global substories
    if column_index == 0:  # Sort by ID
        substories = sorted(substories, key=lambda x: x['id'], reverse=sort_reverse[column_index])
    elif column_index == 1:  # Sort by Title
        substories = sorted(substories, key=lambda x: x['title'], reverse=sort_reverse[column_index])
    elif column_index == 2:  # Sort by Description
        substories = sorted(substories, key=lambda x: x['description'], reverse=sort_reverse[column_index])
    elif column_index == 3:  # Sort by Character (Yakuza 4 only)
        substories = sorted(substories, key=lambda x: x.get('character', ''), reverse=sort_reverse[column_index])
    elif column_index == 4:  # Sort by Available From
        substories = sorted(substories, key=lambda x: x.get('available from', ''), reverse=sort_reverse[column_index])
    elif column_index == 5:  # Sort by Status
        substories = sorted(substories, key=lambda x: x['status'], reverse=sort_reverse[column_index])
    
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
        if isinstance(widget, (tk.Label, tk.Entry, tk.Text, ttk.Combobox, tk.Button)):
            widget.configure(font=new_font)
    description_text.configure(font=new_font)

# Function to reset font size for the detail window
def reset_detail_font_size(detail_frame, description_text):
    global detail_font_size
    detail_font_size = default_font_size
    new_font = (current_font_family, detail_font_size)
    for widget in detail_frame.winfo_children():
        if isinstance(widget, (tk.Label, tk.Entry, tk.Text, ttk.Combobox, tk.Button)):
            widget.configure(font=new_font)
    description_text.configure(font=new_font)

def apply_theme_to_widget(widget, widget_style):
    try:
        if isinstance(widget, tk.Entry):
            widget.configure(background='#333333', foreground='#FFFFFF')
        elif isinstance(widget, tk.Text):
            widget.configure(background='#333333', foreground='#FFFFFF')
        elif isinstance(widget, ttk.Combobox):
            widget_style.configure("TCombobox", fieldbackground='#555555', background='#333333', foreground='#FFFFFF')
        elif isinstance(widget, tk.Frame):
            widget.configure(background='#333333')
        elif isinstance(widget, tk.Label):
            widget.configure(background='#333333', foreground='#FFFFFF')
        elif isinstance(widget, tk.Button):
            widget.configure(background='#333333', foreground='#FFFFFF')
        elif isinstance(widget, ttk.Button):
            widget_style.configure("TButton", background='#333333', foreground='#FFFFFF')
    except tk.TclError as e:
        print(f"Error configuring widget: {e}")

def apply_theme_to_window(window, widgets):
    widget_style = ttk.Style()
    if dark_mode_var.get():
        window.configure(background='#333333')
        for widget in widgets:
            apply_theme_to_widget(widget, widget_style)
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    apply_theme_to_widget(child, widget_style)
    else:
        window.configure(background='#f0f0f0')
        for widget in widgets:
            try:
                if isinstance(widget, tk.Entry):
                    widget.configure(background='#FFFFFF', foreground='#000000')
                elif isinstance(widget, tk.Text):
                    widget.configure(background='#FFFFFF', foreground='#000000')
                elif isinstance(widget, ttk.Combobox):
                    widget_style.configure("TCombobox", fieldbackground='#FFFFFF', background='#f0f0f0', foreground='#000000')
                elif isinstance(widget, tk.Frame):
                    widget.configure(background='#f0f0f0')
                elif isinstance(widget, tk.Label):
                    widget.configure(background='#f0f0f0', foreground='#000000')
                elif isinstance(widget, tk.Button):
                    widget.configure(background='#f0f0f0', foreground='#000000')
                elif isinstance(widget, ttk.Button):
                    widget_style.configure("TButton", background='#f0f0f0', foreground='#000000')
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Entry):
                            child.configure(background='#FFFFFF', foreground='#000000')
                        elif isinstance(child, tk.Text):
                            child.configure(background='#FFFFFF', foreground='#000000')
                        elif isinstance(child, ttk.Combobox):
                            widget_style.configure("TCombobox", fieldbackground='#FFFFFF', background='#f0f0f0', foreground='#000000')
                        elif isinstance(child, tk.Frame):
                            child.configure(background='#f0f0f0')
                        elif isinstance(child, tk.Label):
                            child.configure(background='#f0f0f0', foreground='#000000')
                        elif isinstance(child, tk.Button):
                            child.configure(background='#f0f0f0', foreground='#000000')
                        elif isinstance(child, ttk.Button):
                            widget_style.configure("TButton", background='#f0f0f0', foreground='#000000')
            except tk.TclError as e:
                print(f"Error configuring widget: {e}")

def show_details(event):
    selected_item = tree.selection()
    if selected_item:
        substory_id = int(tree.item(selected_item, 'values')[0])
        substory = next(sub for sub in substories if sub['id'] == substory_id)
        
        detail_window = tk.Toplevel(root)
        detail_window.title(f"Details of Substory {substory['id']}")
        detail_window.geometry('900x400')
        detail_window.resizable(True, True)  # Enable resizing
        
        # Adding a canvas and scrollbar for the entire detail window
        canvas = tk.Canvas(detail_window, background='#333333' if dark_mode_var.get() else '#f0f0f0')
        v_scrollbar = ttk.Scrollbar(detail_window, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(detail_window, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=hsb.set)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        detail_frame = tk.Frame(canvas, background='#333333' if dark_mode_var.get() else '#f0f0f0')
        canvas.create_window((0, 0), window=detail_frame, anchor="nw")

        detail_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        detail_frame.grid_columnconfigure(1, weight=1)

        widgets = []

        widgets.append(tk.Label(detail_frame, text="ID:", background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000'))
        widgets[-1].grid(row=0, column=0, sticky='e', padx=5, pady=5)
        id_entry = tk.Entry(detail_frame, background='#333333' if dark_mode_var.get() else '#FFFFFF', foreground='#FFFFFF' if dark_mode_var.get() else '#000000')
        id_entry.insert(0, substory['id'])
        id_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        widgets.append(id_entry)

        widgets.append(tk.Label(detail_frame, text="Title:", background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000'))
        widgets[-1].grid(row=1, column=0, sticky='e', padx=5, pady=5)
        title_entry = tk.Entry(detail_frame, background='#333333' if dark_mode_var.get() else '#FFFFFF', foreground='#FFFFFF' if dark_mode_var.get() else '#000000')
        title_entry.insert(0, substory['title'])
        title_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        widgets.append(title_entry)

        widgets.append(tk.Label(detail_frame, text="Description:", background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000'))
        widgets[-1].grid(row=2, column=0, sticky='ne', padx=5, pady=5)
        description_text = tk.Text(detail_frame, wrap=tk.WORD, height=10, width=80, background='#333333' if dark_mode_var.get() else '#FFFFFF', foreground='#FFFFFF' if dark_mode_var.get() else '#000000')
        description_text.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        description_text.insert(tk.END, substory['description'])
        widgets.append(description_text)

        widgets.append(tk.Label(detail_frame, text="Available From:", background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000'))
        widgets[-1].grid(row=3, column=0, sticky='e', padx=5, pady=5)
        chapter_option = ttk.Combobox(detail_frame, values=['chapter 3', 'chapter 4', 'chapter 5','chapter 6','chapter 7','chapter 9','chapter 10','chapter 12'])
        chapter_option.set(substory.get('available from', ''))
        chapter_option.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        widgets.append(chapter_option)

        widgets.append(tk.Label(detail_frame, text="Status:", background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000'))
        widgets[-1].grid(row=4, column=0, sticky='e', padx=5, pady=5)
        status_option = ttk.Combobox(detail_frame, values=['Completed', 'Not Completed', 'In Progress'])
        status_option.set(substory['status'])
        status_option.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        status_option.bind("<<ComboboxSelected>>", lambda e: update_status(substory, status_option.get()))
        widgets.append(status_option)

        # Adding font size controls for the detail window
        button_frame = tk.Frame(detail_frame, background='#333333' if dark_mode_var.get() else '#f0f0f0')
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        widgets.append(button_frame)

        button_increase_font = tk.Button(button_frame, text="Increase Font Size", command=lambda: change_detail_font_size(detail_frame, description_text, 2), background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000')
        button_increase_font.grid(row=0, column=0, padx=5)
        widgets.append(button_increase_font)

        button_decrease_font = tk.Button(button_frame, text="Decrease Font Size", command=lambda: change_detail_font_size(detail_frame, description_text, -2), background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000')
        button_decrease_font.grid(row=0, column=1, padx=5)
        widgets.append(button_decrease_font)

        button_reset_font = tk.Button(button_frame, text="Reset Font Size", command=lambda: reset_detail_font_size(detail_frame, description_text), background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000')
        button_reset_font.grid(row=0, column=2, padx=5)
        widgets.append(button_reset_font)

        apply_theme_to_window(detail_window, widgets)

        def on_close():
            substory['id'] = int(id_entry.get())
            substory['title'] = title_entry.get()
            substory['description'] = description_text.get("1.0", tk.END).strip()
            substory['available from'] = chapter_option.get()
            substory['status'] = status_option.get()
            save_data(substories, json_filename)
            
            # Refresh the table without resetting the filters
            query, filter_by, status_filters, chapter_filters, character_filters = get_current_filters()
            filtered_substories = filter_substories(query, substories, filter_by, status_filters, chapter_filters, character_filters)
            refresh_table(tree, filtered_substories)
            
            detail_window.destroy()

        detail_window.protocol("WM_DELETE_WINDOW", on_close)

def update_status(substory, new_status):
    substory['status'] = new_status
    save_data(substories, json_filename)
    refresh_table(tree, substories)
    
    # Re-select the items
    for item in tree.get_children():
        if int(tree.item(item, 'values')[0]) == substory['id']:
            tree.selection_add(item)
            tree.focus(item)

# Function to open a new window with revelation details
def show_revelation_details(event, json_filename):
    selected_item = revelations_tree.selection()
    if selected_item:
        revelation_id = int(revelations_tree.item(selected_item, 'values')[0])
        revelation = next(rev for rev in revelations if rev['id'] == revelation_id)
        
        detail_window = tk.Toplevel(root)
        detail_window.title(f"Details of Revelation {revelation['id']}")
        detail_window.geometry('900x400')
        detail_window.resizable(True, True)  # Enable resizing
        
        # Adding a canvas and scrollbar for the entire detail window
        canvas = tk.Canvas(detail_window, background='#333333' if dark_mode_var.get() else '#f0f0f0')
        v_scrollbar = ttk.Scrollbar(detail_window, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(detail_window, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=hsb.set)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        detail_frame = tk.Frame(canvas, background='#333333' if dark_mode_var.get() else '#f0f0f0')
        canvas.create_window((0, 0), window=detail_frame, anchor="nw")

        detail_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        detail_frame.grid_columnconfigure(1, weight=1)

        widgets = []

        widgets.append(tk.Label(detail_frame, text="ID:", background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000'))
        widgets[-1].grid(row=0, column=0, sticky='e', padx=5, pady=5)
        id_entry = tk.Entry(detail_frame, background='#333333' if dark_mode_var.get() else '#FFFFFF', foreground='#FFFFFF' if dark_mode_var.get() else '#000000')
        id_entry.insert(0, revelation['id'])
        id_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        widgets.append(id_entry)

        widgets.append(tk.Label(detail_frame, text="Title:", background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000'))
        widgets[-1].grid(row=1, column=0, sticky='e', padx=5, pady=5)
        title_entry = tk.Entry(detail_frame, background='#333333' if dark_mode_var.get() else '#FFFFFF', foreground='#FFFFFF' if dark_mode_var.get() else '#000000')
        title_entry.insert(0, revelation['title'])
        title_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        widgets.append(title_entry)

        widgets.append(tk.Label(detail_frame, text="Description:", background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000'))
        widgets[-1].grid(row=2, column=0, sticky='ne', padx=5, pady=5)
        description_text = tk.Text(detail_frame, wrap=tk.WORD, height=10, width=80, background='#333333' if dark_mode_var.get() else '#FFFFFF', foreground='#FFFFFF' if dark_mode_var.get() else '#000000')
        description_text.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        description_text.insert(tk.END, revelation['description'])
        widgets.append(description_text)

        widgets.append(tk.Label(detail_frame, text="Status:", background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000'))
        widgets[-1].grid(row=3, column=0, sticky='e', padx=5, pady=5)
        status_option = ttk.Combobox(detail_frame, values=['Completed', 'Not Completed'])
        status_option.set(revelation['status'])
        status_option.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        status_option.bind("<<ComboboxSelected>>", lambda e: update_revelation_status(revelation, status_option.get(), json_filename))
        widgets.append(status_option)

        # Adding font size controls for the detail window
        button_frame = tk.Frame(detail_frame, background='#333333' if dark_mode_var.get() else '#f0f0f0')
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        widgets.append(button_frame)

        button_increase_font = tk.Button(button_frame, text="Increase Font Size", command=lambda: change_detail_font_size(detail_frame, description_text, 2), background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000')
        button_increase_font.grid(row=0, column=0, padx=5)
        widgets.append(button_increase_font)

        button_decrease_font = tk.Button(button_frame, text="Decrease Font Size", command=lambda: change_detail_font_size(detail_frame, description_text, -2), background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000')
        button_decrease_font.grid(row=0, column=1, padx=5)
        widgets.append(button_decrease_font)

        button_reset_font = tk.Button(button_frame, text="Reset Font Size", command=lambda: reset_detail_font_size(detail_frame, description_text), background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000')
        button_reset_font.grid(row=0, column=2, padx=5)
        widgets.append(button_reset_font)

        apply_theme_to_window(detail_window, widgets)

        def on_close():
            revelation['id'] = int(id_entry.get())
            revelation['title'] = title_entry.get()
            revelation['description'] = description_text.get("1.0", tk.END).strip()
            revelation['status'] = status_option.get()
            save_revelations(revelations, json_filename)

            # Refresh the table without resetting the filters
            refresh_revelations_table(revelations_tree, revelations)
            
            detail_window.destroy()

        detail_window.protocol("WM_DELETE_WINDOW", on_close)

def update_revelation_status(revelation, new_status, json_filename):
    revelation['status'] = new_status
    save_revelations(revelations, json_filename)
    refresh_revelations_table(revelations_tree, revelations)

def refresh_revelations_table(tree, revelations):
    for row in tree.get_children():
        tree.delete(row)
    for revelation in revelations:
        tree.insert("", "end", values=(revelation['id'], revelation['title'], revelation['description'], revelation['status']))

# Function to open the revelations window
def show_revelations(json_filename):
    global revelations, revelations_tree
    revelations = load_revelations(json_filename)
    
    revelations_window = tk.Toplevel(root)
    revelations_window.title("Revelations")
    revelations_window.geometry('800x400')
    revelations_window.resizable(True, True)  # Enable resizing

    columns = ("ID", "Title", "Description", "Status")
    revelations_tree = ttk.Treeview(revelations_window, columns=columns, show='headings')
    revelations_tree.heading("ID", text="ID")
    revelations_tree.heading("Title", text="Title")
    revelations_tree.heading("Description", text="Description")
    revelations_tree.heading("Status", text="Status")

    # Set column widths
    revelations_tree.column("ID", width=50)
    revelations_tree.column("Title", width=150)
    revelations_tree.column("Description", width=450)
    revelations_tree.column("Status", width=100)

    # Creating scrollbars
    vsb = ttk.Scrollbar(revelations_window, orient="vertical", command=revelations_tree.yview)
    hsb = ttk.Scrollbar(revelations_window, orient="horizontal", command=revelations_tree.xview)
    revelations_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    # Placing the Treeview and scrollbars in the frame using grid
    revelations_tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')

    # Configure the frame to expand with the window
    revelations_window.grid_rowconfigure(0, weight=1)
    revelations_window.grid_columnconfigure(0, weight=1)

    # Adding a separate combobox for status change in the main window using grid
    status_combobox_frame = tk.Frame(revelations_window, background='#333333' if dark_mode_var.get() else '#f0f0f0')
    status_combobox_frame.grid(row=2, column=0, columnspan=2, pady=5)

    tk.Label(status_combobox_frame, text="Change Status:", background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000').grid(row=0, column=0, padx=5)
    status_combobox = ttk.Combobox(status_combobox_frame, values=['Completed', 'Not Completed'], state='readonly')
    status_combobox.grid(row=0, column=1, padx=5)
    
    def change_revelation_status(event):
        selected_items = revelations_tree.selection()
        if selected_items:
            new_status = status_combobox.get()
            selected_ids = [int(revelations_tree.item(item, 'values')[0]) for item in selected_items]
            for revelation_id in selected_ids:
                revelation = next(rev for rev in revelations if rev['id'] == revelation_id)
                update_revelation_status(revelation, new_status, json_filename)
            refresh_revelations_table(revelations_tree, revelations)
            
            # Re-select the items based on their IDs
            for item in revelations_tree.get_children():
                if int(revelations_tree.item(item, 'values')[0]) in selected_ids:
                    revelations_tree.selection_add(item)
                    revelations_tree.focus(item)

    status_combobox.bind("<<ComboboxSelected>>", change_revelation_status)

    # Adding character filter for Yakuza 4 revelations
    if json_filename == 'Y4_Revelations.json':
        character_filter_frame = tk.Frame(revelations_window, background='#333333' if dark_mode_var.get() else '#f0f0f0')
        character_filter_frame.grid(row=3, column=0, columnspan=2, pady=5)
        
        character_listbox = tk.Listbox(character_filter_frame, selectmode=tk.MULTIPLE, exportselection=0, height=4)
        characters = ['All', 'Akiyama', 'Saejima', 'Tanimura', 'Kiryu']  # Replace with actual character names
        for character in characters:
            character_listbox.insert(tk.END, character)
        character_listbox.grid(row=0, column=1, padx=5, pady=5)

        def filter_revelations_by_character():
            selected_characters = [character_listbox.get(i) for i in character_listbox.curselection()]
            if 'All' in selected_characters or not selected_characters:
                filtered_revelations = revelations
            else:
                filtered_revelations = [revelation for revelation in revelations if revelation.get('character') in selected_characters]
            refresh_revelations_table(revelations_tree, filtered_revelations)
        
        button_filter_character = tk.Button(character_filter_frame, text="Filter by Character", command=filter_revelations_by_character, background='#333333' if dark_mode_var.get() else '#f0f0f0', foreground='#FFFFFF' if dark_mode_var.get() else '#000000')
        button_filter_character.grid(row=0, column=0, padx=5, pady=5)

    refresh_revelations_table(revelations_tree, revelations)

    # Binding events
    revelations_tree.bind("<Double-1>", lambda event: show_revelation_details(event, json_filename))

    apply_theme_to_window(revelations_window, [status_combobox_frame, status_combobox])

# Load configuration settings
def load_config():
    config = configparser.ConfigParser()
    config.read(resource_path('config.ini'))
    return config

# Save configuration settings
def save_config():
    config = configparser.ConfigParser()
    config['FILTERS'] = {
        'query': entry_search.get(),
        'filter_by': filter_option.get(),
        'status_filter': ','.join([status_listbox.get(i) for i in status_listbox.curselection()]),
        'chapter_filter': ','.join([chapter_listbox.get(i) for i in chapter_listbox.curselection()]),
        'character_filter': ','.join([character_listbox.get(i) for i in character_listbox.curselection()]),
        'json_file': json_filename_var.get()
    }
    config['WINDOW'] = {
        'width': root.winfo_width(),
        'height': root.winfo_height()
    }
    config['THEME'] = {
        'dark_mode': dark_mode_var.get()
    }
    with open(resource_path('config.ini'), 'w') as configfile:
        config.write(configfile)

# Apply configuration settings
def apply_config(config):
    if 'FILTERS' in config:
        filters = config['FILTERS']
        entry_search.insert(0, filters.get('query', ''))
        filter_option.set(filters.get('filter_by', 'Title'))
        
        # Setting status filter
        status_filters = filters.get('status_filter', 'All').split(',')
        for i in range(status_listbox.size()):
            if status_listbox.get(i) in status_filters:
                status_listbox.select_set(i)
        
        # Setting chapter filter
        chapter_filters = filters.get('chapter_filter', 'All').split(',')
        for i in range(chapter_listbox.size()):
            if chapter_listbox.get(i) in chapter_filters:
                chapter_listbox.select_set(i)
        
        # Setting character filter
        character_filters = filters.get('character_filter', 'All').split(',')
        for i in range(character_listbox.size()):
            if character_listbox.get(i) in character_filters:
                character_listbox.select_set(i)
        
        json_filename_var.set(filters.get('json_file', 'Yakuza 3'))
    
    if 'WINDOW' in config:
        window = config['WINDOW']
        width = window.get('width', '1024')
        height = window.get('height', '768')
        root.geometry(f'{width}x{height}')
    
    if 'THEME' in config:
        theme = config['THEME']
        dark_mode_var.set(theme.getboolean('dark_mode', False))
        apply_theme()

def toggle_dark_mode():
    apply_theme()
    save_config()

def apply_theme():
    if dark_mode_var.get():
        style.theme_use('alt')
        style.configure('TFrame', background='#333333')
        style.configure('TLabel', background='#333333', foreground='#FFFFFF')
        style.configure('TButton', background='#555555', foreground='#FFFFFF')
        style.configure('TCombobox', fieldbackground='#555555', background='#333333', foreground='#FFFFFF')
        style.configure('TCheckbutton', background='#333333', foreground='#FFFFFF')
        style.configure('Treeview', background='#555555', foreground='#FFFFFF', fieldbackground='#555555')
        style.configure('Treeview.Heading', background='#333333', foreground='#FFFFFF')
        root.configure(background='#333333')  # Set background color of main window
        frame_filter.configure(background='#333333')  # Set background color of filtering frame
    else:
        style.theme_use('default')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', foreground='#000000')
        style.configure('TButton', background='#f0f0f0', foreground='#000000')
        style.configure('TCombobox', fieldbackground='#FFFFFF', background='#f0f0f0', foreground='#000000')
        style.configure('TCheckbutton', background='#f0f0f0', foreground='#000000')
        style.configure('Treeview', background='#FFFFFF', foreground='#000000', fieldbackground='#FFFFFF')
        style.configure('Treeview.Heading', background='#f0f0f0', foreground='#000000')
        root.configure(background='#f0f0f0')  # Reset background color of main window
        frame_filter.configure(background='#f0f0f0')  # Reset background color of filtering frame

def show_character_filter_window():
    character_filter_window = tk.Toplevel(root)
    character_filter_window.title("Character Filter")
    character_filter_window.geometry('300x200')

    label_character = tk.Label(character_filter_window, text="Character:")
    label_character.pack(pady=5)

    character_listbox = tk.Listbox(character_filter_window, selectmode=tk.MULTIPLE, exportselection=0, height=6)
    characters = ['All', 'Character 1', 'Character 2', 'Character 3']  # Replace with actual character names
    for character in characters:
        character_listbox.insert(tk.END, character)
    character_listbox.pack(pady=5)

    button_apply_filter = tk.Button(character_filter_window, text="Apply Filter", command=apply_character_filter)
    button_apply_filter.pack(pady=10)

# Mapping of JSON filenames to display names
json_file_display_names = {
    'substories.json': 'Yakuza 3',
    'y4subst.json': 'Yakuza 4'
}

def change_json_file(event):
    global substories, json_filename
    display_name = json_filename_var.get()
    json_filename = {v: k for k, v in json_file_display_names.items()}[display_name]
    substories = load_data(json_filename)
    
    if json_filename == 'y4subst.json':
        chapters = ['All', 'chapter 2', 'chapter 3', 'chapter 4', 'finale']
        label_character.pack()
        character_listbox.pack()
    else:
        chapters = ['All', 'chapter 3', 'chapter 4', 'chapter 5', 'chapter 6', 'chapter 7', 'chapter 9', 'chapter 10', 'chapter 12']
        label_character.pack_forget()
        character_listbox.pack_forget()

    chapter_listbox.delete(0, tk.END)
    for chapter in chapters:
        chapter_listbox.insert(tk.END, chapter)

    on_filter()

# Creating the main application window
root = tk.Tk()
root.title("Yakuza Substories Manager")
root.geometry('1024x768')  # Set default window size
root.resizable(True, True)  # Enable window resizing

# Initialize JSON filename variable with display names
json_filename_var = tk.StringVar(value=json_file_display_names['substories.json'])
json_filename = {v: k for k, v in json_file_display_names.items()}[json_filename_var.get()]

# Loading data
substories = load_data(json_filename)
sort_reverse = [False, False, False, False, False, False]  # Sorting flags for columns
current_font_family = 'Helvetica'
default_font_size = 12  # Default font size
current_font_size = default_font_size
detail_font_size = default_font_size

# Creating the style
style = ttk.Style()
style.configure("Treeview", font=(current_font_family, current_font_size))
style.configure("Treeview.Heading", font=(current_font_family, current_font_size))

# Creating the frame for filtering options
frame_filter = tk.Frame(root)
frame_filter.pack(pady=10)

label_search = tk.Label(frame_filter, text="Search:")
label_search.grid(row=0, column=0)

entry_search = tk.Entry(frame_filter)
entry_search.grid(row=0, column=1, padx=5)

filter_option = ttk.Combobox(frame_filter, values=['ID', 'Title', 'Description'])
filter_option.set('Title')
filter_option.grid(row=0, column=2)

# Adding Status Filter
label_status = tk.Label(frame_filter, text="Status:")
label_status.grid(row=1, column=0, padx=5, pady=5)

status_listbox = tk.Listbox(frame_filter, selectmode=tk.MULTIPLE, exportselection=0, height=4)
statuses = ['All', 'Completed', 'Not Completed', 'In Progress']
for status in statuses:
    status_listbox.insert(tk.END, status)
status_listbox.grid(row=1, column=1, padx=5, pady=5)

# Adding Chapter Filter
label_chapter = tk.Label(frame_filter, text="Chapter:")
label_chapter.grid(row=1, column=2, padx=5, pady=5)

chapter_listbox = tk.Listbox(frame_filter, selectmode=tk.MULTIPLE, exportselection=0, height=4)
chapters = ['All', 'chapter 3', 'chapter 4', 'chapter 5', 'chapter 6', 'chapter 7', 'chapter 9', 'chapter 10', 'chapter 12']
for chapter in chapters:
    chapter_listbox.insert(tk.END, chapter)
chapter_listbox.grid(row=1, column=3, padx=5, pady=5)

# Adding Character Filter
label_character = tk.Label(frame_filter, text="Character:")
label_character.grid(row=1, column=4, padx=5, pady=5)

character_listbox = tk.Listbox(frame_filter, selectmode=tk.MULTIPLE, exportselection=0, height=4)
characters = ['All', 'Akiyama', 'Saejima', 'Tanimura', 'Kiryu']  # Replace with actual character names
for character in characters:
    character_listbox.insert(tk.END, character)
character_listbox.grid(row=1, column=5, padx=5, pady=5)
if json_filename != 'y4subst.json':
    label_character.pack_forget()
    character_listbox.pack_forget()

# Adding the filter button
button_filter = tk.Button(frame_filter, text="Filter", command=on_filter)
button_filter.grid(row=0, column=6, padx=5, pady=5)

# Adding font size controls for the Treeview
button_increase_font = tk.Button(frame_filter, text="Increase Font Size", command=lambda: change_font_size(2))
button_increase_font.grid(row=2, column=0, padx=5, pady=5)

button_decrease_font = tk.Button(frame_filter, text="Decrease Font Size", command=lambda: change_font_size(-2))
button_decrease_font.grid(row=2, column=1, padx=5, pady=5)

# Adding reset font size button
button_reset_font = tk.Button(frame_filter, text="Reset Font Size", command=reset_font_size)
button_reset_font.grid(row=2, column=2, padx=5, pady=5)

# Adding button to show revelations
button_revelations = tk.Button(frame_filter, text="Show Revelations", command=lambda: show_revelations('revelations.json' if json_filename == 'substories.json' else 'Y4_Revelations.json'))
button_revelations.grid(row=2, column=3, padx=5, pady=5)

# Adding dark mode toggle
dark_mode_var = tk.BooleanVar()
dark_mode_checkbutton = tk.Checkbutton(frame_filter, text="Dark Mode", variable=dark_mode_var, command=toggle_dark_mode)
dark_mode_checkbutton.grid(row=2, column=4, padx=5, pady=5)

# Adding JSON file selection
label_json_file = tk.Label(frame_filter, text="Select JSON file:")
label_json_file.grid(row=0, column=4, padx=5, pady=5)

json_file_combobox = ttk.Combobox(frame_filter, textvariable=json_filename_var, values=list(json_file_display_names.values()))
json_file_combobox.grid(row=0, column=5, padx=5, pady=5)
json_file_combobox.bind("<<ComboboxSelected>>", change_json_file)

# Creating a frame for the Treeview and scrollbars
frame_tree = tk.Frame(root)
frame_tree.pack(expand=True, fill=tk.BOTH)

# Creating the table to display substories
columns = ("ID", "Title", "Description", "Available From", "Status")
if json_filename == 'y4subst.json':
    columns = ("ID", "Title", "Description", "Character", "Available From", "Status")

tree = ttk.Treeview(frame_tree, columns=columns, show='headings', selectmode='extended')
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
if json_filename == 'y4subst.json':
    tree.column("Character", width=100)

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

# Adding a separate combobox for status change in the main window
status_combobox_frame = tk.Frame(root)
status_combobox_frame.pack(pady=5)

tk.Label(status_combobox_frame, text="Change Status:").pack(side=tk.LEFT)
status_combobox = ttk.Combobox(status_combobox_frame, values=['Completed', 'Not Completed', 'In Progress'], state='readonly')
status_combobox.pack(side=tk.LEFT)
status_combobox.bind("<<ComboboxSelected>>", change_status)

# Save configuration settings on exit
def on_exit():
    save_config()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_exit)

# Load and apply configuration settings
config = load_config()

# Apply the JSON file selection logic initially
change_json_file(None)

# Initial table refresh
on_filter()

# Binding events
tree.bind("<Double-1>", show_details)

# Apply configuration settings after the UI has been built
apply_config(config)

# Start the main loop
root.mainloop()
