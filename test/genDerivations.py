import colorama
from colorama import Fore, Back, Style

Nonterminal = ['S', 'Program', 'DefList', 'Def', 'TypedVar', 'Type', 'TypedVarList', 'TypedVarListTail', 'Return', 'Block', 'StatementList', 'Statement', 'ElifList', 'Elif', 'Else', 'SimpleStatement', 'SSTail', 'ReturnExpr', 'Expr', 'ExprPrime', 'orExpr', 'orExprPrime', 'andExpr', 'andExprPrime', 'notExpr', 'notExprPrime', 'CompExpr', 'CompExprPrime', 'IntExpr', 'IntExprPrime', 'Term', 'TermPrime', 'Factor', 'Name', 'NameTail', 'Literal', 'List', 'ExprList', 'ExprListTail', 'CompOp']

rules = {}
def getRules():
    with open("test/grammar.txt") as file:
        for linea in file:
            nt,produccion = linea.split(" ::= ")
            if produccion == "''\n":
                produccion = ""
            else:
                produccion = produccion[:-1].split(" ")
            #print(nt," ::= ",produccion)
            if nt not in rules:
                rules[nt]=[produccion]
            else:
                rules[nt].append(produccion)
getRules()
global production
production = ['S']

def printOptions(idx):
    global production
    nullable = False
    for ridx, rule in enumerate(rules[production[idx]]):
        if rule !="":
            print(Fore.BLUE + str(ridx), Fore.WHITE + ": ", ' '.join(rule))
        else:
            print(Fore.BLUE + str(ridx), Fore.WHITE + ": ", "''")
            nullable = True
    if nullable:
        print(Fore.BLUE + str(len(rules[production[idx]])), Fore.WHITE + ": FILL WITH EMPTY")


def derivar():
    global production
    idx = 0
    file = open("saveSelections.txt", 'w')
    while idx<len(production):
        if production[idx] in Nonterminal:#Se puede remplazar
            if len(rules[production[idx]])==1:#si solo hay una opcion para seguir la escoge
                production[idx:idx+1] = rules[production[idx]][0]
            else:
                status = ""
                if idx>0: status+= Fore.BLUE + ' '.join(production[:idx]) + " " #lo ya parseado
                status+= Fore.RED + production[idx] +" " #Simbolo a reemplazar
                status+= Fore.GREEN + ' '.join(production[idx+1:]) # lo que aun falta reemplazar
                print(status)

                printOptions(idx)

                seleccion = int(input("Ingrese regla a utilizar "))
                file.write(str(seleccion)+"\n")

                unalen = len(rules[production[idx]])
                print(seleccion == unalen)
                if seleccion == len(rules[production[idx]]):#Llena de vacios todo lo q puede
                    #Mientras pueda ser vacio escoge vacio
                    n = int(input("Ingrese cuantas producciones desea saltar"))
                    file.write(str(n)+"\n")
                    while idx<len(production) and production[idx] in Nonterminal and '' in rules[production[idx]] and n:
                        del production[idx]
                        n-=1
                else:
                    # Insertar todos los elementos de lista2 en lista1 en el índice especificado
                    production[idx:idx+1] = rules[production[idx]][seleccion]

            print("PRODUCCION ::= "+Fore.WHITE + ' '.join(production))
        else:
            idx+=1

    archivo = open("output.txt","+a")
    archivo.write("\n"+' '.join(production))

def genID():
    genID.idx += 1
    return 'ID_%03d ' % genID.idx
genID.idx = 0

def genSTRING():
    genSTRING.idx += 1
    return 'STR_%03d ' % genSTRING.idx
genSTRING.idx = 0

def genIDENT():
    genIDENT.idx += 1
    #return " "*4
    return None
genIDENT.idx = 0

def genDEDENT():
    genIDENT.idx -= 1
    return None

def genNEWLINE():
    genNEWLINE.pending = True
    return None
    #return "\n" + " "*(genIDENT.idx*4)
genNEWLINE.pending = False

def genINTEGER():
    genINTEGER.idx += 1
    return str(genINTEGER.idx)
genINTEGER.idx = 0

def genEOF():
    return None

translateMap = {
    "ID":genID,
    "STRING":genSTRING,
    "NEWLINE": genNEWLINE,
    "INTEGER":genINTEGER,
    "EOF":genEOF,
}

def productionToCode(produccion, path):
    genID.idx = 0
    with open(path, 'w') as file:
        for p in produccion:
            if genNEWLINE.pending:
                if p == "DEDENT": genDEDENT()# Primero hace el dedent
                elif p == "INDENT": genIDENT()
                genNEWLINE.pending = False
                file.write("\n" + " "*(genIDENT.idx*4))
            if p in translateMap:
                traduction = translateMap[p]()
                if traduction!=None:
                    file.write(traduction)
            elif p == "DEDENT" or p=="INDENT":
                continue
            else: file.write(p + " ")

def genTestProduction():
    global production
    p = input("Escribe la produccion a derivar: ")
    production = [p]
    derivar()


#genTestProduction()
#productionToCode(production, "newfile2.txt")
productionToCode("def ID ( ID : int ) -> int : NEWLINE INDENT pass NEWLINE return ID * ID  + False or ID if True // ( ID )  else ID NEWLINE DEDENT  if INTEGER : NEWLINE INDENT pass NEWLINE ID * INTEGER // INTEGER   = ID NEWLINE while [ INTEGER + ID , ID - ID ] % STRING  : NEWLINE INDENT ID = INTEGER <=  - STRING NEWLINE DEDENT DEDENT elif INTEGER >  INTEGER : NEWLINE INDENT pass NEWLINE DEDENT elif INTEGER not False : NEWLINE INDENT for ID in ID : NEWLINE INDENT ( True and [ ID ] or ID ) NEWLINE DEDENT DEDENT else : NEWLINE INDENT pass NEWLINE DEDENT EOF".split(),"newfile2.txt")