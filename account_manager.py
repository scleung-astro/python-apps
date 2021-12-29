# this apps helps you to manage your financial
# account and do the bookkeeping. Let's get a 
# better grasp of your income and expense!
#
# Created by Shing CHi Leung at 14 Sep 2021
#

import datetime
import tkinter as tk
from tkinter import Entry, Text, ttk, Menu, Message, messagebox
from tkinter.filedialog import askopenfilename,  asksaveasfilename
import pandas as pd

class AccountManager():

    def __init__(self):

        self.read_database()

    def read_database(self):
        self.database_df = pd.read_csv("account_checking.csv", index_col=0)

        # clean the empty fields
        self.database_df.fillna("-",inplace=True)

        # Fix the datetime to date format
        self.database_df["Date"] = pd.to_datetime(self.database_df["Date"], format="%Y-%m-%d").dt.date

        # for debug use
        print(self.database_df)

    def save_file(self, filename):

        self.database_df.to_csv(filename)

    def load_file(self, filename):

        del self.database_df 
        self.database_df = pd.read_csv(filename, index_col=0)

        # clean the empty fields
        self.database_df.fillna("-",inplace=True)

        # Fix the datetime to date format
        self.database_df["Date"] = pd.to_datetime(self.database_df["Date"], format="%Y-%m-%d").dt.date

    def get_accounts(self):
        accounts = list(set(self.database_df["From"].unique()).union(set(self.database_df["To"].unique())))

        # the Imbalance acct is removed by hand 
        # because it is just an artificial pool
        #accounts.remove("Inbalance")

        return accounts

    def get_inflow_from(self, acct, acct_target, amount):

        if acct == acct_target:
            return -amount
        else:
            return amount

    def get_records(self, account, sort_key):

        print("Getting record related to {}".format(account))

        df_out = self.database_df[(self.database_df["From"] == account) | (self.database_df["To"] == account)]

        #print(df_out)

        # create the "Total" column for the culmulative sum
        df_out["Total"] = df_out.apply(
            lambda row: self.get_inflow_from(row["From"], account, row["Amount"]), axis=1
            ).cumsum()

        df_out = df_out.sort_values(sort_key)

        # rearrange the columns for pretty output
        df_out = df_out[["ID", "Date", "Purpose", "From", "To", "Amount", "Total", "Remark"]]

        return df_out.to_numpy()

    def remove_entry(self, entry):

        removed_entry = False
        id = entry[0]

        if id in self.database_df["ID"]:
            removed_entry = True
            self.database_df.drop(id, inplace=True)
            
        print(self.database_df)

        return removed_entry

    def create_entry(self, entry):

        id = max(self.database_df["ID"]) + 1
        entry[0] = id

        print(entry)
        self.database_df.loc[id] = entry           
        print(self.database_df)

    def update_entry(self, entry):

        id = entry[0]

        print(id, entry)
        self.database_df.loc[id] = entry           
        print(self.database_df)

class AccountManagerApps(tk.Tk):

    def __init__(self):

        tk.Tk.__init__(self)

        self.AM = AccountManager()

        self.create_widget()

    def quit_app(self):
        self.quit()
        self.destroy()
        quit()

    def create_widget(self):

        # metadata of the apps
        self.title("Account Manager Vers1.0")

        # header of the apps
        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)

        # header File button
        self.file_menu = Menu(self)
        self.file_menu.add_command(label="Save", command=self.save_database)
        self.file_menu.add_command(label="Load", command=self.load_database)
        self.file_menu.add_command(label="Quit", command=self.quit_app)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # header About button
        self.about_menu = Menu(self)
        self.about_menu.add_command(label="Help", command=self.about_app)
        self.menu_bar.add_cascade(label="About", menu=self.about_menu)

        # Top frame for choosing account to view
        self.viewacct_frame = ttk.LabelFrame(self, text="Account Manager")
        self.viewacct_frame.grid(row=1, column=0, columnspan=1, sticky="W")

        # Content for the top frame
        self.accounts = self.AM.get_accounts()
        
        self.viewacct_label = ttk.Label(self.viewacct_frame, text="View Account ")
        self.viewacct_label.grid(row=0, column=0, columnspan=1, stick="W")
        self.viewacct_field = tk.StringVar()
        self.viewacct_input = ttk.Combobox(self.viewacct_frame, width=30, textvariable=self.viewacct_field)
        self.viewacct_input.grid(row=0, column=1, columnspan=1, sticky="W")
        self.viewacct_input["values"] = self.accounts

        self.viewacct_button = ttk.Button(self.viewacct_frame, text="View", command=self.populate_tree)
        self.viewacct_button.grid(row=0, column=2, columnspan=1, sticky="W")
        
        # frame for the detailed transaction
        self.viewacct_frame = ttk.LabelFrame(self, text="Account Detail")
        self.viewacct_frame.grid(row=2, column=0, columnspan=1, sticky="W")

        self.view_account = None
        self.build_tree()

        self.editentry_button = ttk.Button(self.viewacct_frame, text="Edit", command=self.edit_entry)
        self.editentry_button.grid(row=1, column=6, columnspan=1, sticky="WE")

        self.removeentry_button = ttk.Button(self.viewacct_frame, text="Remove", command=self.remove_entry)
        self.removeentry_button.grid(row=1, column=7, columnspan=1, sticky="WE")

        # frame for the transaction editor
        self.editor_frame = ttk.LabelFrame(self, text="Transaction Editor")
        self.editor_frame.grid(row=3, column=0, columnspan=1, sticky="W")

        self.transid_label = ttk.Label(self.editor_frame, text="ID (for edit): ")
        self.transid_label.grid(row=0, column=0, columnspan=1, sticky="W")
        self.transid_field = tk.StringVar()
        self.transid_input = tk.Entry(self.editor_frame, width=23, textvariable=self.transid_field)
        self.transid_input.grid(row=0, column=1, columnspan=1, sticky="W")

        self.transdate_label = ttk.Label(self.editor_frame, text="Date (YYYY-MM-DD): ")
        self.transdate_label.grid(row=1, column=0, columnspan=1, sticky="W")
        self.transdate_field = tk.StringVar()
        self.transdate_input = tk.Entry(self.editor_frame, width=23, textvariable=self.transdate_field)
        self.transdate_input.grid(row=1, column=1, columnspan=1, sticky="W")

        self.transpurpose_label = ttk.Label(self.editor_frame, text=" Purpose: ")
        self.transpurpose_label.grid(row=1, column=2, columnspan=1, sticky="W")
        self.transpurpose_field = tk.StringVar()
        self.transpurpose_input = tk.Entry(self.editor_frame, width=23, textvariable=self.transpurpose_field)
        self.transpurpose_input.grid(row=1, column=3, columnspan=1, sticky="W")

        self.transfrom_label = ttk.Label(self.editor_frame, text="From: ")
        self.transfrom_label.grid(row=2, column=0, columnspan=1, sticky="W")
        self.transfrom_field = tk.StringVar()
        self.transfrom_input = ttk.Combobox(self.editor_frame, width=20, textvariable=self.transfrom_field)
        self.transfrom_input["values"] = self.accounts
        self.transfrom_input.grid(row=2, column=1, columnspan=1, sticky="W")

        self.transto_label = ttk.Label(self.editor_frame, text=" To: ")
        self.transto_label.grid(row=2, column=2, columnspan=1, sticky="W")
        self.transto_field = tk.StringVar()
        self.transto_input = ttk.Combobox(self.editor_frame, width=20, textvariable=self.transto_field)
        self.transto_input["values"] = self.accounts
        self.transto_input.grid(row=2, column=3, columnspan=1, sticky="W")

        self.transamount_label = ttk.Label(self.editor_frame, text="Amount: ")
        self.transamount_label.grid(row=3, column=0, columnspan=1, sticky="W")
        self.transamount_field = tk.StringVar()
        self.transamount_input = tk.Entry(self.editor_frame, width=23, textvariable=self.transamount_field)
        self.transamount_input.grid(row=3, column=1, columnspan=1, sticky="W")

        self.transremark_label = ttk.Label(self.editor_frame, text=" Remark: ")
        self.transremark_label.grid(row=3, column=2, columnspan=1, sticky="W")
        self.transremark_field = tk.StringVar()
        self.transremark_input = tk.Entry(self.editor_frame, width=23, textvariable=self.transremark_field)
        self.transremark_input.grid(row=3, column=3, columnspan=1, sticky="W")

        self.clearentry_button = ttk.Button(self.editor_frame, text="Clear", command=self.clear_entry)
        self.clearentry_button.grid(row=1, column=4, columnspan=1, sticky="WE")

        self.newentry_button = ttk.Button(self.editor_frame, text="Create", command=self.create_entry)
        self.newentry_button.grid(row=2, column=4, columnspan=1, sticky="WE")

        self.updateentry_button = ttk.Button(self.editor_frame, text="Update", command=self.update_entry)
        self.updateentry_button.grid(row=3, column=4, columnspan=1, sticky="WE")

    def save_database(self):
        
        filename = asksaveasfilename()

        if not filename.endswith(".csv"):
            filename += ".csv"

        self.AM.save_file(filename)


    def load_database(self):
        
        filename = askopenfilename()
        self.AM.load_file(filename)

        # refresh the system
        self.accounts = self.AM.get_accounts()  
        self.view_account = None  

        # update all refreshed values
        self.viewacct_input["values"] = self.accounts
        self.transfrom_input["values"] = self.accounts
        self.transto_input["values"] = self.accounts

        # clear all previous input
        self.viewacct_input.delete(0, tk.END)

        # clear tree
        for child in self.tree.get_children():
            self.tree.delete(child)

    def clear_entry(self):

        self.transid_input.delete(0, tk.END)
        self.transdate_input.delete(0, tk.END)
        self.transpurpose_input.delete(0, tk.END)
        self.transfrom_input.delete(0, tk.END)
        self.transto_input.delete(0, tk.END)
        self.transamount_input.delete(0, tk.END)
        self.transremark_input.delete(0, tk.END)


    def edit_entry(self):

        entry_IDs = self.tree.selection()
        print(entry_IDs)

        # only when one entry is selected the app
        # proceeds the edit procedure, otherwise
        # ignore the request
        if len(entry_IDs) == 0 or len(entry_IDs) > 1:
            return

        for entry_ID in entry_IDs:

            item = self.tree.item(entry_ID)['values']
                
            # list
            print(item)

        self.transid_field.set(item[0])
        self.transdate_field.set(item[1])
        self.transpurpose_field.set(item[2])
        self.transfrom_field.set(item[3])
        self.transto_field.set(item[4])
        self.transamount_field.set(item[5])
        self.transremark_field.set(item[7])


    def remove_entry(self):
        
        entry_IDs = self.tree.selection()
        print(entry_IDs)

        # only when one entry is selected the app
        # proceeds the edit procedure, otherwise
        # ignore the request
        if len(entry_IDs) == 0:
            return

        for entry_ID in entry_IDs:

            item = self.tree.item(entry_ID)['values']
            #self.tree.delete(entry_ID)
            self.AM.remove_entry(item)

        self.populate_tree("ID")

    def create_entry(self):
        
        input1 = self.transdate_field.get()
        input2 = self.transpurpose_field.get()
        input3 = self.transfrom_field.get()
        input4 = self.transto_field.get()
        input5 = self.transamount_field.get()
        input6 = self.transremark_field.get()

        input1 = datetime.datetime.strptime(input1, "%Y-%m-%d").date()
        input5 = float(input5)

        entry = [None, input1, input2, input3, input4, input5, input6]

        self.AM.create_entry(entry)

        self.populate_tree("ID")        
        

    def update_entry(self):
        
        input0 = self.transid_field.get()
        input1 = self.transdate_field.get()
        input2 = self.transpurpose_field.get()
        input3 = self.transfrom_field.get()
        input4 = self.transto_field.get()
        input5 = self.transamount_field.get()
        input6 = self.transremark_field.get()

        input0 = int(input0)
        input1 = datetime.datetime.strptime(input1, "%Y-%m-%d").date()
        input5 = round(float(input5),2)

        entry = (input0, input1, input2, input3, input4, input5, input6)

        self.AM.update_entry(entry)

        self.populate_tree("ID")

    def build_tree(self):

        columns = ["#1", "#2", "#3", "#4", "#5", "#6", "#7", "#8"]
        self.tree = ttk.Treeview(self.viewacct_frame, columns=columns, show="headings")

        self.tree.heading("#1", text="ID", command=self.sort_database_by_id)
        self.tree.heading("#2", text="Date", command=self.sort_database_by_date)
        self.tree.heading("#3", text="Purpose")
        self.tree.heading("#4", text="From")
        self.tree.heading("#5", text="To")
        self.tree.heading("#6", text="Amount", command=self.sort_database_by_amount)
        self.tree.heading("#7", text="Total")
        self.tree.heading("#8", text="Remark")

        self.tree.column("#1", width=80, stretch=tk.NO)
        self.tree.column("#2", width=80, stretch=tk.NO)
        self.tree.column("#3", width=80, stretch=tk.NO)
        self.tree.column("#4", width=80, stretch=tk.NO)
        self.tree.column("#5", width=80, stretch=tk.NO)
        self.tree.column("#6", width=60, stretch=tk.NO)
        self.tree.column("#7", width=60, stretch=tk.NO)
        self.tree.column("#8", width=60, stretch=tk.NO)


        self.tree.grid(row=0, column=0, columnspan=8, sticky="we")

        self.tree_scrollbar = ttk.Scrollbar(self.viewacct_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=self.tree_scrollbar.set)
        self.tree_scrollbar.grid(row=0, column=9, columnspan=1, sticky="ns")

    def sort_database_by_id(self):
        self.populate_tree("ID")

    def sort_database_by_date(self):
        self.populate_tree("Date")

    def sort_database_by_amount(self):
        self.populate_tree("Amount")

    def populate_tree(self, sort_key="ID"):

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.view_account = self.viewacct_field.get()
        if self.view_account is None or self.view_account not in self.accounts:
            self.view_account = None
            return

        entries = self.AM.get_records(self.view_account, sort_key)
        for entry in entries:
            entry = list(entry)
            self.tree.insert('', tk.END, values=entry)

    
    def about_app(self):

        new_window = tk.Toplevel(self)
        new_window.title("About this app")

        message_text = "This app helps you to keep track of your financial record." + \
            "Let the app help manage your income and expediture by adding your transactions! " + \
            "The app helps you classify and visualize your cashflow to help you keep track " + \
            "of your current financial health. " + \
            "Developed by Shing Chi Leung at 14 Sep 2021."

        Message(new_window, text=message_text).pack()

        # keep the size of the help window
        new_window.resizable(False, False)

def main():

    apps = AccountManagerApps()
    apps.mainloop()

if __name__=="__main__":
    main()
