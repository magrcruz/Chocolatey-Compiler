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

def derivar():
    global production
    idx = 0

    while idx<len(production):
        if production[idx] in Nonterminal:#Se puede remplazar
            status = ""
            if idx>0: status+= Fore.BLUE + ' '.join(production[:idx]) + " " #lo ya parseado
            status+= Fore.RED + production[idx] +" " #Simbolo a reemplazar
            status+= Fore.GREEN + ' '.join(production[idx+1:]) # lo que aun falta reemplazar
            print(status)
            for ridx, rule in enumerate(rules[production[idx]]):
                if rule !="": print(Fore.BLUE + str(ridx), Fore.WHITE + ": ", ' '.join(rule))
                else: print(Fore.BLUE + str(ridx), Fore.WHITE + ": ", "''")

            seleccion = input("Ingrese regla a utilizar ")

            # Insertar todos los elementos de lista2 en lista1 en el índice especificado
            production[idx:idx+1] = rules[production[idx]][int(seleccion)]

            print("PRODUCCION "+Fore.WHITE + ' '.join(production))
        else:
            idx+=1

    archivo = open("output.txt","+a")
    archivo.write("\n"+' '.join(production))

def genTestProduction():
    global production
    p = input("Escribe la produccion a derivar: ")
    production = [p]
    derivar()

genTestProduction()