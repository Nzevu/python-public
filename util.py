from io import StringIO
     

class Class:
    def __init__(self, name, indentLevel=0):
        self.name=name
        self.indentLevel=indentLevel
        self.constructors=[]
        self.functions=[]
        self.stmts=[]

    def setIndentLevel(self, indentLevel):
        self.indentLevel=indentLevel

    def addConstructor(self, constructor):
        self.constructors.append(constructor)
    

    def addFunction(self, function):
        self.functions.append(function)


    def addStmt(self, stmt):
        self.stmts.append(stmt)


    def getDeclaration(self):
        buffer=StringIO("")
        buffer.write("\n");
        for i in range(self.indentLevel):
            buffer.write("\t")
        buffer.write("class " + self.name)
        buffer.write(":\n")

        for constructor in self.constructors:
            buffer.write(constructor.getDeclaration())
            
        for function in self.functions:
            buffer.write(function.getDeclaration())

        for stmt in self.stmts:
            buffer.write(stmt.getDeclaration())

        return buffer.getvalue()
    


class Constructor:
    def __init__(self, indentLevel=1):
        
        self.indentLevel=indentLevel
        self.args=[]
        self.stmts=[]

    def setIndentLevel(self, indentLevel):
        self.indentLevel=indentLevel
            
    def addStmt(self, stmt):
        self.stmts.append(stmt)

    def addArg(self, arg):
        self.args.append(arg)
            
    def getDeclaration(self):
        buffer=StringIO("")
        buffer.write("\n");
        for ii in range(self.indentLevel):
            buffer.write("\t")
        buffer.write("def __init__")
        
        slen=len(self.args)
        if slen <= 0:
            buffer.write("(self):")
        else:
            buffer.write("(self, ")
            for i in range(slen):
                if i>=slen-1:
                    buffer.write(self.args[i] + "):")
                else:
                    buffer.write(self.args[i] + ", ")
        buffer.write("\n")

        for stmt in self.stmts:
            buffer.write("\n")
            for j in range(stmt.indentLevel):
                buffer.write("\t")
            buffer.write(stmt.content)
        
        return buffer.getvalue()



class Function:
    def __init__(self, name, indentLevel=1):
        self.name=name
        self.indentLevel=indentLevel
        self.args=[]
        self.stmts=[]

    def setIndentLevel(self, indentLevel):
        self.indentLevel=indentLevel
            
    def addStmt(self, stmt):
        self.stmts.append(stmt)

    def addArg(self, arg):
        self.args.append(arg)
            
    def getDeclaration(self):
        buffer=StringIO("")
        buffer.write("\n");
        for ii in range(self.indentLevel):
            buffer.write("\t")
        buffer.write("def " + self.name)
        
        slen=len(self.args)
        if slen <= 0:
            buffer.write("(self):")
        else:
            buffer.write("(self, ")
            for i in range(slen):
                if i>=slen-1:
                    buffer.write(self.args[i] + "):")
                else:
                    buffer.write(self.args[i] + ", ")
        buffer.write("\n")

        for stmt in self.stmts:
            buffer.write("\n")
            for j in range(stmt.indentLevel):
                buffer.write("\t")
            buffer.write(stmt.content)
        
        return buffer.getvalue()


class Stmt:
    
    def __init__(self, content, indentLevel=0):
        self.indentLevel=indentLevel
        self.content=content

    def setIndentLevel(self, indentLevel):
        self.indentLevel=indentLevel
    def setContent(self, content):
        self.content=content

    def getDeclaration(self):
        buffer=StringIO("")
        buffer.write("\n");
        ii=0
        while ii < self.indentLevel:
            buffer.write("\t")
            ii=ii+1
        buffer.write(self.content)

        return buffer.getvalue()
    
