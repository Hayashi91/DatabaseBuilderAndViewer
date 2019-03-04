#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
import tkinter as tk
import sqlite3 as sql
from enum import Enum

class Form(Enum):
    entry = 1
    text = 2
    image = 3

class Article:
    def __init__(self,name,forms):
        self.name = name
        self.forms = forms

class DbViewer:
    def __init__(self,db,articles):
        self.cleared = False
        self.myParent = tk.Tk()
        self.myParent.title("Database Viewer")
        self.myDB = db
        self.myDBcursor = self.myDB.cursor()
        self.articles = articles

        self.searchResults = []

        self.searchContainer = tk.Frame(self.myParent)
        self.searchContainer.grid(row=0,column=0)

        tk.Label(self.searchContainer,text="Search:").grid(row=0,column=0)
        self.searchBar = tk.Entry(self.searchContainer,width=60,font=("Times",14))
        self.searchBar.bind("<KeyRelease>",self.searchUpdate)
        self.searchBar.grid(row=0,column=1)

        self.resultsContainer = tk.Frame(self.myParent)
        self.resultsContainer.grid(row=1,column=0)

        self.bookmarkContainer = tk.Frame(self.myParent)
        self.bookmarkContainer.grid(row=2,column=0)

        self.bookmarks = {}

        self.formCanvas = tk.Canvas(self.myParent,width=580,height=0)
        self.formCanvas.config(highlightthickness=0)
        #self.formCanvas.grid(row=3,column=0)

        self.formContainer = tk.Frame(self.formCanvas)
        #self.formContainer.grid(row=3,column=0)

        self.formScrollbar = tk.Scrollbar(self.myParent,command=self.formCanvas.yview)
        #self.formScrollbar.grid(row=3,column=1,sticky=tk.NS)

        self.formCanvas.config(yscrollcommand=self.formScrollbar.set)
        self.formCanvas.create_window(0,0,window=self.formContainer,anchor="nw")

        self.formContainer.bind("<Configure>",self.fixScrollRegion)

        self.labels = {}
        self.entries = {}

        self.buttonContainer = tk.Frame(self.myParent)
        self.buttonContainer.grid(row=4,column=0)

        self.editButton = tk.Button(self.buttonContainer,text="Edit",command=self.editSearchResult)
        self.editButton.grid(row=0,column=0)

        self.bookmarkButton = tk.Button(self.buttonContainer,text="Bookmark",command=self.bookmarkResult)
        self.bookmarkButton.grid(row=0,column=1)

        self.closeButton = tk.Button(self.buttonContainer,text="Close",command=self.closeViewer)
        self.closeButton.grid(row=0,column=2)

    def searchUpdate(self,event):
        for result in self.searchResults:
            result.destroy()
        self.searchResults=[]
        self.formCanvas.grid_forget()
        self.formScrollbar.grid_forget()
        if self.searchBar.get() == "":
            self.resultsContainer.grid_forget()
        else:
            self.resultsContainer.grid(row=1,column=0)
            value = ('%'+self.searchBar.get()+'%',)
            self.myDBcursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.myDBcursor.fetchall()
            results = []
            for table in tables:
                searchString = "SELECT rowid, name FROM " + table[0] + " WHERE name LIKE '" + value[0] + "'"
                tmp = self.myDBcursor.execute(searchString)
                for row in tmp:
                    results.append([table[0],str(row[0]),row[1]])
            if len(results) == 0:
                self.resultsContainer.grid_forget()
            else:
                i=0
                for result in results:
                    #print(result)
                    self.searchResults.append(tk.Button(self.resultsContainer,
                        text=result[2],command=lambda res=result: self.openSearchResult(res)))
                    self.searchResults[i].grid(row=0,column=i)
                    i += 1
                    if i > 4:
                        break
                self.openSearchResult(results[0])

    def fixScrollRegion(self,event):
        self.formCanvas.config(scrollregion=self.formCanvas.bbox("all"))

    def openSearchResult(self,result):
        #print("Opening Search Result")
        #print(result[0]+"-"+result[1]+" "+result[2])
        #print(self.entries)
        self.formCanvas.grid(row=3,column=0)
        self.formScrollbar.grid(row=3,column=1,sticky=tk.NS)
        for name,label in self.labels.items():
            label.destroy()
        for name,form in self.entries.items():
            form.destroy()
        self.result = result
        self.entries = {}
        self.myDBcursor.execute("SELECT * FROM "+result[0]+" WHERE rowid = ?",result[1])
        info = self.myDBcursor.fetchone()
        article = None
        for art in self.articles:
            if art.name == result[0]:
                article = art
        #print(info)
        #print(article.forms)
        row=0
        for form in article.forms:
            #print(form + " " + str(article.forms[form]) + ": " + info[row])
            self.labels[form] = tk.Label(self.formContainer,text=form+":")
            self.labels[form].grid(row=row,column=0,sticky=tk.NE)
            if article.forms[form]==Form.entry:
                self.entries[form] = tk.Entry(self.formContainer,width=60,font=("Times",14))
                self.entries[form].insert(0,info[row])
                self.entries[form].configure(state=tk.DISABLED,disabledforeground="black")
            if article.forms[form]==Form.text:
                self.entries[form] = tk.Text(self.formContainer,height=5,width=60,font=("Times",14))
                self.entries[form].insert("1.0",info[row])
                self.entries[form].configure(state=tk.DISABLED)
            self.entries[form].configure(borderwidth=1,relief=tk.SUNKEN,highlightcolor="steel blue")
            self.entries[form].grid(row=row,column=1)
            row += 1
        self.formCanvas.config(height=min(400,self.formContainer.winfo_height()))

    def editSearchResult(self):
        for name,entry in self.entries.items():
            entry.configure(state=tk.NORMAL)
        self.editButton.configure(text="Save",command=self.saveEditedResult)

    def saveEditedResult(self):
        insertString = "UPDATE " + self.result[0] + " SET "
        for label,entry in self.entries.items():
            if type(entry)==tk.Entry:
                insertString += "'"+label+"'='"+entry.get().replace("'","''")+"', "
            if type(entry)==tk.Text:
                insertString += "'"+label+"'='"+entry.get(0.0,tk.END).replace("'","''")+"', "
        insertString = insertString[:-2]
        insertString += " WHERE rowid=" + self.result[1]

        #print(insertString)
        self.myDBcursor.execute(insertString)
        self.myDB.commit()

        for name,entry in self.entries.items():
            entry.configure(state=tk.DISABLED)
        self.editButton.configure(text="Edit",command=self.editSearchResult)

    def bookmarkResult(self):
        bookmarkKey = self.result[0]+"-"+self.result[1]
        self.bookmarkContainer.grid(row=2,column=0)
        if bookmarkKey not in self.bookmarks:
            self.bookmarks[bookmarkKey] = tk.Button(self.bookmarkContainer,text=self.result[2],command=lambda res=self.result: self.openSearchResult(res))
            self.bookmarks[bookmarkKey].grid(row=0,column=len(self.bookmarks)-1)
        else:
            self.bookmarks[bookmarkKey].destroy()
            del self.bookmarks[bookmarkKey]
            if len(self.bookmarks) == 0:
                self.bookmarkContainer.grid_forget()
            else:
                col = 0
                for key,bookmark in self.bookmarks.items():
                    bookmark.grid(row=0,column=col)
                    col += 1

    def closeViewer(self):
        #print("Close Database Viewer")
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
    def __init__(self,db,article):
        self.cleared = False
        self.myParent = tk.Tk()
        self.formType = article.name
        self.myParent.title(self.formType+" Builder")
        self.myDB = db
        self.myDBcursor = self.myDB.cursor()

        self.formCanvas = tk.Canvas(self.myParent,width=580,height=400)
        self.formCanvas.config(highlightthickness=0)
        self.formCanvas.grid(row=0,column=0)

        self.formContainer = tk.Frame(self.formCanvas)
        #self.formContainer.grid(row=0,column=0)

        self.formScrollbar = tk.Scrollbar(self.myParent,command=self.formCanvas.yview)
        self.formScrollbar.grid(row=0,column=1,sticky=tk.NS)

        self.formCanvas.config(yscrollcommand=self.formScrollbar.set)
        self.formCanvas.create_window(0,0,window=self.formContainer,anchor="nw")

        self.formContainer.bind("<Configure>",self.fixScrollRegion)

        row=0
        self.entries = {}
        for label,form in article.forms.items():
            tk.Label(self.formContainer,text=label+":").grid(row=row,column=0,sticky=tk.NE)
            if form==Form.entry:
                self.entries[label] = tk.Entry(self.formContainer,width=60,font=("Times",14))
            if form==Form.text:
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

    def fixScrollRegion(self,event):
        self.formCanvas.config(scrollregion=self.formCanvas.bbox("all"))

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
        #print("Saving " + self.formType + " Article")
        tableString = "CREATE TABLE IF NOT EXISTS " + self.formType + "("
        insertString = "INSERT INTO " + self.formType + " VALUES ("
        for label,entry in self.entries.items():
            #print(type(entry))
            tableString += "'"+label + "', "
            if type(entry)==tk.Entry:
                insertString += "'" + entry.get().replace("'","''") + "', "
            if type(entry)==tk.Text:
                insertString += "'" + entry.get(0.0,tk.END).replace("'","''") + "', "
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

        self.articles=[]
        self.articles.append(Article("Character",{"Name":Form.entry,"Description":Form.text,
            "Gender":Form.entry,"Race":Form.entry,"Age":Form.entry,
            "Skin Color":Form.entry,"Hair Color":Form.entry,"Eye Color":Form.entry,
            "Aspects":Form.text,"Skills":Form.text,"Stunts":Form.text}))
        self.articles.append(Article("Race",{"Name":Form.entry,"Description":Form.text,"Appearance":Form.text,
            "Culture":Form.text,"Location":Form.text}))
        self.articles.append(Article("Geography",{"Name":Form.entry,"Description":Form.text,"Location":Form.entry}))
        self.articles.append(Article("Item",{"Name":Form.entry,"Description":Form.text,"Aspects":Form.text}))

        self.builders = {}
        for article in self.articles:
            self.builders[article.name] = None

        self.articleContainer = tk.Frame(self.myParent)
        self.articleContainer.grid(row=0)

        self.buttonContainer = tk.Frame(self.myParent)
        self.buttonContainer.grid(row=1)

        self.buttons = {}
        row = 0
        column = 0
        numCols = 5
        for article in self.articles:
            if column == numCols:
                column = 0
                row += 1
            self.buttons[article.name] = tk.Button(self.articleContainer,
                    command=lambda art=article: self.openBuilder(art))
            self.buttons[article.name].configure(text=article.name)
            self.buttons[article.name].grid(row=row,column=column)
            column += 1

        self.viewerButton = tk.Button(self.buttonContainer, command=self.openViewer)
        self.viewerButton.configure(text="Viewer")
        self.viewerButton.grid(row=0,column=0)

        self.closeButton = tk.Button(self.buttonContainer, command=self.closeBuilder)
        self.closeButton.configure(text="Close")
        self.closeButton.grid(row=0,column=1)

    def openBuilder(self,article):
        if self.builders[article.name] == None or self.builders[article.name].cleared:
            self.builders[article.name] = ArticleBuilder(self.myDB,article)

    def openViewer(self):
        self.dbViewer = DbViewer(self.myDB,self.articles)

    def closeBuilder(self):
        #print("Close Database Builder")
        self.myDB.close()
        self.myParent.destroy()

root = tk.Tk()
database = sql.connect("deorum.db")
dbBuilder = DbBuilder(root,database)
root.mainloop()
