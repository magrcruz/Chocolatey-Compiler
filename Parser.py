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

    def to_NewLine(self): #R
        while self.current_token != "NEWLINE" :
            self.getToken()

    def add_error(self, error):
        error.col = self.current_token.col
        error.descripcion += ", found %s" % self.current_token.value
        self.error_list.append(error)

    def S(self):
        #print("INFO PARSE - Start scanning...")

        self.abstract_syntax_tree = self.Program()
        if self.current_token != "EOF":
            self.add_error("Se encontraron tokens no esperados")

        #Errores
        print("INFO SCAN - Completed with %i errors" % (len(self.escaner.errores)))
        if len(self.escaner.errores):
            for i in self.escaner.errores:
                print("Error:  %s " % i)

        print("INFO PARSE - Completed with %i errors" % (len(self.error_list)))
        if len(self.error_list):
            for i in self.error_list:
                print("Error:  %s " % i)
            return False
        
        elif not len(self.escaner.errores): #Si no hubo errores en el escaner ni en el parser
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
        child2 = self.StatementList()
        if child2!=None:
            child2.parent = nodo
        return nodo

    def DefList(self):
        nodo = None
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
  
        #DefList ::=  ''
        elif self.current_token not in FOLLOW['DefList']:
            #En este caso esta bien ya que si hay un arror despues de la funcion corresponde a statement list
            self.add_error(Error("DefList", "Follow(DefList) not founded", self.current_token.row))
            while self.current_token not in FOLLOW['DefList'] and self.current_token not in ["EOF","NEWLINE"]:
                self.getToken()
            if self.current_token == "NEWLINE" : self.getToken()
            nodo = self.errorNode()
        return nodo
        
    def Def(self):
        nodo = None
        #Def ::=  def ID ( TypedVarList ) Return : NEWLINE Block
        addedError = True
        # Verifica hasta los dos puntos
        if self.current_token == "DEF":
            nodo = Node("Def")
            self.getToken()
            if self.current_token == "ID":
                Node(self.current_token.value, parent=nodo)
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
                            if self.current_token == "NEWLINE":
                                self.getToken()
                                child3 = self.Block()
                                child3.parent = nodo
                                addedError = False
                            else: self.add_error(Error("DEF", "NEWLINE not founded", self.current_token.row))
                        else: self.add_error(Error("DEF", "COLON not founded", self.current_token.row))
                    else: self.add_error(Error("DEF", "RPAREN not founded", self.current_token.row))
                else: self.add_error(Error("DEF", "LPAREN not founded", self.current_token.row))
            else: self.add_error(Error("DEF", "<ID> not founded", self.current_token.row))
        else: self.add_error(Error("DEF", "DEF not founded", self.current_token.row))

        if addedError: nodo = self.errorNode()
        # Si encontro algun error sincroniza con los follow
        if self.current_token not in FOLLOW['Def'] and not addedError:
            #Si no esta en los follow pero aun no anadio algun error
            self.add_error(Error("DEF", "Token inesperado", self.current_token.row))
        while self.current_token not in FOLLOW['Def'] and self.current_token not in ["EOF","NEWLINE"]:
            self.getToken()
        if self.current_token == "NEWLINE" : self.getToken()##
        return nodo
    
    def TypedVar(self):
        # TypeVar ::= ID : Type
        addError = True
        nodo = None
        if self.current_token=="ID":
            nodo = Node(":")
            Node(self.current_token.value, parent=nodo)
            self.getToken()
            if self.current_token == "COLON":
                self.getToken()
                child2 = self.Type()
                child2.parent = nodo
                addError = False

        # Si encontro algun error sincroniza con los follow
        if addError: nodo = self.errorNode()
        if self.current_token not in FOLLOW['TypedVar'] and self.current_token != "NEWLINE" or addError:
            self.add_error(Error("TypedVar", "Token inesperado", self.current_token.row))
        while self.current_token not in FOLLOW['TypedVar'] and self.current_token not in ["EOF","NEWLINE"]:
            self.getToken()
        return nodo

    def Type(self):
        addError = True
        nodo = None
        # Type ::= int
        if self.current_token=="INT" or self.current_token=="STR":
            nodo = Node(self.current_token.value)
            self.getToken()
            addError = False

        # Type ::= [ Type ]
        elif self.current_token == "LBRACKET":
            self.getToken()
            nodo = self.Type()
            if self.current_token == "RBRACKET":
                addError = False
                self.getToken()
                nodo.name = "[{}]".format(nodo.name)

        # Sincronizacion de errores
        if addError: nodo = self.errorNode()
        if self.current_token not in FOLLOW["Type"] and self.current_token != "NEWLINE" or addError:
            self.add_error(Error("Type", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['Type'] and self.current_token not in ["EOF","NEWLINE"]:
                self.getToken()
        return nodo

    def TypedVarList(self):
        nodo = None
        #TypedVarList ::=  TypedVar TypedVarListTail
        if self.current_token in FIRST['TypedVarList']: #ID
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

        #TypedVarList ::=  ''
        if self.current_token not in FOLLOW['TypedVarList'] and self.current_token != "NEWLINE":
            self.add_error(Error("TypedVarList", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['TypedVarList'] and self.current_token not in ["EOF","NEWLINE"]:
                self.getToken()
            nodo =  self.errorNode()
        return nodo

    def TypedVarListTail(self):
        nodo = None
        #TypedVarListTail ::=  , TypedVar TypedVarListTail
        if self.current_token == "COMMA":
            nodo = Node("TAIL")
            self.getToken()
            child1 = self.TypedVar()
            child1.parent = nodo
            child2 = self.TypedVarListTail()
            if child2 != None:#Puede ser vacio
                child2.parent = nodo

        #TypedVarListTail ::=  ''
        if self.current_token not in FOLLOW['TypedVarListTail'] and self.current_token != "NEWLINE":
            self.add_error(Error("TypedVarListTail", "Token inesperado", self.current_token.row))
            nodo = self.errorNode()
            while self.current_token not in FOLLOW['TypedVarListTail'] and self.current_token not in ["EOF","NEWLINE"]:
                self.getToken()
        return nodo
    
    def Return(self):
        nodo = None
        addError = True
        #Return ::= -> Type
        if self.current_token == "ARROW":
            nodo = Node("->")
            self.getToken()
            child1 = self.Type()
            child1.parent = nodo
            addError = False
        
        if self.current_token in FOLLOW['Return']:
            addError = False

        if addError : nodo = self.errorNode()

        #Return ::= epsilon
        if self.current_token not in FOLLOW['Return'] and self.current_token != "NEWLINE":
            self.add_error(Error("Return", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['Return'] and self.current_token not in ["EOF","NEWLINE"]:
                self.getToken()
        return nodo

    def Block(self):
        nodo = Node("DO")
        #Block ::= IDENT Statement StatementList DEDENT
        addError = True
        if self.current_token == "IDENT":
            self.getToken()
            child1 = self.Statement()
            child1.parent = nodo
            childs = self.StatementList()
            if childs != None:
                for i,c in enumerate(childs.children):
                    c.parent = nodo##
            if self.current_token == "DEDENT":
                self.getToken()
                addError = False

        # Sincronizacion de errores
        if self.current_token not in FOLLOW["Block"] and self.current_token != "NEWLINE" and addError:
            self.add_error(Error("Block", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['Block'] and self.current_token not in ["EOF","NEWLINE"]:
                self.getToken()
            nodo = self.errorNode()
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
        if self.current_token not in FOLLOW['StatementList']:
            nodo = self.errorNode()
            self.add_error(Error("StatementList", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['StatementList'] or self.current_token != "EOF":
                self.getToken()
        return nodo

    def Statement(self): #M
        nodo = None
        #Statement ::=  SimpleStatement NEWLINE
        if self.current_token in FIRST['SimpleStatement']:
            nodo = self.SimpleStatement()

            #En ese se sincroniza avanzando hasta newline
            if self.current_token != "NEWLINE":
                nodo = self.add_error()
                self.add_error(Error("Statement","Token inesperado", self.current_token.row))
                while self.current_token != "NEWLINE" and self.current_token != "EOF":
                    self.getToken()

            if self.current_token == "NEWLINE":
                self.getToken()

        #Statement ::=  if Expr : NEWLINE Block ElifList Else
        elif self.current_token == "IF":
            self.getToken()
            nodo = Node("IF_BLOCK")
            nodoif = Node("IF", parent=nodo)
            child1 = self.Expr()
            child1.parent = nodoif
            if self.current_token == "COLON":
                self.getToken()
            else:
                self.add_error(Error("Statement", "COLON not founded",self.current_token.row))
                nodo = self.errorNode()
            #Sincroniza hasta el newline
            if self.current_token != "NEWLINE":
                self.add_error(Error("Statement","Token inesperado", self.current_token.row))
                nodo = self.errorNode()
                while self.current_token != "NEWLINE" or self.current_token != "EOF":
                    self.getToken()

            if self.current_token == "NEWLINE":
                self.getToken()

            child2 = self.Block()
            child2.parent = nodoif
            child2 = self.ElifList()
            if child2!=None:
                for _,c in enumerate(child2.children):
                    c.parent = nodo
            child2 = self.Else()
            if child2!=None: child2.parent= nodo

        #Statement ::=  while Expr : NEWLINE Block
        elif self.current_token == "WHILE":
            nodo = Node("WHILE")
            self.getToken()
            child = self.Expr()
            child.parent = nodo
            if self.current_token =="COLON":
                self.getToken()
            else:
                self.add_error(Error("Statement", "COLON not founded",self.current_token.row))
                nodo = self.errorNode()
            #Sincroniza hasta el newline
            if self.current_token != "NEWLINE":
                nodo = self.errorNode()
                self.add_error(Error("Statement","Token inesperado", self.current_token.row))
                while self.current_token != "NEWLINE" or self.current_token != "EOF":
                    self.getToken()

            if self.current_token == "NEWLINE":
                self.getToken()

            child1 = self.Block()
            child1.parent = nodo
            
        #Statement ::=  for ID in Expr : NEWLINE Block
        elif self.current_token == "FOR":
            nodo = Node("FOR")
            self.getToken()
            if self.current_token == "ID":
                grandson = Node(self.current_token.value)
                self.getToken()
                if self.current_token == "IN":
                    child1 = Node("IN", parent=nodo)
                    grandson.parent = child1
                    self.getToken()
                    child2 = self.Expr()
                    child2.parent = child1
                    if self.current_token == "COLON":
                        self.getToken()
                    else:
                        nodo = self.errorNode()
                        self.add_error(Error("Statement", "COLON not founded",self.current_token.row))
                else:
                    nodo = self.errorNode()
                    self.add_error(Error("Statement", "IN not founded",self.current_token.row))
            else:
                nodo = self.errorNode()
                self.add_error(Error("Statement", "<ID  > not founded",self.current_token.row))

            #Sincroniza hasta el newline
            if self.current_token != "NEWLINE":
                self.add_error(Error("Statement","Token inesperado", self.current_token.row))
                nodo = self.errorNode()
                while self.current_token != "NEWLINE" or self.current_token != "EOF":
                    self.getToken()

            if self.current_token == "NEWLINE":
                self.getToken()
            child2 = self.Block()
            child2.parent = nodo

        # Statment no puede ser vacio, asi que tambien evaluamos else
        #       else
        #           self.add_error(Error("Statement","Token inesperado", self.current_token.row))
        else:
            self.add_error(Error("Statement","No se encontro statement",self.current_token.row))##
            nodo = self.errorNode()

        if self.current_token not in FOLLOW['Statement']:
            nodo = self.errorNode()
            self.add_error(Error("Statement","Token inesperado",self.current_token.row))
            while self.current_token not in FOLLOW['Statement'] and self.current_token != "EOF":
                self.getToken()
        return nodo

    def ElifList(self): #FALTA
        nodo = None
        #ElifList ::= Elif ElifList
        if self.current_token in FIRST['Elif']:
            nodo = Node("ELIFLIST")
            child1 = self.Elif()
            childs = self.ElifList()
            child1.parent = nodo
            if childs != None:
                for i,c in enumerate(childs.children):
                    c.parent = nodo##check

        #ElifList ::= epsilon
        if self.current_token not in FOLLOW['ElifList']:
            nodo = self.errorNode()
            self.add_error(Error("ElifList","Token inesperado",self.current_token.row))
            while self.current_token not in FOLLOW['ElifList'] and self.current_token != "EOF":
                self.getToken()
        return nodo

    def Elif(self): 
        nodo = None
        addedError = True
        #Elif ::= elif Expr : NEWLINE Block
        if self.current_token == "ELIF":
            self.getToken()
            child1 = self.Expr()
            if self.current_token == "COLON":
                self.getToken()
                if self.current_token == "NEWLINE":
                    self.getToken()
                    child2 = self.Block()
                    nodo = Node("ELIF")
                    child1.parent = nodo
                    child2.parent = nodo
                    addedError = False
                else: self.add_error(Error("Elif", "NEWLINE not founded", self.current_token.row))
            else: self.add_error(Error("Elif", "COLON not founded", self.current_token.row))
        else: self.add_error(Error("Elif", "ELIF not founded", self.current_token.row))

        if self.current_token not in FOLLOW['Elif']:
            nodo = self.errorNode()
            self.add_error(Error("Elif","Token inesperado",self.current_token.row))
        while self.current_token not in FOLLOW['Elif'] and self.current_token != "EOF":
            self.getToken()
        return nodo

    def Else(self):
        node = None
        #Else ::=  else : NEWLINE Block
        addedError = True
        if self.current_token == "ELSE":
            self.getToken()
            if self.current_token == "COLON":
                self.getToken()
                if self.current_token == "NEWLINE":
                    self.getToken()
                    node = Node("ELSE")
                    child1 = self.Block()
                    #Ya que no existe una condicion se puede asignar directamente a else
                    for _,c in enumerate(child1.children):
                        c.parent = node                 
                    addedError = False
                else: self.add_error(Error("Else", "NEWLINE not founded", self.current_token.row))
            else: self.add_error(Error("Else", "COLON not founded", self.current_token.row))
        else: self.add_error(Error("Else", "ELSE not founded", self.current_token.row))##

        #Else ::=  ''
        if not addedError and self.current_token not in FOLLOW['Else']:
            node = self.errorNode()
            self.add_error(Error("Else","Token inesperado",self.current_token.row))
        while self.current_token not in FOLLOW['Else'] and self.current_token != "EOF":
            self.getToken()
        return node
    
    def SimpleStatement(self): ##M
        nodo = None
        #SimpleStatement ::=  Expr SSTail
        if self.current_token in FIRST['Expr']:
            child1 = self.Expr()
            child2 = self.SSTail()
            if child2!= None:
                nodo = Node("=")
                child1.parent = nodo
                child2.parent = nodo
            else: 
                nodo = child1

        #SimpleStatement ::= pass
        elif self.current_token == "PASS":
            nodo = Node("PASS")
            self.getToken()

        #SimpleStatement ::= return ReturnExpr
        elif self.current_token == "RETURN":
            self.getToken()
            nodo = Node("return")
            child1 = self.ReturnExpr()
            child1.parent = nodo
        else:
            nodo = self.errorNode
            self.add_error(Error("SimpleStatement","Token inesperado",self.current_token.row))

        if self.current_token not in FOLLOW['SimpleStatement']:
            nodo = self.errorNode
            self.add_error(Error("SimpleStatement","Token inesperado",self.current_token.row))
            while self.current_token not in FOLLOW['SimpleStatement'] and self.current_token != "EOF":
                self.getToken()
        return nodo
## A partir de aqui Ruben

    def SSTail(self): # COMPLETADO
        nodo = None
        # SSTail ::=  = Expr
        if self.current_token == "ASSIGN":
            self.getToken()
            nodo = self.Expr()

        # SSTail ::=  Epsilon
        if self.current_token not in FOLLOW["SSTail"]:
            nodo = self.errorNode()
            self.add_error(Error("SSTail", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['SSTail'] and self.current_token != "EOF":
                self.getToken()
        return nodo

    def ReturnExpr(self): # COMPLETADO
        nodo = None
        # ReturnExpr ::= Expr
        if self.current_token in FIRST['Expr']: #ID
            nodo = self.Expr()

        # ReturnExpr ::= Epsilon
        if self.current_token not in FOLLOW["ReturnExpr"]:
            nodo = self.errorNode()
            self.add_error(Error("ReturnExpr", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['ReturnExpr'] and self.current_token != "EOF":
                self.getToken()
        return nodo

    def Expr(self):
        #Expr ::=  orExpr ExprPrime
        prime, tofill = Place(), Place()
        child1 = self.orExpr()
        self.ExprPrime(prime, tofill)
        if not prime.empty:
            tofill.copyNodo(child1)
            return prime.nodo
        return child1

    def ExprPrime(self, head, tofill): # COMPLETADO
        nodo = None
        #ExprPrime ::=   if andExpr else andExpr ExprPrime
        addedError = True
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

                addedError = False
            else: self.add_error(Error("ExprPrime", "ELSE not founded", self.current_token.row))

        #ExprPrime ::=  ''
        if not addedError and self.current_token not in FOLLOW['ExprPrime']:
            nodo = self.errorNode()
            self.add_error(Error("ExprPrime","Token inesperado",self.current_token.row))
        while self.current_token not in FOLLOW['ExprPrime'] and self.current_token != "EOF":
            self.getToken()
        return nodo

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
        nodo = None
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

        #orExprPrime ::= epsilon
        if self.current_token not in FOLLOW["OrExprPrime"]:
            nodo = self.errorNode()
            self.add_error(Error("OrExprPrime", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['OrExprPrime'] and self.current_token != "EOF":
                self.getToken()
        return nodo

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
        nodo = None
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

        #andExprPrime ::=  ''
        if self.current_token not in FOLLOW["AndExprPrime"]:
            nodo = self.errorNode()
            self.add_error(Error("AndExprPrime", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['AndExprPrime'] and self.current_token != "EOF":
                self.getToken()
        return nodo
    
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
        nodo = None
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

        #notExprPrime ::= epsilon
        if self.current_token not in FOLLOW["NotExprPrime"]:
            nodo = self.errorNode()
            self.add_error(Error("NotExprPrime", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['NotExprPrime'] and self.current_token != "EOF":
                self.getToken()
        return nodo

    def CompExpr(self): # COMPLETADO
        #CompExpr ::=  IntExpr CompExprPrime
        prime, tofill = Place(), Place()
        child1 = self.IntExpr()
        self.CompExprPrime(prime, tofill)
        if not prime.empty:
            tofill.copyNodo(child1)
            return prime.nodo
        return child1

    def CompExprPrime(self, head, tofill): #
        nodo = None
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

        # CompExprPrime ::=  ''
        if self.current_token not in FOLLOW["CompExprPrime"]:
            nodo = self.errorNode()
            self.add_error(Error("CompExprPrime", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['CompExprPrime'] and self.current_token != "EOF":
                self.getToken()
        return nodo

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
        nodo = None
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

        #IntExprPrime ::= epsilon
        if self.current_token not in FOLLOW["IntExprPrime"]:
            nodo = self.errorNode()
            self.add_error(Error("IntExprPrime", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['IntExprPrime'] and self.current_token != "EOF":
                self.getToken()
        return nodo
    
    def Term(self): # COMPLETADO
        #Term ::=  Factor TermPrime
        prime, tofill = Place(), Place()
        child1 = self.Factor()
        self.TermPrime(prime, tofill)#Si esto sucede debe agregar el hijo al nivel mas bajo a la izquierda
        if not prime.empty:
            tofill.copyNodo(child1)
            return prime.nodo
        return child1
   
    def TermPrime(self, head, tofill):
        nodo = None
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
            
        #TermPrime ::=  ε
        if self.current_token not in FOLLOW["TermPrime"]:
            nodo = self.errorNode()
            self.add_error(Error("TermPrime", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['TermPrime'] and self.current_token != "EOF":
                self.getToken()
        return nodo

    def Factor(self):  # COMPLETADO
        addError = True
        nodo = None
        # Factor ::= - Factor
        if self.current_token == "SUB":
            nodo = Node("-")
            self.getToken()
            child = self.Factor()
            if child!=None: child.parent = nodo
            addError = False

        # Factor ::= Name
        elif self.current_token in FIRST['Name']:
            nodo = self.Name()
            addError = False

        # Factor ::= Literal
        elif self.current_token in FIRST['Literal']:
            nodo = self.Literal()
            addError = False

        # Factor ::= List
        elif self.current_token in FIRST['List']:
            nodo = self.List()
            addError = False

        # Factor ::= ( Expr )
        elif self.current_token == "LPAREN":
            self.getToken()
            nodo = self.Expr()#
            if self.current_token == "RPAREN":
                self.getToken()
                addError = False
        
        else:
            nodo = self.errorNode()#

        if addError or self.current_token not in FOLLOW["Factor"]:
            self.add_error(Error("Factor", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['Factor'] and self.current_token != "EOF":
                self.getToken()
        return nodo
    
    def Name(self): # COMPLETADO
        nodo = None
        # Name ::= ID NameTail
        if self.current_token == "ID":
            nodo = Node(self.current_token.value, parent=nodo)
            self.getToken()
            child2 = self.NameTail()
            if child2 != None:
                child2.parent = nodo
        else:
            nodo = self.errorNode()
            self.add_error(Error("Name", "ID not founded", self.current_token.row))
            while self.current_token != "NEWLINE" and  self.current_token != "EOF":
                self.getToken()
        return nodo
    
    def NameTail(self): # COMPLETADO
        addError = True
        nodo = None
        #NameTail ::=  ( ExprList )
        if self.current_token == "LPAREN":
            self.getToken()
            nodo = self.ExprList()
            nodo.name = "()"
            if self.current_token == "RPAREN":
                self.getToken()
                addError = False

        #NameTail ::=  List
        elif self.current_token in FIRST['List']:
            nodo = self.List()
            addError = False

        #NameTail ::=  ε # FOLLOWS
        if addError and self.current_token not in FOLLOW["NameTail"]:
            nodo = self.errorNode()
            self.add_error(Error("NameTail", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['NameTail'] and self.current_token != "EOF":
                self.getToken()
        return nodo

    def Literal(self): # COMPLETADO
        nodo = None
        if self.current_token in ["NONE", "TRUE", "FALSE", "INTEGER", "STRING"]:
            nodo = Node(self.current_token.value)
            self.getToken()

        if self.current_token not in FOLLOW["Literal"]:
            self.add_error(Error("Literal", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['Literal'] and self.current_token != "EOF":
                self.getToken()
            nodo = self.errorNode()
        return nodo

    def List(self):
        nodo = None
        addedError = True
        # List ::= [ ExprList ]
        if self.current_token == "LBRACKET":
            self.getToken()
            nodo = self.ExprList()
            nodo.name = ("[]")
            if self.current_token == "RBRACKET":
                self.getToken()
                addedError = False
            else:   self.add_error(Error("List", "LBRACKET not founded", self.current_token.row))
        else:   self.add_error(Error("List", "RBRACKET not founded", self.current_token.row))

        if addedError:
          nodo = self.errorNode()
          while self.current_token != "NEWLINE" and self.current_token != "EOF":
            self.getToken()
        return nodo

    def ExprList(self):  # COMPLETADO
        nodo = None
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

        # ExprList ::=  ε
        if self.current_token not in FOLLOW["ExprList"]:
            nodo = self.errorNode()
            self.add_error(Error("ExprList", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['ExprList'] and self.current_token != "EOF":
                self.getToken()
        
        return nodo

    def ExprListTail(self): #M
        nodo = None
        #ExprListTail ::=  , Expr ExprListTail
        if self.current_token == "COMMA":
            nodo = Node("TAIL")
            self.getToken()
            child1 = self.Expr()
            child1.parent = nodo
            child2 = self.ExprListTail()
            if child2 != None:
                child2.parent = nodo

        #ExprListTail ::=  ε # FOLLOWS
        if self.current_token not in FOLLOW["ExprListTail"]:
            nodo = self.errorNode()
            self.add_error(Error("ExprListTail", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['ExprListTail'] and self.current_token != "EOF":
                self.getToken()
        return nodo

    def CompOp(self): # COMPLETADO
        #CompOp ::=  == | != | < | > | <= | >= | is
        if self.current_token in ["EQ", "DIF", "LESS", "GRTR", "LESSEQ", "GRTREQ", "IS"]:
            nodo = Node(self.current_token.value)
            self.getToken()
            return nodo

        if self.current_token not in FOLLOW["CompOp"]:
            self.add_error(Error("CompOp", "Token inesperado", self.current_token.row))
            while self.current_token not in FOLLOW['CompOp'] and self.current_token != "EOF":
                self.getToken()
            return self.errorNode()

if not DEBUG:
    escaner = Scanner()
    escaner.begin("file.txt")
    miparser = Parser(escaner)
    #TOKEN_INPUT = ["PASS", "NEWLINE", "EOF"]
    miparser.S()