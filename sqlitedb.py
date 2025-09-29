#class for database access and automatic screen generation
#
import sqlite3
from io import StringIO
import array
import numpy as np
from tkinter import *
from tkinter import messagebox


class SqliteDb:
    def __init__(self):
        self.name="c:/Users/archangelb/Documents/Projects/python/tut/new1.db"
        self.tables=[] #np.array([], dtype=Table)
        self.connection=None
        self.cursor=None
        self.connected=False

    def close(self):
        if(self.connection != None):
            self.connection.close()
            self.connection=None
            self.connected= False

    def getConnection(self):
        if self.connection == None:
            self.connect()
        return self.connection

    def connectTo(self, name):
        self.name=name
        return self.connect()

    def connect(self):
        # Step 1: Connect to SQLite Database (or create it if it doesn't exist)
        try:
            self.connection = sqlite3.connect(self.name)  # Creates db if it doesn't exist
            self.connected=True
            #messagebox.showinfo("Connection established", "Database connected successfully.")
            return self.connection
        except sqlite3.Error as e:
            messagebox.showerror("Db connection error",f"Error connecting to database: {e}")
            return self.connection

    def getCursor(self):
        if self.connection == None:
            self.connect()
        try:
            # Step 2: Create a Cursor Object
            self.cursor = self.connection.cursor()
            return self.cursor
        except sqlite3.Error as e:
            messagebox.showerrorr("Db cursor error",f"Unable to obtain cursor: {e}")
            #self.connection.close()
            return self.cursor

    def insert(self, sql, args):
        try:
            # update cursor
            self.getCursor()
            # Insert data in the database table
            self.cursor.execute(sql, args)
            self.connection.commit()  # Save changes to the database
            messagebox.showinfo("Info saved","Data inserted")
            #self.connection.close()

        except sqlite3.Error as e:
            messagebox.showerror("Db insert error", f"Unable to insert data: {e}")
            #self.connection.close()
            return

    def fetchOne(self):
        try:
            return self.cursor.fetchone()
        except Exception as e:
            messagebox.showerror("Db fetchone error", f"Unable to fetch data: {e}")
            return None
        
    def fetchAll(self):
        try:
            return self.cursor.fetchAll()
        except Exception as e:
            messagebox.showerror("Db fetchall error", f"Unable to fetch data: {e}")
            return None
        
    def extractFrom(self, name):
        self.name=name
        self.extractAll()

    def extractAll(self):

        self.connect()
        cursor=self.getCursor()
        
        try:
            cursor.execute("SELECT tbl_name FROM sqlite_master WHERE tbl_name<>'sqlite_sequence'")
            rows=cursor.fetchall()
            rcount = len(rows)
            i=0
            #for i in range(rcount):
            while i<rcount:
                #print("rows[i]: ", rows[i])
                #print("table name: ", rows[i][0])
                args=[rows[i][0]]
                table=Table(rows[i][0])
                cursor.execute("SELECT sql FROM sqlite_master WHERE tbl_name=?", [rows[i][0]])
                cinfo=cursor.fetchall()
                columns_info =cinfo[0][0]
                #print("columns_info: ", columns_info)
                columns_info=columns_info.strip('\n')
                #print("columns_info: ", columns_info)
                columns=columns_info.split('(')[1].split(')')[0].strip('\n').split(',')
                #print(columns)
                for jj in range(len(columns)):
                    columns[jj]=columns[jj].strip('\n').strip().lstrip().rstrip()
                ccount=len(columns)
                for j in range(ccount):
                    ctemp=columns[j].split(' ')
                    #print(ctemp)
                    col=Column(ctemp[0], ctemp[1])
            
                    tlen=len(ctemp)
                    for k in range(tlen):
                        tempStr=ctemp[k]
                        if tempStr=="PRIMARY":
                            col.setPrimaryKey(True)
                        if tempStr=="AUTOINCREMENT":
                            col.setAutoIncrement(True)
                        if tempStr.__contains__("NULL") and k>0 and ctemp[k-1].startswith("NOT"):
                            col.setNotNull(True)
                    table.addColumn(col)

                query="SELECT * FROM "+ table.name
                cursor.execute(query)
                dataRows=cursor.fetchall()
                table.rows=[ii for ii in range(len(dataRows))]
                for r in range(len(dataRows)):
                    dataRow=dataRows[r]
                    for c in range(len(dataRow)):
                        table.addColumnValue(c, dataRow[c])
                i=i+1
                table.db=self
                self.tables.append(table)
            self.close()
        except Exception as e:
            print('Sql query error: ', e)

    def print(self):
        print("db: ", self.name)
        for table in self.tables:
            table.print()

    def generateInsertScreens(self):
        for table in self.tables:
            table.generateInsertScreen()

    def generateUpdateScreens(self):
        for table in self.tables:
            table.generateUpdateScreen()

    def generateScreens(self):
        self.generateInsertScreens()
        self.generateUpdateScreens()


class Table:

    def __init__(self, name):
        self.name=name
        self.columns=[]
        #self.rows=array.array('i')
        self.rows=np.array([], dtype=int)
        self.db=None

        #screen dimensions
        self.width=640
        self.height=480

    def deleteColumn(self, c):
        self.columns.remove(self.columns[c])
    
    def deleteRow(self, r):
        if(r<len(self.rows) and r>=0):
           self.rows.remove(self.rows[r])
           for col in self.columns:
               col.deleteValue(r)
    

    def addColumn(self, col):
        self.columns.append(col)

    def addRow(self, row):
        self.rows.append(int(row))

    def setColumnValue(self, r, c, value):
        if(r<len(self.rows) and r >=0 and c < len(self.columns) and c>=0):
            self.columns[c].setValue(r, value)

    def setValue(self, r, c, value):
        if(r<len(self.rows) and r >=0 and c < len(self.columns) and c>=0):
            self.columns[c].setValue(r, value)

    def addColumnValue(self, c, value):
        self.columns[c].addValue(value)

    def getValue(self, r, c):
        result = None
        if(r<len(self.rows) and r >=0 and c < len(self.columns) and c>=0):
            #result = self.columns[c].values[r]
            result = self.columns[c].getValue(r)
        else:
            print("getValue index out of range: ", r, c)
        return result
    
    
    def print(self):
        buffer = StringIO()
        buffer.write("Table: ")
        buffer.write(self.name)
        buffer.write("\nColumn details:\n")
        print(buffer.getvalue())
        for col in self.columns:
            col.print()
            #print("\n")
        print("Values:")
        #self.printColumnValues()
        self.printValues()
        

    def printValues(self):
        buffer=StringIO("")
        for r in range(len(self.rows)):
            for c in range(len(self.columns)):
                #print("")
                buffer.write(str(self.getValue(r, c)))
                buffer.write("\t\t")
            buffer.write("\n")
        print(buffer.getvalue())

    def printColumnValues(self):
        for c in range(len(self.columns)):
            self.columns[c].printValues()

    def getColumnUpdateDeclarations(self, parent):
        buffer=StringIO("")
        for col in self.columns:
            #if col.isAutoIncrement == False:
            buffer.write(col.getTKLabelDeclaration(parent))
            if col.type=="TEXT":
                buffer.write(col.getTKTextDeclaration(parent, str(50), str(3)))
            else:
                buffer.write(col.getTKEntryDeclaration(parent, str(25)))

        return buffer.getvalue()

    def getColumnDeclarations(self, parent):
        buffer=StringIO("")
        for col in self.columns:
            if col.isAutoIncrement == False:
                buffer.write(col.getTKLabelDeclaration(parent))
                if col.type=="TEXT":
                    buffer.write(col.getTKTextDeclaration(parent, str(50), str(3)))
                else:
                    buffer.write(col.getTKEntryDeclaration(parent, str(25)))

        return buffer.getvalue()

    def getClickCommands(self):
        buffer=StringIO("")

        return buffer.getvalue()


    def getButton(self):
        buffer=StringIO("")

        return buffer.getvalue()

    def getWritableColumns(self):
        writableCols=[]
        for col in self.columns:
            if col.isAutoIncrement == False:
                writableCols.append(col)

        return writableCols

    def generateUpdateRecordFunction(self):
        buffer=StringIO("")
        buffer.write("def updateRecord(sql, args):\n")
        buffer.write("\t# Step 1: Connect to SQLite Database (or create it if it doesn't exist)\n")
        buffer.write("\ttry:\n")
        buffer.write("\t\tconnection = sqlite3.connect(\"c:/Users/archangelb/Documents/Projects/python/tut/new1.db\")  # Creates 'new1.db' if it doesn't exist\n")
        buffer.write("#\t\tmessagebox.showinfo(\"Connection established\", \"Database connected successfully.\")\n")
        buffer.write("\texcept sqlite3.Error as e:\n")
        buffer.write("\t\tmessagebox.showerror(\"Db connection error\",f\"Error connecting to database: {e}\")\n")
        buffer.write("\t\treturn\n")
        buffer.write("\ttry:\n")
        buffer.write("\t\t# Step 2: Create a Cursor Object\n")
        buffer.write("\t\tcursor = connection.cursor()\n")
        buffer.write("\texcept sqlite3.Error as e:\n")
        buffer.write("\t\tmessagebox.showerrorr(\"Db cursor error\",f\"Unable to obtain cursor: {e}\")\n")
        buffer.write("\t\tconnection.close()\n")
        buffer.write("\t\treturn\n")
        buffer.write("\ttry:\n")
        buffer.write("\t\t# Update data in the database table\n")
        buffer.write("\t\t#messagebox.showinfo(\"sql\", sql)\n")
        buffer.write("\t\t#messagebox.showinfo(\"args[0]\", args[0])\n")
        buffer.write("\t\tcursor.execute(sql, args)\n")
        buffer.write("\t\tconnection.commit()  # Save changes to the database\n")
        buffer.write("\t\tmessagebox.showinfo(\"Info saved\",\"Record updated in the database\")\n")
        buffer.write("\t\tmessagebox.showinfo(\"total changes\", \"# of rows affected: \" + str(connection.total_changes))\n")
        buffer.write("#\t\tsql2=\"SELECT last_insert_rowid() AS id;\"\n")
        buffer.write("#\t\tcursor.execute(sql2)\n")
        buffer.write("\t\tresult=connection.total_changes\n")
        buffer.write("\t\tconnection.close()\n")
        buffer.write("\t\treturn result\n")
        buffer.write("\texcept sqlite3.Error as e:\n")
        buffer.write("\t\tmessagebox.showerror(\"Db update error\", f\"Unable to update data: {e}\")\n")
        buffer.write("\t\tconnection.close()\n")
        buffer.write("\t\treturn None\n")

        return buffer.getvalue()

    def generateUpdateBottomClickCommands(self):
        cols=self.getWritableColumns()
        buffer=StringIO("")
        buffer.write("def saveButtonClick():\n")
        
        buffer.write("\tkv={}\n")
        buffer.write("\tupdateStmt='UPDATE " + self.name + " SET '\n")
        #buffer.write("\tcols='('\n")
        #buffer.write("\tvalues=\n")

        clen=len(cols)
        for i in range(clen):
            if cols[i].type=="TEXT":
                buffer.write("\t" + cols[i].name + "=" + cols[i].name +"Text.get(\"1.0\", \"end-1c\")\n")
            else:
                buffer.write("\t" + cols[i].name + "=" + cols[i].name +"Entry.get()\n")
            buffer.write("#\tif " + cols[i].name +" != None:\n")
            buffer.write("\tif len(" + cols[i].name +") > 0:\n")
            buffer.write("\t\tkv['" + cols[i].name +"']=" + cols[i].name + "\n")
            if i >= clen-1:
                buffer.write("\t\tupdateStmt=updateStmt+' " + cols[i].name + "=?'\n")
                #buffer.write("\t\tvalues=values+'?'\n")
            else:
                buffer.write("\t\tupdateStmt=updateStmt+' " + cols[i].name +"=?, '\n")
                #buffer.write("\t\tvalues=values+'?, '\n")
        buffer.write("\tupdateStmt=updateStmt.rstrip()\n")
        buffer.write("\tif updateStmt[len(updateStmt)-1] ==',':\n")
        buffer.write("\t\tupdateStmt=updateStmt[:-1]\n")
        buffer.write("\tupdateStmt=updateStmt + \" WHERE id=?\"\n")
        buffer.write("\tmessagebox.showinfo('updateStmt', updateStmt)\n")
        buffer.write("\targs=[]\n")
        buffer.write("\tfor value in kv.values(): args.append(value)\n")
        buffer.write("\targs.append(idEntry.get())\n")
        buffer.write("\t#for arg in args: messagebox.showinfo('args', arg)\n")
        buffer.write("\t#if len(args) > 0: cursor.execute(updateStmt, args)\n")
        buffer.write("\tif len(args) > 0:\n")
        buffer.write("\t\tresult=updateRecord(updateStmt, args)\n")
        buffer.write("\t\tif result != None:\n")
        buffer.write("\t\t\tmessagebox.showinfo(\"rows affected\", str(result))\n")
        buffer.write("\t\telse:\n")
        buffer.write("\t\t\tmessagebox.showinfo(\"result\", \"Nothing returned!\")\n")
        buffer.write("\n")
        buffer.write("def cancelButtonClick():\n")
        buffer.write("\tmessagebox.showinfo('Not yet implemented', 'Coming soon')\n")
        buffer.write("\n")

        return buffer.getvalue()
    

    def generateInsertRecordFunction(self):
        buffer=StringIO("")
        buffer.write("def insertRecord(sql, args):\n")
        buffer.write("\t# Step 1: Connect to SQLite Database (or create it if it doesn't exist)\n")
        buffer.write("\ttry:\n")
        buffer.write("\t\tconnection = sqlite3.connect(\"c:/Users/archangelb/Documents/Projects/python/tut/new1.db\")  # Creates 'new1.db' if it doesn't exist\n")
        buffer.write("#\t\tmessagebox.showinfo(\"Connection established\", \"Database connected successfully.\")\n")
        buffer.write("\texcept sqlite3.Error as e:\n")
        buffer.write("\t\tmessagebox.showerror(\"Db connection error\",f\"Error connecting to database: {e}\")\n")
        buffer.write("\t\treturn\n")
        buffer.write("\ttry:\n")
        buffer.write("\t\t# Step 2: Create a Cursor Object\n")
        buffer.write("\t\tcursor = connection.cursor()\n")
        buffer.write("\texcept sqlite3.Error as e:\n")
        buffer.write("\t\tmessagebox.showerrorr(\"Db cursor error\",f\"Unable to obtain cursor: {e}\")\n")
        buffer.write("\t\tconnection.close()\n")
        buffer.write("\t\treturn\n")
        buffer.write("\ttry:\n")
        buffer.write("\t\t# Insert data in the database table\n")
        buffer.write("\t\t#messagebox.showinfo(\"sql\", sql)\n")
        buffer.write("\t\t#messagebox.showinfo(\"args[0]\", args[0])\n")
        buffer.write("\t\tcursor.execute(sql, args)\n")
        buffer.write("\t\tconnection.commit()  # Save changes to the database\n")
        buffer.write("\t\tmessagebox.showinfo(\"Info saved\",\"New record added to database\")\n")
        buffer.write("\t\tmessagebox.showinfo(\"total changes\", \"# of rows affected: \" + str(connection.total_changes))\n")
        buffer.write("\t\tsql2=\"SELECT last_insert_rowid() AS id;\"\n")
        buffer.write("\t\tcursor.execute(sql2)\n")
        buffer.write("\t\tresult=cursor.fetchall()\n")
        buffer.write("\t\tconnection.close()\n")
        buffer.write("\t\treturn result\n")
        buffer.write("\texcept sqlite3.Error as e:\n")
        buffer.write("\t\tmessagebox.showerror(\"Db insert error\", f\"Unable to insert data: {e}\")\n")
        buffer.write("\t\tconnection.close()\n")
        buffer.write("\t\treturn None\n")

        return buffer.getvalue()
    
    def generateBottomClickCommands(self):
        cols=self.getWritableColumns()
        buffer=StringIO("")
        buffer.write("def saveButtonClick():\n")
        
        buffer.write("\tkv={}\n")
        buffer.write("\tinsertStmt='INSERT INTO " + self.name + " '\n")
        buffer.write("\tcols='('\n")
        buffer.write("\tvalues=' VALUES('\n")

        clen=len(cols)
        for i in range(clen):
            if cols[i].type=="TEXT":
                buffer.write("\t" + cols[i].name + "=" + cols[i].name +"Text.get(\"1.0\", \"end-1c\")\n")
            else:
                buffer.write("\t" + cols[i].name + "=" + cols[i].name +"Entry.get()\n")
            buffer.write("#\tif " + cols[i].name +" != None:\n")
            buffer.write("\tif len(" + cols[i].name +") > 0:\n")
            buffer.write("\t\tkv['" + cols[i].name +"']=" + cols[i].name + "\n")
            if i >= clen-1:
                buffer.write("\t\tcols=cols+'" + cols[i].name + "'\n")
                buffer.write("\t\tvalues=values+'?'\n")
            else:
                buffer.write("\t\tcols=cols+'" + cols[i].name +", '\n")
                buffer.write("\t\tvalues=values+'?, '\n")
        buffer.write("\tcols=cols.rstrip()\n")
        buffer.write("\tif cols[len(cols)-1] ==',':\n")
        buffer.write("\t\tcols=cols[:-1]\n")
        buffer.write("\tcols=cols+')'\n")
        buffer.write("\tvalues=values.rstrip()\n")
        buffer.write("\tif values[len(values)-1] ==',':\n")
        buffer.write("\t\tvalues=values[:-1]\n")
        buffer.write("\tvalues=values+')'\n")
        buffer.write("\tinsertStmt=insertStmt+cols+values\n")
        buffer.write("\t#messagebox.showinfo('Not yet implemented', insertStmt)\n")
        buffer.write("\targs=[]\n")
        buffer.write("\tfor value in kv.values(): args.append(value)\n")
        buffer.write("\t#for arg in args: messagebox.showinfo('args', arg)\n")
        buffer.write("\t#if len(args) > 0: cursor.execute(insertStmt, args)\n")
        buffer.write("\tif len(args) > 0:\n")
        buffer.write("\t\tresult=insertRecord(insertStmt, args)\n")
        buffer.write("\t\tif result != None:\n")
        buffer.write("\t\t\tmessagebox.showinfo(\"last row id\", result[0][0])\n")
        buffer.write("\t\telse:\n")
        buffer.write("\t\t\tmessagebox.showinfo(\"result\", \"Nothing returned!\")\n")
        buffer.write("\n")
        buffer.write("def cancelButtonClick():\n")
        buffer.write("\tmessagebox.showinfo('Not yet implemented', 'Coming soon')\n")
        buffer.write("\n")

        return buffer.getvalue()

    def addBottomButtons(self):
        buffer=StringIO("")
        buffer.write("bottomFrame=tk.Frame(window, pady=20)\n")
        buffer.write("bottomFrame.grid()\n")
        buffer.write("saveButton=tk.Button(bottomFrame, text='Save', command=saveButtonClick)\n")
        buffer.write("saveButton.grid(column=0,  row=1)\n")
        buffer.write("cancelButton=tk.Button(bottomFrame, text='Cancel', command=cancelButtonClick)\n")
        buffer.write("cancelButton.grid(column=2, row=1)\n")

        return buffer.getvalue()

    def generateInsertScreen(self, width=640, height=480):
        self.width=width
        self.height=height
        buffer=StringIO("")
        buffer.write("import tkinter as tk\n")
        buffer.write("from tkinter import *\n")
        buffer.write("from tkinter import messagebox\n")
        #buffer.write("\n")
        buffer.write("from tkinter import Scrollbar\n")
        #buffer.write("\n")
        buffer.write("import sqlite3\n")
        
        buffer.write("\n")
        buffer.write("window=tk.Tk()\n")
        buffer.write("window.title('Insert " + self.name + "')\n")
        buffer.write("window.geometry('" + str(self.width) + "x" + str(self.height) + "')\n")
        buffer.write("\n")
        buffer.write(self.getColumnDeclarations("window"))
        buffer.write("\n")
        buffer.write(self.generateInsertRecordFunction())
        buffer.write("\n");
        buffer.write(self.generateBottomClickCommands());
        
        buffer.write("\n")
        buffer.write(self.addBottomButtons())
        buffer.write("\n")
        buffer.write("window.mainloop()\n")

        with open(self.name+"entry.py", "w") as file:
            file.write(buffer.getvalue())
        return buffer.getvalue()


    def generateUpdateScreen(self, width=640, height=480):
        self.width=width
        self.height=height
        buffer=StringIO("")
        buffer.write("import tkinter as tk\n")
        buffer.write("from tkinter import *\n")
        buffer.write("from tkinter import messagebox\n")
        #buffer.write("\n")
        buffer.write("from tkinter import Scrollbar\n")
        #buffer.write("\n")
        buffer.write("import sqlite3\n")
        
        buffer.write("\n")
        buffer.write("window=tk.Tk()\n")
        buffer.write("window.title('Update " + self.name + "')\n")
        buffer.write("window.geometry('" + str(self.width) + "x" + str(self.height) + "')\n")
        buffer.write("\n")
        buffer.write(self.getColumnUpdateDeclarations("window"))
        buffer.write("\n")
        buffer.write(self.generateUpdateRecordFunction())
        buffer.write("\n");
        buffer.write(self.generateUpdateBottomClickCommands());
        
        buffer.write("\n")
        buffer.write(self.addBottomButtons())
        buffer.write("\n")
        buffer.write("window.mainloop()\n")

        with open(self.name+"update.py", "w") as file:
            file.write(buffer.getvalue())
        return buffer.getvalue()

    
class Column:
    def __init__(self):
        self.name=""
        self.type=""
        self.isPrimaryKey=False
        self.isAutoIncrement=False
        self.isNotNull=False
        self.values=[]
        self.histogram={}

    def __init__(self, name, type):
        self.name=name
        self.type=type
        self.isPrimaryKey=False
        self.isAutoIncrement=False
        self.isNotNull=False
        self.values=[]
        self.histogram={}

    def getTKLabelDeclaration(self, parent):
        buffer=StringIO("")
        buffer.write(self.name + "Label=tk.Label("+ parent + ", text=\"" +self.name+"\")\n")
        buffer.write(self.name+ "Label.grid(sticky=(W))\n")
        #buffer.write("\n")
        
        return buffer.getvalue()

    def getTKEntryDeclaration(self, parent, width):
        buffer=StringIO("")
        buffer.write(self.name + "=StringVar()\n")
        buffer.write(self.name + "Entry=tk.Entry("+ parent + ", width=" +width+")\n")
        buffer.write(self.name + "Entry.textvariable=" + self.name + "\n")
        buffer.write(self.name+ "Entry.grid()\n")
        #buffer.write("\n")
        
        return buffer.getvalue()

    def getTKTextDeclaration(self, parent, width, height):
        buffer=StringIO("")
        buffer.write(self.name + "=StringVar()\n")
        buffer.write(self.name + "Text=tk.Text("+ parent + ", width=" +width+", height="+ height +")\n")
        buffer.write(self.name + "Text.textvariable=" + self.name + "\n")
        buffer.write(self.name+ "Text.grid()\n")
        #buffer.write("\n")
        
        return buffer.getvalue()
    
    def setName(self, name):
        self.name=name

    def setType(self, type):
        self.name=type

    def setPrimaryKey(self, isPK):
        self.isPrimaryKey=isPK

    def setAutoIncrement(self, isAutoIncr):
        self.isAutoIncrement=isAutoIncr

    def setNotNull(self, isNotNull):
        self.isNotNull=isNotNull

    def addValue(self, value):
        self.values.append(value)

    def setValue(self, i, value):
        self.values[i]=value

    def getValue(self, i):
        result = None
        if(i<len(self.values) and i >=0):
            result = self.values[i]
        else:
            print("Column.getValue index out of range: ", i, len(self.values))
        return result
    def deleteValue(self, r):
        if(r<len(self.values) and r>=0):
           self.values.remove(self.values[r])

    def print(self):
        buffer=StringIO("")
        buffer.write("Name: ")
        buffer.write(self.name)
        buffer.write("\nType: ")
        buffer.write(self.type)
        buffer.write("\nAutoIncrement: ")
        if self.isAutoIncrement== True: 
            buffer.write("True")
        else:
            buffer.write("False")
        buffer.write("\nNot Null: ")
        if self.isNotNull == True:
            buffer.write("True")
        else:
            buffer.write("False")

        buffer.write("\n")
        print(buffer.getvalue())

    def printValues(self):
        for value in self.values:
            print(value)

    def toString(self):
        buffer=StringIO("")
        buffer.write("Name: ")
        buffer.write(self.name)
        buffer.write("\nType: ")
        buffer.write(self.type)
        buffer.write("\nAutoIncrement: ")
        if self.isAutoIncrement== True: 
            buffer.write("True")
        else:
            buffer.write("False")
            buffer.write("\nNot Null: ")
        if self.isNotNull == True:
            buffer.write("True")
        else:
            buffer.write("False")

        return buffer

    def buildHistogram(self):
        self.histogram={}
        for key in self.values:
            value=self.histogram.get(key)
            if value is None:
                self.histogram[key]=1
            else:
                self.histogram[key]=value+1
        print("histogram: ", self.histogram)
        #retutn self.histogram

    def getHistoFrequencies(self):
        tcount=len(self.values)
        histofrequencies={}
        for key in self.histogram.keys():
            histofrequencies[key]=self.histogram.get(key)/tcount
        #print(histofrequencies)

        return histofrequencies






#Sample driver program


#from sqlitedb import SqliteDb
#from sqlitedb import Table
#from sqlitedb import Column

#from util import *


#db1=SqliteDb()
#db1.extractAll("new1.db")
#db1.print()
#db1.generateInsertScreens()
#print("All done!")

