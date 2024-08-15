from tkinter import *
from tkinter import ttk
import customtkinter

import pyperclip

class TableFrame(customtkinter.CTkFrame):
    def __init__(self, master, titles, values, height):
        super().__init__(master)
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_rowconfigure(index=0, weight=1)
        self.titles = titles
        self.values = values
        self.height = height
        self.create_tree()
    
    def create_tree(self):
        # Add a Treeview widget
        self.tree = ttk.Treeview(self, column=self.titles, show='headings', height=self.height)

        for i in range(len(self.titles)):
            self.tree.column("# "+str(i+1), anchor=CENTER, width=600 if i==4 else 100)
            self.tree.heading("# "+str(i+1), text=self.titles[i])
        
        # Insert the data in Treeview widget
        for i in range(len(self.values)):
            self.tree.insert('', 'end', text=i+1, values=self.values[i])

        self.tree.bind("<<TreeviewSelect>>", lambda x: on_tree_select(self.tree, x))
        self.tree.bind("<Control-Key-c>", lambda x: copy_from_treeview(self.tree, x))

        self.tree.grid(row=0, column=0, padx=10, pady=5, sticky="WSEN")

        def copy_from_treeview(tree, event):
            selection = tree.selection()
            column = tree.identify_column(event.x)
            column_no = int(column.replace("#", "")) - 1
                    
            copy_values = []
            for each in selection:
                try:
                    value = tree.item(each)["values"][column_no]
                    copy_values.append(str(value))
                except:
                    pass
                
            copy_string = "\n".join(copy_values)
            pyperclip.copy(copy_string)
        
        def on_tree_select(tree, event):
                print("selected items:")
                for item in tree.selection():
                    item_text = tree.item(item,"text")
                    print(item_text)

    def clean_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def remove_item(self):
        selected_items = self.tree.selection()        
        for selected_item in selected_items:          
            self.tree.delete(selected_item)

    def get_tree(self, index):
        values = []
        for item in self.tree.get_children():
            values.append(self.tree.item(item, "values")[index].rstrip(","))
        print("Values: ",values)
        return values

    def add_item(self, values):
        for i in range(len(values)):
            self.tree.insert('', 'end', text=i+1, values=values[i])

class FilterFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.text_fields = []
        self.add_text_field()

    def add_text_field(self):
        index = len(self.text_fields)
        frame = customtkinter.CTkFrame(self)
        frame.grid(row=index, column=0, pady=5, sticky="ewn")

        entry = customtkinter.CTkEntry(frame, placeholder_text="Insira NCMs", width=200)
        entry.grid(row=0, column=0, padx=(0, 10))
        entry.configure(validate="key", validatecommand=(self.register(self.validate_number), '%P', '%d'))
        
        btn_add = customtkinter.CTkButton(frame, text="+", width=30, command=self.add_text_field)
        btn_add.grid(row=0, column=1, padx=(0, 10))
        
        btn_remove = customtkinter.CTkButton(frame, text="-", width=30, command=lambda f=frame: self.remove_text_field(f))
        btn_remove.grid(row=0, column=2)

        if index > 0:
            self.text_fields[-1][1].grid_forget()

        self.text_fields.append((entry, btn_add, btn_remove))

    def remove_text_field(self, frame):
        if len(self.text_fields) > 1:
            for widgets in frame.winfo_children():
                widgets.destroy()
            frame.grid_forget()
            self.text_fields.remove(next(filter(lambda f: f[0].master == frame, self.text_fields)))

        if len(self.text_fields) > 0:
            self.text_fields[-1][1].grid(row=0, column=1, padx=(0, 10))

    def validate_number(self, value, action_type):
        if action_type == '1':
            if value.isdigit() and len(value) <= 8:
                return True
            else:
                return False
        else:
            return True

    def get_values(self):
        return [entry.get() for entry, _, _ in self.text_fields]
    
class MainButtonFrame(customtkinter.CTkFrame):
    def __init__(self, master, text):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.variable = customtkinter.StringVar(value="")
        self.text = text
        self.buttons = []
        self.create_buttons()

    def create_buttons(self):
        for i in range(len(self.text)):
            button = customtkinter.CTkButton(self, text = self.text[i], width=300, height=35)
            self.buttons.append(button)
            button.grid(row=i, column=0, padx=10, pady=(10,0), sticky="EW")