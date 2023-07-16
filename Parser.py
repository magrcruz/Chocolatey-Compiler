from Scanner import *
from utils.Error import *
from utils.FirstAndFollows import *
from utils.Place import Place
from anytree import Node, RenderTree
from anytree.exporter import DotExporter
from anytree.search import findall

DEBUG = False

def render_tree(root: object) -> None:
    print(">> ===== ARBOL ===== <<")
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))
    print("")

def addChildFront(child,parent):
    parent.children = list([child]) + list(parent.children)

class Parser:
    def __init__(self, escaner):
        self.escaner = escaner
        self.error_list = []
        self.abstract_syntax_tree = None
        self.current_token = None
        self.current_error = None
        self.TOKEN_INPUT = []

    #TREE
    def errorNode(self):
        return Node("ERROR")
    def nodeToList(self,root, key):
        output = []
        nodes = findall(root, filter_=lambda node: node.name == key)
        for node in nodes:
            for children in node.children:
                if children.name != key:
                    output.append(children)
        return output
    
    def getToken(self):
        if not DEBUG:
            #Caso especial de ident y dedent
            if self.current_token == "IDENT" or self.current_token == "DEDENT":
                self.current_token.value -=1
                if not self.current_token.value:
                    self.current_token = self.escaner.getToken()
            else: self.current_token = self.escaner.getToken()
        else:
            if len(self.TOKEN_INPUT):
                self.current_token = Token(self.TOKEN_INPUT[0],self.TOKEN_INPUT[0],0,0)
                self.TOKEN_INPUT = self.TOKEN_INPUT[1:]
            else:
                self.current_token = Token("EOF","EOF",0,0)

    #def add_error(self, error):
    #    error.col = self.current_token.col
    #    error.descripcion += ", found %s" % self.current_token.value
    #    self.error_list.append(error)
    def synchronize(self):
        while not(self.current_token == "NEWLINE" or self.current_token == "EOF"):
            print("you here")
            self.getToken()
        print("You out")
        

    def quickError(self, production, expected = None):
        if self.current_error != None: return
        if expected != None:
            self.current_error = Error(production, "%s expected but [ %s ] founded instead"%(expected,self.current_token.value), self.current_token.row, self.current_token.col)
        else:
            self.current_error = Error(production,"Token unexpected %s" %self.current_token.value, self.current_token.row, self.current_token.col)
        print(self.current_error)
        print("Here") 

    def S(self):
        #print("INFO PARSE - Start scanning...")

        self.abstract_syntax_tree = self.Program()
        if self.current_token != "EOF":
            self.quickError("S","EOF")
        
        self.escaner.buffer = []#Vacia el buffer para hacer la sincronizacion
        #Agrega si aun quedase algun error
        if self.current_error:
            self.error_list.append(self.current_error)
            self.current_error = None

        #Errores
        print("INFO SCAN - Completed with %i errors" % (len(self.escaner.errores)))
        for i in self.escaner.errores:
            print("Error:  %s " % i)

        print("INFO PARSE - Completed with %i errors" % (len(self.error_list)))
        for i in self.error_list:
            print("Error:  %s " % i)
        
        if not len(self.escaner.errores) and not len(self.error_list): #Si no hubo errores en el escaner ni en el parser
            render_tree(self.abstract_syntax_tree)
            return True
        
        return False

    def Program(self):
        self.getToken()

        #Program ::= DefList StatementList
        nodo = Node("Program")
        child1 = self.DefList()
        if child1!=None:
            child1.parent = nodo

            #Sincronizar
            if self.current_token not in FOLLOW["DefList"]:
                self.quickError("Deflist")
                while self.current_token not in FOLLOW["DefList"]:
                    self.getToken()
            #Agrega el error si lo hubiera
            if self.current_error:
                nodo = self.errorNode()
                self.error_list.append(self.current_error)
                self.current_error = None          

        child2 = self.StatementList()
        if child2!=None:
            child2.parent = nodo

            #Sincronizar
            if self.current_token not in FOLLOW["StatementList"]:
                self.quickError("StatementList")
                while self.current_token not in FOLLOW["StatementList"]:
                    self.getToken()
            #Agrega el error si lo hubiera
            if self.current_error:
                nodo = self.errorNode()
                self.error_list.append(self.current_error)
                self.current_error = None 

        #Sincronizar
        if self.current_token not in FOLLOW["Program"]:
            self.quickError("Program")
            while self.current_token not in FOLLOW["Program"]:
                self.getToken()
        #Agrega el error si lo hubiera
        if self.current_error:
            nodo = self.errorNode()
            self.error_list.append(self.current_error)
            self.current_error = None
        return nodo

    def DefList(self):
        #DefList ::=  Def DefList
        if self.current_token in FIRST['Def']:
            child1 = self.Def()
            if child1!=None:
                nodo = Node("DefList")
                child1.parent = nodo
                childs = self.DefList()
                if childs != None:
                    for i,c in enumerate(childs.children):
                        c.parent = nodo
                        setattr(c, "order", i+1)
                return nodo
            return child1#
            
        #DefList ::=  ''
        elif self.current_token in FOLLOW["DefList"]:
            return None
        
        self.quickError("DefList","def")
        return self.errorNode()
        
    def Def(self):
        #Def ::=  def ID ( TypedVarList ) Return : NEWLINE Block
        # Verifica hasta los dos puntos
        nodo = self.errorNode()
        if self.current_token == "DEF":
            #nodo = Node("Def")
            self.getToken()
            if self.current_token == "ID":
                #Node(self.current_token.value, parent=nodo)
                nodo = Node(self.current_token.value)
                self.getToken()
                if self.current_token == "LPAREN":
                    self.getToken()
                    child1 = self.TypedVarList()
                    if child1!= None: child1.parent = nodo
                    if self.current_token =="RPAREN":
                        self.getToken()
                        child2 = self.Return()
                        if child2 != None: child2.parent = nodo
                        if self.current_token == "COLON":
                            self.getToken()
                        else: self.quickError("Def",":")
                    else: self.quickError("Def",")")
                else: self.quickError("Def","(")
            else: self.quickError("Def","ID")
        else: self.quickError("Def","def")

        if self.current_token != "NEWLINE":
            self.quickError("Def","NEWLINE")

        self.synchronize()
        if self.current_error:
            nodo = self.errorNode()
            self.error_list.append(self.current_error)
            self.current_error = None

        #Aqui continua leyendo Block
        if self.current_token == "NEWLINE":
            self.getToken()

        child3 = self.Block()
        child3.parent = nodo

        #Sincroniza con los follow
        if self.current_token not in FOLLOW['Def']:
            self.quickError("Def")
            nodo = self.errorNode()
            while self.current_token not in FOLLOW['Def']:
                self.getToken()

        return nodo
    
    def TypedVar(self):
        # TypeVar ::= ID : Type
        if self.current_token=="ID":
            nodo = Node(":")
            Node(self.current_token.value, parent=nodo)
            self.getToken()

            if self.current_token != "COLON":
                self.quickError("TypedVar",":")
            else:
                self.getToken()
                child2 = self.Type()
                child2.parent = nodo

            return nodo

        #No deberia llegar aqui porque solo se llama cuando self.currentToken es ID
        self.quickError("TypedVar","ID")
        return nodo

    def Type(self):
        # Type ::= int
        if self.current_token=="INT" or self.current_token=="STR":
            nodo = Node(self.current_token.value)
            self.getToken()
            return nodo

        # Type ::= [ Type ]
        elif self.current_token == "LBRACKET":
            self.getToken()
            nodo = self.Type()
            if self.current_token != "RBRACKET":
                self.quickError("Type","]")
            else:
                self.getToken()
            nodo.name = "[{}]".format(nodo.name)
            return nodo

        self.quickError("Type","int | str | [")
        return self.errorNode()

    def TypedVarList(self):
        #TypedVarList ::=  TypedVar TypedVarListTail
        if self.current_token in FIRST['TypedVar']: #ID
            nodo = Node("()")
            child1 = self.TypedVar()
            child1.parent = nodo
            setattr(child1, "order", 0)
            nodeTail = self.TypedVarListTail()
            if nodeTail != None:
                childrens = self.nodeToList(nodeTail,"TAIL")
                for i, c in enumerate(childrens):
                    c.parent = nodo
                    setattr(c, "order", i+1)
            return nodo
        
        #TypedVarList ::=  ''
        elif self.current_token in FOLLOW['TypedVarList']:
            return None

        self.quickError("TypedVarList","ID")
        return self.errorNode()

    def TypedVarListTail(self):
        #TypedVarListTail ::=  , TypedVar TypedVarListTail
        if self.current_token == "COMMA":
            nodo = Node("TAIL")
            self.getToken()
            child1 = self.TypedVar()
            child1.parent = nodo
            child2 = self.TypedVarListTail()
            if child2 != None:#Puede ser vacio
                child2.parent = nodo
            return nodo

        #TypedVarListTail ::=  ''
        elif self.current_token in FOLLOW['TypedVarListTail']:
            return None
        
        self.quickError("TypedVarListTail",",")
        return self.errorNode()
    
    def Return(self):
        #Return ::= -> Type
        if self.current_token == "ARROW":
            nodo = Node("->")
            self.getToken()
            child1 = self.Type()
            child1.parent = nodo
            return nodo
        
        elif self.current_token in FOLLOW['Return']:
            return None

        self.quickError("Return","->")
        return self.errorNode()

    def Block(self):
        nodo = Node("DO")
        #Block ::= IDENT Statement StatementList DEDENT

        if self.current_token == "IDENT":
            self.getToken()
            child1 = self.Statement() # Statement ya esta sincronizado
            child1.parent = nodo
            childs = self.StatementList()
            if childs != None:
                for i,c in enumerate(childs.children):
                    c.parent = nodo##
            
            if self.current_token != "DEDENT":
                #Si no hay dedent solo se olvido de ponerlo y como ya esta sincronizado en statement no habria tanto problema
                self.quickError("Block","DEDENT")
                print("Capaz no sincronizo bien el statement")
            else: self.getToken()

        else:
            self.quickError("Block", "IDENT")

        # Sincronizacion de errores
        if self.current_token not in FOLLOW["Block"]:
            self.quickError("Block")
            while self.current_token not in FOLLOW["Block"]:
                self.getToken()

        if self.current_error:#Agrega el error si aun no lo agrego
            nodo = self.errorNode()
            self.error_list.append(self.current_error)
            self.current_error = None

        return nodo

    def StatementList(self): #M
        nodo = None
        #StatementList ::=  Statement StatementList
        if self.current_token in FIRST['Statement']:
            nodo = Node("Statements")
            child1 = self.Statement()
            childs = self.StatementList()
            child1.parent = nodo
            if childs != None:
                for i,c in enumerate(childs.children):
                    c.parent = nodo##

        #StatementList ::=  '' 
        elif self.current_token in FOLLOW['StatementList']:
            nodo = None
        else:
            self.quickError("StatementList")
            nodo = self.errorNode()
            # sincroniza en Program y Block
        return nodo

    def Statement(self): #M
        nodo = None
        #Statement ::=  SimpleStatement NEWLINE
        if self.current_token in FIRST['SimpleStatement']:
            nodo = self.SimpleStatement()

            #En ese se sincroniza avanzando hasta newline
            if self.current_token != "NEWLINE":
                self.quickError("Statement","NEWLINE")

            # Sincronizacion de errores con el NEWLINE
            self.synchronize()
            if self.current_error:
                nodo = self.errorNode()
                self.error_list.append(self.current_error)
                self.current_error = None

            if self.current_token == "NEWLINE":
                self.getToken()
            
        #Statement ::=  if Expr : NEWLINE Block ElifList Else
        elif self.current_token == "IF":
            self.getToken()
            nodo = Node("IF_BLOCK")
            nodoif = Node("IF", parent=nodo)
            child1 = self.Expr()
            child1.parent = nodoif

            if self.current_token != "COLON":
                self.quickError("Statement",":")
            else: self.getToken()

            if self.current_token != "NEWLINE":
                self.quickError("Statement","NEWLINE")

            # Sincronizacion de errores con el NEWLINE
            self.synchronize()
            if self.current_error:
                nodo = self.errorNode()
                self.error_list.append(self.current_error)
                self.current_error = None

            if self.current_token == "NEWLINE":
                self.getToken()

            child2 = self.Block() #Block se sincroniza solito
            child2.parent = nodoif

            child2 = None
            if self.current_token in FIRST["ElifList"]:
                child2 = self.ElifList()
                if child2!=None:
                    for _,c in enumerate(child2.children):
                        c.parent = nodo

            child2 = None
            if self.current_token in FIRST["Else"]:
                child2 = self.Else()
                if child2!=None: child2.parent = nodo

        #Statement ::=  while Expr : NEWLINE Block
        elif self.current_token == "WHILE":
            nodo = Node("WHILE")
            self.getToken()
            child = self.Expr()
            child.parent = nodo
           
            if self.current_token != "COLON":
                self.quickError("Statement",":")
            else: self.getToken()

            if self.current_token != "NEWLINE":
                self.quickError("Statement","NEWLINE")

            # Sincronizacion de errores con el NEWLINE
            self.synchronize()
            if self.current_error:
                nodo = self.errorNode()
                self.error_list.append(self.current_error)
                self.current_error = None

            if self.current_token == "NEWLINE":
                self.getToken()

            child1 = self.Block() # Block se sincroniza solo
            child1.parent = nodo
            
        #Statement ::=  for ID in Expr : NEWLINE Block
        elif self.current_token == "FOR":
            nodo = Node("FOR")
            self.getToken()
            child1 = self.errorNode()
            grandson = self.errorNode()

            if self.current_token != "ID":
                self.quickError("Statement","ID")
            else:
                grandson = Node(self.current_token.value)
                self.getToken()                

            if self.current_token != "IN":
                self.quickError("Statement","in")
            else:
                self.getToken()
                child1 = Node("IN", parent=nodo)
                
            grandson.parent = child1
            #self.getToken()#why
            child2 = self.Expr()
            child2.parent = child1
                    
            if self.current_token != "COLON":
                self.quickError("Statement",":")
            else: self.getToken()

            if self.current_token != "NEWLINE":
                self.quickError("Statement","NEWLINE")

            # Sincronizacion de errores con el NEWLINE
            self.synchronize()
            if self.current_error:
                nodo = self.errorNode()
                self.error_list.append(self.current_error)
                self.current_error = None

            if self.current_token == "NEWLINE":
                self.getToken()

            child2 = self.Block()
            child2.parent = nodo

        else:#Se sincroniza para que no entre en bucle infinito, no puede ser vacio
            #No deberia entrar aqui
            self.quickError("Statement")#check si se puede sincronizar con newline xd
            nodo = self.errorNode()
            while self.current_token not in FOLLOW['Statement']:#Incluye dedent y eof
                self.getToken()

        #Si falto agregar algun error lo guarda
        if self.current_error:
            nodo = self.errorNode()
            self.error_list.append(self.current_error)
            self.current_error = None

        print("Chequea el estado")
        return nodo

    def ElifList(self):
        #ElifList ::= Elif ElifList
        if self.current_token in FIRST['Elif']:
            nodo = Node("ELIFLIST")
            child1 = self.Elif()
            childs = self.ElifList()
            child1.parent = nodo
            if childs != None:
                for i,c in enumerate(childs.children):
                    c.parent = nodo##check
            return nodo

        #ElifList ::= epsilon
        if self.current_token in FOLLOW['ElifList']:
            return None
            
        self.quickError("ElifList")
        return self.errorNode()


    def Elif(self):
        nodo = None
        #Elif ::= elif Expr : NEWLINE Block
        if self.current_token == "ELIF":
            self.getToken()
            child1 = self.Expr()

            if self.current_token != "COLON":
                self.quickError("Elif",":")
            else: self.getToken()

            if self.current_token != "NEWLINE":
                self.quickError("Elif","NEWLINE")

            # Sincronizacion de errores con el NEWLINE
            self.synchronize()
            if self.current_error:
                nodo = self.errorNode()
                self.error_list.append(self.current_error)
                self.current_error = None

            if self.current_token == "NEWLINE":
                self.getToken()
                child2 = self.Block()
                nodo = Node("ELIF")
                child1.parent = nodo
                child2.parent = nodo

        elif self.current_token in FOLLOW['Elif']:
            nodo = None
        else: #Con la modificacion no deberia entrar aqui
            #Cuando no esta vacio pero se intento poner la produccion, se sincroniza en Statement
            self.quickError("Elif","elif")
            nodo = self.errorNode()
        return nodo

    def Else(self): #SYNCHRONIZE
        node = None
        #Else ::=  else : NEWLINE Block
        if self.current_token == "ELSE":
            self.getToken()
            if self.current_token != "COLON":
                self.quickError("Else",":")
            else: self.getToken()

            if self.current_token != "NEWLINE":
                self.quickError("Else","NEWLINE")
                                
            # Sincronizacion de errores con el NEWLINE
            self.synchronize()
            if self.current_error:
                node = self.errorNode()
                self.error_list.append(self.current_error)
                self.current_error = None

            if self.current_token == "NEWLINE":
                self.getToken()
                node = Node("ELSE")
                child1 = self.Block()
                #Ya que no existe una condicion se puede asignar directamente a else
                for _,c in enumerate(child1.children):
                    c.parent = node                 
            #Ya agrego el error de no encontrar newline anteriormente

        #Else ::=  ''
        elif self.current_token in FOLLOW['Else']:
            node = None

        else: #Con la modificacion no deberia entrar aqui
            #Cuando no esta vacio pero se intento poner la produccion, se sincroniza en Statement
            self.quickError("Else","else")
            node = self.errorNode()

        return node
    
    def SimpleStatement(self):
        #SimpleStatement ::=  Expr SSTail
        if self.current_token in FIRST['Expr']:
            nodo = None
            child1 = self.Expr()
            child2 = self.SSTail()
            if child2!= None:
                nodo = Node("=")
                child1.parent = nodo
                child2.parent = nodo
            else: 
                nodo = child1
            return nodo

        #SimpleStatement ::= pass
        elif self.current_token == "PASS":
            self.getToken()
            return Node("pass")

        #SimpleStatement ::= return ReturnExpr
        elif self.current_token == "RETURN":
            self.getToken()
            nodo = Node("return")
            child1 = self.ReturnExpr()
            if child1 != None: ##CTSW
                child1.parent = nodo
            return nodo
        
        #Nunca deberia entrar aqui porque solo se llama si self.current_token in FIRST['SimpleStatement']
        self.quickError("SimpleStatement")
        return self.errorNode()

    def SSTail(self): # COMPLETADO
        # SSTail ::=  = Expr
        if self.current_token == "ASSIGN":
            self.getToken()
            return self.Expr()

        # SSTail ::=  ''
        if self.current_token in FOLLOW["SSTail"]:
            return None
        
        self.quickError("SSTail","=")
        return self.errorNode()


    def ReturnExpr(self):
        # ReturnExpr ::= Expr
        if self.current_token in FIRST['Expr']:
            return self.Expr()

        # ReturnExpr ::= ''
        elif self.current_token in FOLLOW["ReturnExpr"]:
            return None
        
        self.quickError("ReturnExpr")
        return self.errorNode()

    def Expr(self):
        #Expr ::=  orExpr ExprPrime
        prime, tofill = Place(), Place()
        child1 = self.orExpr()
        self.ExprPrime(prime, tofill)
        if not prime.empty:
            tofill.copyNodo(child1)
            return prime.nodo
        return child1

    def ExprPrime(self, head, tofill):
        #ExprPrime ::=   if andExpr else andExpr ExprPrime
        if self.current_token == "IF":
            nodo = Node("IFEXPR")
            self.getToken()
            head.saveNodo(nodo)
            if tofill.empty: tofill.start(nodo)

            child0 = self.andExpr()
            child0.parent = nodo
            if self.current_token == "ELSE":
                self.getToken()
                child1 = self.andExpr()
                child1.parent = nodo
                child2 = self.ExprPrime(head, tofill)
                if child2 != None:
                    addChildFront(nodo, child2)
                return nodo
            else:
                self.quickError("ExprPrime","else")
        
        #ExprPrime ::=  ''
        elif self.current_token in FOLLOW['ExprPrime']:
            return None

        self.quickError("ExprPrime", "if")
        return self.errorNode()

    def orExpr(self):
        # orExpr ::= andExpr orExprPrime
        prime, tofill = Place(), Place()
        child1 = self.andExpr()
        self.orExprPrime(prime, tofill)
        if not prime.empty:
            tofill.copyNodo(child1)
            return prime.nodo
        return child1

    def orExprPrime(self, head, tofill):
        # orExprPrime ::= or andExpr orExprPrime
        if self.current_token == "OR":
            nodo = Node("OR")
            self.getToken()
            head.saveNodo(nodo)
            if tofill.empty: tofill.start(nodo)

            child1 = self.andExpr()
            child1.parent = nodo
            child2 = self.orExprPrime(head, tofill)
            if child2 != None:
                addChildFront(nodo, child2)
            return nodo

        #orExprPrime ::= epsilon
        if self.current_token in FOLLOW["OrExprPrime"]:
            return None

        self.quickError("OrExprPrime", "or")
        return self.errorNode()

    def andExpr(self):
        #andExpr ::= notExpr andExprPrime
        prime, tofill = Place(), Place()
        child1 = self.notExpr()
        self.andExprPrime(prime, tofill)
        if not prime.empty:
            tofill.copyNodo(child1)
            return prime.nodo
        return child1

    def andExprPrime(self, head, tofill):
        #andExprPrime ::=   and notExpr andExprPrime
        if self.current_token == "AND":
            nodo = Node("AND")
            self.getToken()
            head.saveNodo(nodo)
            if tofill.empty: tofill.start(nodo)

            child1 = self.notExpr()
            child1.parent = nodo
            child2 = self.andExprPrime(head, tofill)
            if child2 != None:
                addChildFront(nodo, child2)
            return nodo
        
        #andExprPrime ::=  ''
        if self.current_token in FOLLOW["AndExprPrime"]:
            return None
        
        self.quickError("AndExprPrime", "and")
        return self.errorNode()
    
    def notExpr(self):
        # notExpr ::= CompExpr notExprPrime
        prime, tofill = Place(), Place()
        child1 = self.CompExpr()
        self.notExprPrime(prime, tofill)
        if not prime.empty:
            tofill.copyNodo(child1)
            return prime.nodo
        return child1

    def notExprPrime(self, head, tofill):
        # notExprPrime ::= not CompExpr notExprPrime
        if self.current_token == "NOT":
            nodo = Node("NOT")
            self.getToken()
            head.saveNodo(nodo)
            if tofill.empty: tofill.start(nodo)

            child1 = self.CompExpr()
            child1.parent = nodo
            child2 = self.notExprPrime(head, tofill)
            if child2 != None:
                addChildFront(nodo, child2)
            return nodo

        #notExprPrime ::= epsilon
        elif self.current_token in FOLLOW["NotExprPrime"]:
            return None
        
        self.quickError("NotExprPrime","not")
        return self.errorNode()

    def CompExpr(self):
        #CompExpr ::=  IntExpr CompExprPrime
        prime, tofill = Place(), Place()
        child1 = self.IntExpr()
        self.CompExprPrime(prime, tofill)
        if not prime.empty:
            tofill.copyNodo(child1)
            return prime.nodo
        return child1

    def CompExprPrime(self, head, tofill):
        #CompExprPrime ::=   CompOp IntExpr CompExprPrime
        if self.current_token in FIRST['CompOp']:
            nodo = self.CompOp()
            head.saveNodo(nodo)
            if tofill.empty: tofill.start(nodo)

            child1 = self.IntExpr()
            child1.parent = nodo
            child2 = self.CompExprPrime(head, tofill)
            if child2 != None:
                addChildFront(nodo, child2)
            return nodo

        # CompExprPrime ::=  ''
        elif self.current_token in FOLLOW["CompExprPrime"]:
            return None
        
        self.quickError("CompExprPrime","Comp operator")
        return self.errorNode()

    def IntExpr(self):
        # IntExpr ::= Term IntExprPrime
        prime, tofill = Place(), Place()
        child1 = self.Term()
        self.IntExprPrime(prime, tofill)
        if not prime.empty:
            tofill.copyNodo(child1)
            return prime.nodo
        return child1

    def IntExprPrime(self, head, tofill):
        # IntExprPrime ::= -|+ Term IntExprPrime
        if self.current_token in ["ADD", "SUB"]:
            nodo = Node(self.current_token.value)
            self.getToken()
            head.saveNodo(nodo)
            if tofill.empty: tofill.start(nodo)

            child1 = self.Term()
            child1.parent = nodo
            child2 = self.IntExprPrime(head, tofill)
            if child2 != None:
                addChildFront(nodo, child2)
            return nodo

        #IntExprPrime ::= epsilon
        elif self.current_token in FOLLOW["IntExprPrime"]:
            return None
        
        self.quickError("IntExprPrime","+ | -")
        return self.errorNode()
    
    def Term(self):
        #Term ::=  Factor TermPrime
        prime, tofill = Place(), Place()
        child1 = self.Factor()
        self.TermPrime(prime, tofill)
        if not prime.empty:
            tofill.copyNodo(child1)
            return prime.nodo
        return child1
   
    def TermPrime(self, head, tofill):
        #TermPrime ::=   *|//|% Factor TermPrime
        if self.current_token in ["MUL", "DIV", "MOD"]:
            nodo = Node(self.current_token.value)
            self.getToken()
            head.saveNodo(nodo)
            if tofill.empty: tofill.start(nodo)
            
            child1 = self.Factor()
            child1.parent = nodo
            child2 = self.TermPrime(head, tofill)
            if child2 != None:
                addChildFront(nodo, child2)
            return nodo
            
        #TermPrime ::=  ε
        elif self.current_token in FOLLOW["TermPrime"]:
            return None
        
        self.quickError("TermPrime", "* | // | %")
        return self.errorNode()

    def Factor(self):  # COMPLETADO
        # Factor ::= - Factor
        if self.current_token == "SUB":
            nodo = Node("-")
            self.getToken()
            child = self.Factor()
            if child!=None: child.parent = nodo
            return nodo

        # Factor ::= Name
        elif self.current_token in FIRST['Name']:
            return self.Name()

        # Factor ::= Literal
        elif self.current_token in FIRST['Literal']:
            return self.Literal()

        # Factor ::= List
        elif self.current_token in FIRST['List']:
            return self.List()

        # Factor ::= ( Expr )
        elif self.current_token == "LPAREN":
            self.getToken()
            nodo = self.Expr()#
            if self.current_token == "RPAREN":
                self.getToken()
                return nodo
            else: self.quickError("Factor",")")
        
        self.quickError("Factor")
        return self.errorNode()
    
    def Name(self): # COMPLETADO
        # Name ::= ID NameTail
        if self.current_token == "ID":
            nodo = Node(self.current_token.value)
            self.getToken()
            child2 = self.NameTail()
            if child2 != None:
                child2.parent = nodo
            return nodo
        #Nunca deberia entrar aqui ya que cuando Name es llamado es cuando self.current_token = ID
        self.quickError("Name","ID")
        #No hace recuperacion de errores porque solo lo ignora si no esta
        return self.errorNode()
    
    def NameTail(self):
        #NameTail ::=  ( ExprList )
        if self.current_token == "LPAREN":
            self.getToken()
            nodo = self.ExprList()
            nodo.name = "()"
            if self.current_token == "RPAREN":
                self.getToken()
                return nodo
            else: self.quickError("NameTail",")")

        #NameTail ::=  List
        elif self.current_token in FIRST['List']:
            return self.List() #Lista ve por sus propios errores

        #NameTail ::=  ε # FOLLOWS
        elif self.current_token in FOLLOW["NameTail"]:
            return None
        
        self.quickError("NameTail")
        return self.errorNode()

    def Literal(self):
        if self.current_token in ["NONE", "TRUE", "FALSE", "INTEGER", "STRING"]:
            nodo = Node(self.current_token.value)
            self.getToken()
            return nodo
        #Nunca deberia entrar aqui porque solo se llama si self.current_token in ["NONE", "TRUE", "FALSE", "INTEGER", "STRING"]
        self.quickError("Literal")
        #No hace recuperacion de errores porque solo lo ignora si no esta
        #while self.current_token not in FOLLOW['Literal'] and self.current_token != "EOF":
        #    self.getToken()
        return self.errorNode()

    def List(self):
        # List ::= [ ExprList ]
        if self.current_token == "LBRACKET":
            self.getToken()
            nodo = self.ExprList()
            nodo.name = ("[]")
            if self.current_token == "RBRACKET":
                self.getToken()
                return nodo
            else: self.quickError("List","]")
        
        self.quickError("List","[")
        return self.errorNode()

    def ExprList(self):
        # ExprList ::= Expr ExprListTail
        if self.current_token in FIRST['Expr']:
            nodo = Node("()")
            child1 = self.Expr()
            child1.parent = nodo
            setattr(child1, "order", 0)

            nodeTail = self.ExprListTail()
            if nodeTail!=None:
                childrens = self.nodeToList(nodeTail,"TAIL")
                for i, c in enumerate(childrens):
                    c.parent = nodo
                    setattr(c, "order", i+1)
            return nodo

        # ExprList ::=  ε
        elif self.current_token in FOLLOW["ExprList"]:
            return None # No agrega error pero no retorna un nodo
        
        self.quickError("ExprList")
        return self.errorNode()

    def ExprListTail(self):
        #ExprListTail ::=  , Expr ExprListTail
        if self.current_token == "COMMA":
            nodo = Node("TAIL")
            self.getToken()
            child1 = self.Expr()
            child1.parent = nodo
            child2 = self.ExprListTail()
            if child2 != None:
                child2.parent = nodo
            return nodo

        #ExprListTail ::=  ε # FOLLOWS
        elif self.current_token in FOLLOW["ExprListTail"]:
            return None
        
        self.quickError("ExprListTail") #Significa que especifico un error al intentar colocar un ExprListTail
        return self.errorNode()
    
    def CompOp(self):
        #CompOp ::=  == | != | < | > | <= | >= | is
        if self.current_token in ["EQ", "DIF", "LESS", "GRTR", "LESSEQ", "GRTREQ", "IS"]:
            nodo = Node(self.current_token.value)
            self.getToken()
            return nodo
        #Nunca deberia entrar aqui porque solo se llama si self.current_token in FIRST['CompOp']
        self.quickError("CompOp", "Comp operator")
        #No hace recuperacion de errores porque solo lo ignora si no esta
        return self.errorNode()