#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
import tkinter as tk
import sqlite3 as sql

class DbViewer:
    def __init__(self,db):
        self.cleared = False
        self.myParent = tk.Tk()
        self.myParent.title("Database Viewer")
        self.myDB = db
        self.myDBcursor = self.myDB.cursor()

        self.searchResults = []

        self.searchContainer = tk.Frame(self.myParent)
        self.searchContainer.grid(row=0,column=0)

        tk.Label(self.searchContainer,text="Search:").grid(row=0,column=0)
        self.searchBar = tk.Entry(self.searchContainer,width=60,font=("Times",14))
        self.searchBar.bind("<KeyRelease>",self.searchUpdate)
        self.searchBar.grid(row=0,column=1)

        self.resultsContainer = tk.Frame(self.myParent)
        self.resultsContainer.grid(row=1,column=0)

        self.formContainer = tk.Frame(self.myParent)
        self.formContainer.grid(row=2,column=0)

        self.buttonContainer = tk.Frame(self.myParent)
        self.buttonContainer.grid(row=3,column=0)

        self.editButton = tk.Button(self.buttonContainer)
        self.editButton.configure(text="Edit")
        self.editButton.grid(row=0,column=0)

        self.closeButton = tk.Button(self.buttonContainer, command=self.closeViewer)
        self.closeButton.configure(text="Close")
        self.closeButton.grid(row=0,column=1)

    def searchUpdate(self,event):
        for result in self.searchResults:
            result.destroy()
        self.searchResults=[]
        if self.searchBar.get() == "":
            self.resultsContainer.grid_forget()
        else:
            self.resultsContainer.grid(row=1,column=0)
            value = ('%'+self.searchBar.get()+'%',)
            self.myDBcursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.myDBcursor.fetchall()
            searchString = ""
            for table in tables:
                searchString += "SELECT name FROM " + table[0] + " WHERE name LIKE '" + value[0] + "' UNION ALL "
            searchString = searchString[:-10]
            #print(searchString)
            results = self.myDBcursor.execute(searchString)
            i = 0
            for row in results:
                self.searchResults.append(tk.Label(self.resultsContainer,text=row[0]))
                self.searchResults[i].grid(row=i,column=0)
                i += 1

    def closeViewer(self):
        print("Close Database Viewer")
        self.myParent.destroy()
        del self.myParent
        del self.myDB
        del self.myDBcursor
        del self.searchContainer
        del self.formContainer
        del self.buttonContainer
        del self.editButton
        del self.closeButton
        self.cleared = True

class ArticleBuilder:
    def __init__(self,db,formType,formEntries):
        self.cleared = False
        self.myParent = tk.Tk()
        self.formType = formType
        self.myParent.title(self.formType+" Builder")
        self.myDB = db
        self.myDBcursor = self.myDB.cursor()

        self.formContainer = tk.Frame(self.myParent)
        self.formContainer.grid(row=0,column=0)

        row=0
        self.entries = {}
        for label,form in formEntries.items():
            tk.Label(self.formContainer,text=label+":").grid(row=row,column=0,sticky=tk.NE)
            if form=="Entry":
                self.entries[label] = tk.Entry(self.formContainer,width=60,font=("Times",14))
            if form=="Text":
                self.entries[label] = tk.Text(self.formContainer,height=5,width=60,font=("Times",14))
            self.entries[label].configure(borderwidth=1,relief=tk.SUNKEN,highlightcolor="steel blue")
            self.entries[label].grid(row=row,column=1)
            row += 1

        self.buttonContainer = tk.Frame(self.myParent)
        self.buttonContainer.grid(row=1,column=0)

        self.saveButton = tk.Button(self.buttonContainer, command=self.saveArticle)
        self.saveButton.configure(text="Save")
        self.saveButton.grid(row=0,column=0)

        self.closeButton = tk.Button(self.buttonContainer, command=self.closeBuilder)
        self.closeButton.configure(text="Close")
        self.closeButton.grid(row=0,column=1)

    def closeBuilder(self):
        #print("Close " + self.formType + " Builder")
        self.myParent.destroy()
        del self.myParent
        del self.formContainer
        del self.entries
        del self.buttonContainer
        del self.closeButton
        del self.saveButton
        del self.formType
        del self.myDB
        del self.myDBcursor
        self.cleared=True

    def saveArticle(self):
        print("Saving " + self.formType + " Article")
        tableString = "CREATE TABLE IF NOT EXISTS " + self.formType + "("
        insertString = "INSERT INTO " + self.formType + " VALUES ("
        for label,entry in self.entries.items():
            #print(type(entry))
            tableString += label + ", "
            if type(entry)==tk.Entry:
                insertString += "'" + entry.get() + "', "
            if type(entry)==tk.Text:
                insertString += "'" + entry.get(0.0,tk.END) + "', "
        tableString = tableString[:-2]
        insertString = insertString[:-2]
        tableString += ")"
        insertString += ")"

        #print(tableString)
        #print(insertString)
        self.myDBcursor.execute(tableString)
        self.myDBcursor.execute(insertString)
        self.myDB.commit()
        self.closeBuilder()

class DbBuilder:
    def __init__(self,parent,database):
        self.myParent = parent
        self.myParent.title("Database Builder")
        self.myDB = database
        self.myDBcursor = self.myDB.cursor()

        self.characterBuilder = None
        self.raceBuilder = None
        self.geographyBuilder = None
        self.itemBuilder = None

        self.dbViewer = None

        self.articleContainer = tk.Frame(self.myParent)
        self.articleContainer.grid(row=0)

        self.buttonContainer = tk.Frame(self.myParent)
        self.buttonContainer.grid(row=1)

        buttons = {"Character":self.openCharacterBuilder,"Race":self.openRaceBuilder,"Geography":self.openGeographyBuilder,
                "Item":self.openItemBuilder}
        self.buttons = {}
        row = 0
        column = 0
        numCols = 5
        for key in sorted(buttons.keys()):
            if column == numCols:
                column = 0
                row += 1
            self.buttons[key] = tk.Button(self.articleContainer, command=buttons[key])
            self.buttons[key].configure(text=key)
            self.buttons[key].grid(row=row,column=column)
            column += 1

        #for button,command in buttons.items():
        #    if column == numCols:
        #        column = 0
        #        row += 1
        #    self.buttons[button] = tk.Button(self.articleContainer, command=command)
        #    self.buttons[button].configure(text=button)
        #    self.buttons[button].grid(row=row,column=column)
        #    column += 1

        self.viewerButton = tk.Button(self.buttonContainer, command=self.openViewer)
        self.viewerButton.configure(text="Viewer")
        self.viewerButton.grid(row=0,column=0)

        self.closeButton = tk.Button(self.buttonContainer, command=self.closeBuilder)
        self.closeButton.configure(text="Close")
        self.closeButton.grid(row=0,column=1)

    def openCharacterBuilder(self):
        formDict = {"Name":"Entry","Description":"Text"
                ,"Gender":"Entry","Race":"Entry","Age":"Entry"
                ,"Skin Color":"Entry","Hair Color":"Entry","Eye Color":"Entry"
                ,"Aspects":"Text","Skills":"Text","Stunts":"Text"}
        if self.characterBuilder==None or self.characterBuilder.cleared:
            self.characterBuilder = ArticleBuilder(self.myDB,"Character",formDict)

    def openRaceBuilder(self):
        formDict = {"Name":"Entry","Appearance":"Text","Culture":"Text","Location":"Text"}
        if self.raceBuilder==None or self.raceBuilder.cleared:
            self.raceBuilder = ArticleBuilder(self.myDB,"Race",formDict)

    def openGeographyBuilder(self):
        formDict = {"Name":"Entry","Description":"Text","Location":"Entry"}
        if self.geographyBuilder==None or self.geographyBuilder.cleared:
            self.geographyBuilder = ArticleBuilder(self.myDB,"Geography",formDict)

    def openItemBuilder(self):
        formDict = {"Name":"Entry","Description":"Text","Aspects":"Text"}
        if self.itemBuilder==None or self.itemBuilder.cleared:
            self.itemBuilder = ArticleBuilder(self.myDB,"Item",formDict)

    def openViewer(self):
        self.dbViewer = DbViewer(self.myDB)

    def closeBuilder(self):
        #print("Close Database Builder")
        self.myDB.close()
        self.myParent.destroy()

root = tk.Tk()
database = sql.connect("deorum.db")
dbBuilder = DbBuilder(root,database)
root.mainloop()
