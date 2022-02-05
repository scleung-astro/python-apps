import PySimpleGUI as sg
import sqlite3
from sqlite3 import Error

database_path = ""
current_tables = None
viewing_table = None

#sg.theme_previewer()
sg.theme("DarkBlue14")

# -----------------------------------------------------------------------------
def get_database_path():

    col1 = sg.Column([
        [
            sg.Text("Database", size=(10,1)),
            sg.Input(size=(40,1), key="-fileinput"),
            sg.FileBrowse(target="-fileinput", key="-fileBrowse"),
            sg.Button("Create/Open"),
            sg.Exit()
        ]
    ])


    layout = [
        [col1]
    ]

    window = sg.Window("SQL Manager", layout)

    while True:

        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Exit":
            break

        elif event == "Create/Open":
            database_path = values["-fileBrowse"]
            break 

    window.close()

    return database_path

# -----------------------------------------------------------------------------
def help_window():

    txt = """
    Welcome to the SQL manager. This apps helps you to visualize the data
    from a SQL database. Choose the table you want to view and press 'Show',
    then the data from the table will be displayed. You can also extract
    the data from a row by pressing 'Extract' -- you need to pick at least one
    row of course. I hope to put in more option to make it look like a real
    app. :-) \n\n Developer: Shing Chi Leung \n Feb 2022
    """

    layout = [
        [sg.Text(txt, size=(60,20))]
    ]

    window = sg.Window("Help", layout=layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Exit":
            break

    window.close()

# -----------------------------------------------------------------------------

database_path = get_database_path()

# -----------------------------------------------------------------------------

print("Selected database = ", database_path)
conn = None
try: 
    conn = sqlite3.connect(database_path)

except Error as e:  
    print(e)

cur = conn.cursor()



cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
current_tables = [t[0] for t in cur.fetchall()]

col1 = sg.Column([
    [sg.Listbox(current_tables, size=(15,10), key="-tablelistbox")],
    [sg.Button("Show", size=(15,1))]
])

default_headings = [str(i) for i in range(10)]
col2 = sg.Column([
    [sg.Table([[]], headings=default_headings, auto_size_columns=False, def_col_width=10, num_rows=10, key="-tabledata")],
    [sg.Button("Extract", size=(20,1)), sg.Button("Delete", disabled=True, size=(20,1)), sg.Button("Help", size=(20,1)), sg.Exit(size=(20,1))]
])

col3 = sg.Column([
    [sg.Text("Data Editor")],
    [
    sg.Column([[sg.Text("Column 0", size=(10,1), key="-columnt0")], [sg.Input(key="-columnip0", size=(10,1))]]),
    sg.Column([[sg.Text("Column 1", size=(10,1), key="-columnt1")], [sg.Input(key="-columnip1", size=(10,1))]]),
    sg.Column([[sg.Text("Column 2", size=(10,1), key="-columnt2")], [sg.Input(key="-columnip2", size=(10,1))]]),
    sg.Column([[sg.Text("Column 3", size=(10,1), key="-columnt3")], [sg.Input(key="-columnip3", size=(10,1))]]),
    sg.Column([[sg.Text("Column 4", size=(10,1), key="-columnt4")], [sg.Input(key="-columnip4", size=(10,1))]]),
    sg.Column([[sg.Text("Column 5", size=(10,1), key="-columnt5")], [sg.Input(key="-columnip5", size=(10,1))]]),
    sg.Column([[sg.Text("Column 6", size=(10,1), key="-columnt6")], [sg.Input(key="-columnip6", size=(10,1))]]),
    sg.Column([[sg.Text("Column 7", size=(10,1), key="-columnt7")], [sg.Input(key="-columnip7", size=(10,1))]]),
    sg.Column([[sg.Text("Column 8", size=(10,1), key="-columnt8")], [sg.Input(key="-columnip8", size=(10,1))]]),
    sg.Column([[sg.Text("Column 9", size=(10,1), key="-columnt9")], [sg.Input(key="-columnip9", size=(10,1))]])]
])

layout = [
    [col1, col2], 
    [sg.HorizontalSeparator()],
    [col3]
]

window = sg.Window("Table Editor", layout = layout)

def update_title(table, new_headings):

    header_size = min(len(default_headings), len(new_headings))
    for i, (cid, text) in enumerate(zip(default_headings, new_headings)):
        table.heading(cid, text=text)
        window["-columnt"+str(i)].update(value=text)

    for i in range(header_size,10):
        table.heading(default_headings[i], text=str(i))
        window["-columnt"+str(i)].update(value=str(i))


while True: 

    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break

    elif event == "Show":

        print(values["-tablelistbox"])
        if values["-tablelistbox"] != []:
            viewing_table = values["-tablelistbox"][0]
            
            headers = []

            cur.execute("SELECT * FROM " + viewing_table + ";")
            table_data = cur.fetchall()
            
            for h in cur.description:
                if h is not None:
                    headers.append(h[0])

            
            window["-tabledata"].update(values=table_data)
            update_title(window["-tabledata"].Widget, headers)
            
            # clean the bottom row data
            for i in range(10):
                window["-columnip"+str(i)].update(value="")

    elif event == "Extract":

        if values["-tabledata"] != []:
            row = values["-tabledata"][0]
            data = window["-tabledata"].Values[row]

            for i in range(len(headers)):
                window["-columnip"+str(i)].update(value=data[i])

    elif event == "Help":

        help_window()

window.close()
# -----------------------------------------------------------------------------

if cur:
    cur.close()

if conn: 
    conn.close()