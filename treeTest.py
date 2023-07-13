from Parser import *

class TestTree():
    def __init__(self):
        self.parser = Parser(None)

    def Program(self):
        self.parser.TOKEN_INPUT = "DEF ID LPAREN RPAREN ARROW INT COLON NEWLINE IDENT PASS NEWLINE DEDENT".split()
        root = self.parser.Program()
        render_tree(root)

        self.parser.TOKEN_INPUT = "DEF ID LPAREN RPAREN ARROW INT COLON NEWLINE IDENT PASS NEWLINE DEDENT WHILE INTEGER COLON NEWLINE IDENT PASS NEWLINE DEDENT PASS NEWLINE DEDENT DEDENT".split()
        root = self.parser.Program()
        render_tree(root)
        
    def DefList(self):
        #DefList ::=  ''
        self.parser.TOKEN_INPUT = "EOF".split()
        self.parser.getToken()
        root = self.parser.DefList()
        print(">> == WORKS EMPTY == <<\n" + str(root == None)+"\n")

        #DefList ::=  Def
        self.parser.TOKEN_INPUT = "DEF ID LPAREN RPAREN ARROW INT COLON NEWLINE IDENT PASS NEWLINE DEDENT".split()
        self.parser.getToken()
        root = self.parser.DefList()
        render_tree(root)

        #DefList ::=  Def Def 
        self.parser.TOKEN_INPUT = "DEF ID LPAREN ID COLON INT RPAREN ARROW INT COLON NEWLINE IDENT PASS NEWLINE DEDENT DEF ID LPAREN RPAREN ARROW INT COLON NEWLINE IDENT PASS NEWLINE DEDENT".split()
        self.parser.getToken()
        root = self.parser.DefList()
        render_tree(root)

        #DefList ::=  Def Def D:
        self.parser.TOKEN_INPUT = "DEF ID LPAREN ID INT RPAREN ARROW INT COLON NEWLINE IDENT PASS NEWLINE DEDENT DEF ID LPAREN RPAREN ARROW NUMBER COLON NEWLINE IDENT PASS NEWLINE DEDENT".split()
        self.parser.getToken()
        root = self.parser.DefList()
        render_tree(root)

    def Def(self):
        #TypedVar ::=  def ID ( TypedVarList ) Return : NEWLINE Block
        self.parser.TOKEN_INPUT = "DEF ID LPAREN ID COLON INT RPAREN ARROW INT COLON NEWLINE IDENT PASS NEWLINE DEDENT".split()
        self.parser.getToken()
        root = self.parser.Def()
        render_tree(root)

        #TypedVar ::=  def ID ( ) Return : NEWLINE Block
        self.parser.TOKEN_INPUT = "DEF ID LPAREN RPAREN ARROW INT COLON NEWLINE IDENT PASS NEWLINE DEDENT".split()
        self.parser.getToken()
        root = self.parser.Def()
        render_tree(root)

        #TypedVar ::=  def ID ( TypedVarList ) : NEWLINE Block
        self.parser.TOKEN_INPUT = "DEF ID LPAREN ID COLON INT RPAREN COLON NEWLINE IDENT PASS NEWLINE DEDENT".split()
        self.parser.getToken()
        root = self.parser.Def()
        render_tree(root)

        #TypedVar ::=  def ID ( TypedVarList ) Return : NEWLINE D:
        self.parser.TOKEN_INPUT = "DEF ID LPAREN ID COLON INT RPAREN ARROW INT COLON".split()
        self.parser.getToken()
        root = self.parser.Def()
        render_tree(root)

        #TypedVar ::=  def ( TypedVarList ) Return : NEWLINE D:
        self.parser.TOKEN_INPUT = "DEF LPAREN ID COLON INT RPAREN ARROW INT COLON".split()
        self.parser.getToken()
        root = self.parser.Def()
        render_tree(root)

    def TypedVar(self):
        #TypedVar ::=  ID : Type :D
        self.parser.TOKEN_INPUT = "ID COLON LBRACKET INT RBRACKET".split()
        self.parser.getToken()
        root = self.parser.TypedVar()
        render_tree(root)

        #TypedVar ::=  ID : Type D:
        self.parser.TOKEN_INPUT = "ID COLON LBRACKET INT".split()
        self.parser.getToken()
        root = self.parser.TypedVar()
        render_tree(root)

        #TypedVar ::=  ID Type D:
        self.parser.TOKEN_INPUT = "ID LBRACKET INT RBRACKET".split()
        self.parser.getToken()
        root = self.parser.TypedVar()
        render_tree(root)

    def Type(self):
        #Type ::=  int
        self.parser.TOKEN_INPUT = "INT".split()
        self.parser.getToken()
        root = self.parser.Type()
        render_tree(root)

        #Type ::=  [ Type ]
        self.parser.TOKEN_INPUT = "LBRACKET INT RBRACKET".split()
        self.parser.getToken()
        root = self.parser.Type()
        render_tree(root)

        #Type ::=  [ Type D:
        self.parser.TOKEN_INPUT = "LBRACKET INT".split()
        self.parser.getToken()
        root = self.parser.Type()
        render_tree(root)

        #error
        self.parser.TOKEN_INPUT = "ERROR".split()
        self.parser.getToken()
        root = self.parser.Type()
        render_tree(root)

    def TypedVarList(self):
        #TypedVarList ::=  ''
        self.parser.TOKEN_INPUT = "RPAREN".split()
        self.parser.getToken()
        root = self.parser.TypedVarList()
        print(">> == WORKS EMPTY == <<\n" + str(root == None)+"\n")

        #TypedVarList ::=  TypedVar TypedVarListTail
        self.parser.TOKEN_INPUT = "ID COLON INT COMMA ID COLON INT COMMA ID COLON STR RPAREN".split()
        self.parser.getToken()
        root = self.parser.TypedVarList()
        render_tree(root)

        #TypedVarList ::=  TypedVar TypedVarListTail D:
        self.parser.TOKEN_INPUT = "COLON INT COMMA ID COLON STR COMMA ID COLON INT".split()
        self.parser.getToken()
        root = self.parser.TypedVarList()
        render_tree(root)

    def TypedVarListTail(self):
        #TypedVarListTail ::=  ''
        self.parser.TOKEN_INPUT = "RPAREN".split()
        self.parser.getToken()
        root = self.parser.TypedVarListTail()
        print(">> == WORKS EMPTY == <<\n" + str(root == None)+"\n")

        #TypedVarListTail ::=  , TypedVar :D
        self.parser.TOKEN_INPUT = "COMMA ID COLON INT RPAREN".split()
        self.parser.getToken()
        root = self.parser.TypedVarListTail()
        render_tree(root)

        #TypedVarListTail ::=  , TypedVar TypedVarListTail :D
        self.parser.TOKEN_INPUT = "COMMA ID COLON INT COMMA ID COLON STR RPAREN".split()
        self.parser.getToken()
        root = self.parser.TypedVarListTail()
        render_tree(root)

        #TypedVarListTail ::=  , TypedVar TypedVarListTail :D
        self.parser.TOKEN_INPUT = "COMMA ID COLON INT COMMA ID COLON STR COMMA ID COLON INT RPAREN".split()
        self.parser.getToken()
        root = self.parser.TypedVarListTail()
        render_tree(root)

        #TypedVarListTail ::=  , TypedVar TypedVar D:
        self.parser.TOKEN_INPUT = "COMMA ID INT".split()
        self.parser.getToken()
        root = self.parser.TypedVarListTail()
        render_tree(root)

    def Return(self):
        #Return ::=  ''
        self.parser.TOKEN_INPUT = "COLON".split()
        self.parser.getToken()
        root = self.parser.Return()
        print(">> == WORKS EMPTY == <<\n" + str(root == None)+"\n")

        #Return ::=  -> Type :D
        self.parser.TOKEN_INPUT = "ARROW LBRACKET INT RBRACKET".split()
        self.parser.getToken()
        root = self.parser.Return()
        render_tree(root)

        #Return ::=  -> Type D:
        self.parser.TOKEN_INPUT = "ARROW".split()
        self.parser.getToken()
        root = self.parser.Return()
        render_tree(root)

    #Block StatementList Statement
    def Block(self):
        #Block ::=  IDENT Statement StatementList DEDENT
        producciones = [
            "IDENT PASS NEWLINE PASS NEWLINE DEDENT DEDENT",
            "IDENT IF INTEGER COLON NEWLINE IDENT PASS NEWLINE DEDENT PASS NEWLINE DEDENT DEDENT",#Sin ElifList ni Else
            "IDENT WHILE INTEGER COLON NEWLINE IDENT PASS NEWLINE DEDENT PASS NEWLINE DEDENT DEDENT",
            "IDENT FOR ID IN INTEGER COLON NEWLINE IDENT PASS NEWLINE DEDENT PASS NEWLINE DEDENT DEDENT",
        ]
        for p in producciones:
            self.parser.TOKEN_INPUT = p.split()
            self.parser.getToken()
            root = self.parser.Block()
            render_tree(root)

    def StatementList(self):
        #Statement ::=  SimpleStatement NEWLINE
        #Statement ::=  if Expr : NEWLINE Block ElifList Else
        #Statement ::=  while Expr : NEWLINE Block
        #Statement ::=  for ID in Expr : NEWLINE Block
        producciones = [
            "PASS NEWLINE PASS NEWLINE DEDENT",
            "IF INTEGER COLON NEWLINE IDENT PASS NEWLINE DEDENT PASS NEWLINE DEDENT DEDENT",
            "WHILE INTEGER COLON NEWLINE IDENT PASS NEWLINE DEDENT PASS NEWLINE DEDENT DEDENT",
            "FOR ID IN INTEGER COLON NEWLINE IDENT PASS NEWLINE DEDENT PASS NEWLINE DEDENT DEDENT",
        ]
        for p in producciones:
            self.parser.TOKEN_INPUT = p.split()
            self.parser.getToken()
            root = self.parser.StatementList()
            render_tree(root)

    def Statement(self):
        #Statement ::=  SimpleStatement NEWLINE
        #Statement ::=  if Expr : NEWLINE Block ElifList Else
        #Statement ::=  while Expr : NEWLINE Block
        #Statement ::=  for ID in Expr : NEWLINE Block
        producciones = [
            "PASS NEWLINE DEDENT",
            "IF INTEGER COLON NEWLINE IDENT PASS NEWLINE DEDENT DEDENT",#Sin ElifList ni Else
            "WHILE INTEGER COLON NEWLINE IDENT PASS NEWLINE DEDENT DEDENT",
            "FOR ID IN INTEGER COLON NEWLINE IDENT PASS NEWLINE DEDENT DEDENT",
        ]
        for p in producciones:
            self.parser.TOKEN_INPUT = p.split()
            self.parser.getToken()
            root = self.parser.Statement()
            render_tree(root)

    #ElifList Elif Else
    def ElifList(self):
        #ElifList ::=  ''
        self.parser.TOKEN_INPUT = "DEDENT".split()
        self.parser.getToken()
        root = self.parser.ElifList()
        print(">> == WORKS EMPTY == <<\n" + str(root == None)+"\n")

        #ElifList ::=  Elif Elif
        self.parser.TOKEN_INPUT = "ELIF INTEGER COLON NEWLINE IDENT PASS NEWLINE DEDENT".split()
        self.parser.getToken()
        root = self.parser.ElifList()
        render_tree(root)

        #ElifList ::=  Elif Elif
        self.parser.TOKEN_INPUT = "ELIF INTEGER COLON NEWLINE IDENT PASS NEWLINE DEDENT ELIF INTEGER COLON NEWLINE IDENT PASS NEWLINE DEDENT".split()
        self.parser.getToken()
        root = self.parser.ElifList()
        render_tree(root)

    def Elif(self):
        #Else ::=  ''
        self.parser.TOKEN_INPUT = "DEDENT".split()
        self.parser.getToken()
        root = self.parser.Elif()
        print(">> == WORKS EMPTY == <<\n" + str(root == None)+"\n")

        #Elif ::=  elif Expr : NEWLINE Block
        self.parser.TOKEN_INPUT = "ELIF INTEGER COLON NEWLINE IDENT PASS NEWLINE DEDENT DEDENT".split()
        self.parser.getToken()
        root = self.parser.Elif()
        render_tree(root)

    def Else(self):
        #Else ::=  ''
        self.parser.TOKEN_INPUT = "DEDENT".split()
        self.parser.getToken()
        root = self.parser.Else()
        print(">> == WORKS EMPTY == <<\n" + str(root == None)+"\n")

        self.parser.TOKEN_INPUT = "ELSE COLON NEWLINE IDENT PASS NEWLINE DEDENT".split()
        self.parser.getToken()
        root = self.parser.Else()
        render_tree(root)

    #ReturnExpr SSTail SimpleStatement
    def SimpleStatement(self):
        #SimpleStatement ::=  pass
        self.parser.TOKEN_INPUT = "PASS NEWLINE".split()
        self.parser.getToken()
        root = self.parser.SimpleStatement()
        render_tree(root)

        #SimpleStatement ::=  return ReturnExpr
        self.parser.TOKEN_INPUT = "RETURN INTEGER NEWLINE".split()
        self.parser.getToken()
        root = self.parser.SimpleStatement()
        render_tree(root)

    def SSTail(self):
        self.parser.TOKEN_INPUT = "ASSIGN INTEGER NEWLINE".split()
        self.parser.getToken()
        root = self.parser.SSTail()
        render_tree(root)

    def ReturnExpr(self):
        self.parser.TOKEN_INPUT = "INTEGER NEWLINE".split()
        self.parser.getToken()
        root = self.parser.ReturnExpr()
        render_tree(root)

    def CompExpr(self):
        self.parser.TOKEN_INPUT = "INTEGER EQ INTEGER EQ INTEGER EQ INTEGER NEWLINE".split()
        self.parser.getToken()
        root = self.parser.CompExpr()
        render_tree(root)

    def CompExprPrime(self):
        self.parser.TOKEN_INPUT = "EQ INTEGER EQ INTEGER EQ INTEGER NEWLINE".split()
        self.parser.getToken()
        root = self.parser.CompExprPrime()
        render_tree(root)

    def IntExpr(self):
        self.parser.TOKEN_INPUT = "INTEGER ADD INTEGER ADD INTEGER NEWLINE".split()
        self.parser.getToken()
        root = self.parser.IntExpr()
        render_tree(root)

    def IntExprPrime(self):
        self.parser.TOKEN_INPUT = "ADD STRING ADD STRING NEWLINE".split()
        self.parser.getToken()
        root = self.parser.IntExprPrime()
        render_tree(root)

    def Term(self):
        self.parser.TOKEN_INPUT = "INTEGER MUL INTEGER MOD INTEGER DIV INTEGER NEWLINE".split()
        self.parser.getToken()
        root = self.parser.Term()
        render_tree(root)

        self.parser.TOKEN_INPUT = "INTEGER MUL INTEGER MOD INTEGER NEWLINE".split()
        self.parser.getToken()
        root = self.parser.Term()
        render_tree(root)
        '''EXPECTED OUTPUT
        MOD
        ├── MUL
        │   ├── INTEGER
        │   └── INTEGER
        └── INTEGER
        '''

        self.parser.TOKEN_INPUT = "INTEGER NEWLINE".split()
        self.parser.getToken()
        root = self.parser.Term()
        render_tree(root)

        self.parser.TOKEN_INPUT = "INTEGER MUL INTEGER MUL INTEGER MOD INTEGER NEWLINE".split()
        self.parser.getToken()
        root = self.parser.Term()
        render_tree(root)
        

    def TermPrime(self):
        #TermPrime ::=  ''
        self.parser.TOKEN_INPUT = "NEWLINE".split()
        self.parser.getToken()
        root = self.parser.TermPrime()
        print(">> == WORKS EMPTY == <<\n" + str(root == None)+"\n")

        # TermPrime ::= * Factor TermPrime 
        #self.parser.TOKEN_INPUT = "MUL ID NEWLINE".split()
        #self.parser.getToken()
        #root = self.parser.TermPrime()
        #render_tree(root)

        # TermPrime ::= * Factor TermPrime 
        self.parser.TOKEN_INPUT = "MUL ID LPAREN INTEGER COMMA INTEGER RPAREN NEWLINE".split()
        self.parser.getToken()
        root = self.parser.TermPrime()
        render_tree(root)

        # TermPrime ::= * Factor TermPrime 
        self.parser.TOKEN_INPUT = "MUL ID MOD ID NEWLINE".split()
        self.parser.getToken()
        root = self.parser.TermPrime()
        render_tree(root)
        '''EXPECTED OUTPUT
        First it needs to perform the mul then the mod
        MOD
        ├── MUL
        │   └── ID
        └── ID
        '''

        self.parser.TOKEN_INPUT = "MUL ID MOD ID DIV ID NEWLINE".split()
        self.parser.getToken()
        root = self.parser.TermPrime()
        render_tree(root)
        '''EXPECTED OUTPUT
        DIV
        ├── MOD
        │   ├── MUL
        │   │   └── ID
        │   └── ID
        └── ID
        '''

        self.parser.TOKEN_INPUT = "MUL ID MOD ID DIV ID MOD ID NEWLINE".split()
        self.parser.getToken()
        root = self.parser.TermPrime()
        render_tree(root)
        '''EXPECTED OUTPUT
        MOD
        ├── DIV
        │   ├── MOD
        │   │   ├── MUL
        │   │   │   └── ID
        │   │   └── ID
        │   └── ID
        └── ID
        '''

    def Factor(self):
        producciones = [
            "SUB INTEGER NEWLINE",
            "ID NEWLINE",
            "ID LPAREN INTEGER COMMA INTEGER RPAREN NEWLINE",
            "INTEGER NEWLINE",
            "LBRACKET INTEGER COMMA INTEGER RBRACKET NEWLINE",
            "LPAREN INTEGER RPAREN NEWLINE",
            "EQ"#error
        ]
        #Factor ::=  - Factor
        #Factor ::=  Name
        #Factor ::=  Literal
        #Factor ::=  List
        #Factor ::=  ( Expr )
        for p in producciones:
            self.parser.TOKEN_INPUT = p.split()
            self.parser.getToken()
            root = self.parser.Factor()
            render_tree(root)

    def Name(self):
        # Name ::= ID
        self.parser.TOKEN_INPUT = "ID NEWLINE".split()
        self.parser.getToken()
        root = self.parser.Name()
        render_tree(root)

        # Name ::= ID NameTail
        self.parser.TOKEN_INPUT = "ID LPAREN INTEGER COMMA INTEGER RPAREN".split()
        self.parser.getToken()
        root = self.parser.Name()
        render_tree(root)

        # Name ::= ID NameTail D:
        self.parser.TOKEN_INPUT = "LPAREN INTEGER COMMA INTEGER RPAREN".split()
        self.parser.getToken()
        root = self.parser.Name()
        render_tree(root)

    def NameTail(self):
        #NameTail ::=  ''
        self.parser.TOKEN_INPUT = "NEWLINE".split()
        self.parser.getToken()
        root = self.parser.NameTail()
        print(">> == WORKS EMPTY == <<\n" + str(root == None)+"\n")

        #NameTail ::=  ( Expr )
        self.parser.TOKEN_INPUT = "LPAREN INTEGER COMMA INTEGER RPAREN".split()
        self.parser.getToken()
        root = self.parser.NameTail()
        render_tree(root)

        #NameTail ::=  List
        self.parser.TOKEN_INPUT = "LBRACKET INTEGER COMMA INTEGER RBRACKET".split()
        self.parser.getToken()
        root = self.parser.NameTail()
        render_tree(root)

        #NameTail ::=  [ List D:
        self.parser.TOKEN_INPUT = "LBRACKET LBRACKET INTEGER COMMA INTEGER RBRACKET".split()
        self.parser.getToken()
        root = self.parser.NameTail()
        render_tree(root)

    def Literal(self):
        self.parser.TOKEN_INPUT = ["INTEGER"]
        self.parser.getToken()
        root = self.parser.Literal()
        render_tree(root)

        self.parser.TOKEN_INPUT = ["ERROR"]
        self.parser.getToken()
        root = self.parser.Literal()
        render_tree(root)

    def List(self):
        #List ::=  [ ExprList ]
        self.parser.TOKEN_INPUT = "LBRACKET INTEGER COMMA INTEGER RBRACKET".split()
        self.parser.getToken()
        root = self.parser.List()
        render_tree(root)

        #List ::=  ? D:
        self.parser.TOKEN_INPUT = "INT".split()
        self.parser.getToken()
        root = self.parser.List()
        render_tree(root)

        #List ::=  ] D:
        self.parser.TOKEN_INPUT = "RBRACKET".split()
        self.parser.getToken()
        root = self.parser.List()
        render_tree(root)

    def ExprList(self):
        #ExprList  ::=  ''
        self.parser.TOKEN_INPUT = "RPAREN".split()
        self.parser.getToken()
        root = self.parser.ExprList ()
        print(">> == WORKS EMPTY == <<\n" + str(root == None)+"\n")

        #ExprList ::=  Expr
        self.parser.TOKEN_INPUT = "INTEGER RPAREN".split()
        self.parser.getToken()
        root = self.parser.ExprList()
        render_tree(root)

        #ExprList ::=  Expr ExprListTail
        self.parser.TOKEN_INPUT = "INTEGER COMMA INTEGER RPAREN".split()
        self.parser.getToken()
        root = self.parser.ExprList()
        render_tree(root)

        #ExprList ::=  Expr ExprListTail
        self.parser.TOKEN_INPUT = "INTEGER COMMA INTEGER COMMA INTEGER RPAREN".split()
        self.parser.getToken()
        root = self.parser.ExprList()
        render_tree(root)

        #ExprList ::=  Expr ExprListTail
        self.parser.TOKEN_INPUT = "INTEGER COMMA INTEGER INTEGER RPAREN".split()
        self.parser.getToken()
        root = self.parser.ExprList()
        render_tree(root)

    def ExprListTail(self):#No funciona
        #ExprListTail ::=  ''
        self.parser.TOKEN_INPUT = "RPAREN".split()
        self.parser.getToken()
        root = self.parser.ExprListTail()
        print(">> == WORKS EMPTY == <<\n" + str(root == None)+"\n")

        #ExprListTail ::=  , Expr ExprListTail
        self.parser.TOKEN_INPUT = "COMMA INTEGER RPAREN".split()
        self.parser.getToken()
        root = self.parser.ExprListTail()
        render_tree(root)

        #ExprListTail ::=  , Expr ExprListTail
        self.parser.TOKEN_INPUT = "COMMA INTEGER COMMA INTEGER RPAREN".split()
        self.parser.getToken()
        root = self.parser.ExprListTail()
        render_tree(root)

    def CompOp(self):
        self.parser.TOKEN_INPUT = "EQ".split()
        self.parser.getToken()
        root = self.parser.CompOp()
        render_tree(root)

        #ERROR
        self.parser.TOKEN_INPUT = "ERROR".split()
        self.parser.getToken()
        root = self.parser.CompOp()
        render_tree(root)


testTree = TestTree()
#testTree.TermPrime()
testTree.Term()
#testTree.DefList()