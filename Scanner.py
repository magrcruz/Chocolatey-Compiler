global foundedToken
global foundedError

from utils.ReservedWords import *
from utils.Error import *

foundedToken = False
foundedError = False

class Token:
    def __init__(self, _type, _value, _row, _col):
        global foundedToken
        self.type = "" + _type
        self.value = _value
        self.row = _row
        self.col = _col
        foundedToken = True
        if _type == "NEWLINE":
            foundedToken = False

    def __repr__(self):
        tam1 = len(self.type)
        espacio = ""
        while tam1 < 8:
            espacio += " "
            tam1 += 1
        #return "%s [ %s ] at (%i:%i)" % (self.type,self.value,self.row, self.col-len(str(self.value))+1*(len(str(self.value))>0))
        return "%s%s [ %s ] at (%i:%i)" % (self.type,espacio,self.value,self.row, self.col)

    def __eq__(self, other):
        return self.type == other
class Scanner:
    # Hacer cada funcionalidad en una funcion diferente valga la redundancia
    def __init__(self):
        global foundedToken
        foundedToken = False

        self.archivo = None
        self.buffer = ""
        self.tokens = []
        self.errores = []

        self.pos = [1, 0]  # Revisar, se podria usar alguna estructura
        self.current_char = ""
        self.lexeme = ""
        self.ident = 0

        self.espacesNeededToTab=4

        # Aux
        self.firstOfDblOper = []
        self.getFirstOfDblOper()

    def createError(self,errorType, errorDescription):
        global foundedError
        foundedError = True
        return Error(errorType,errorDescription, self.pos[0])

    def begin(self, file):
        try:
            self.archivo = file
            with open(file,'r') as archivo:
                self.buffer = archivo.read() + "\n$"
                archivo.close()
        except FileNotFoundError:
            self.buffer = "$"
            print("Hubo problemas para encontrar el archivo")
            self.archivo = None

        self.errores = []

    def beginText(self,text):
        self.buffer = text+ "\n$"
        self.errores = []

    def getFirstOfDblOper(self):
        # Funcion que extrae los primeros caracteres de los operadores dobles
        for op in OPER_DELIMITERS_2:
            self.firstOfDblOper.append(op[0])

    def getchar(self):  # Se actualiza current_char
        if len(self.buffer) == 0:
            self.current_char = "$"
        else:
            self.pos[1] += 1
            # Obtiene el primer caracter y lo pone en self current char
            self.current_char = self.buffer[0]
            self.buffer = self.buffer[1:]

    def peekchar(self):
        if len(self.buffer) == 0:
            return None
        return self.buffer[0]

    def ignoreComents(self):
        c = self.pos[1]
        if self.current_char == "#":
            while self.peekchar() != "\n" and self.peekchar() != "$":
                self.getchar()
            self.pos[1] = c

    def getIdentifier(self):
        # Consume todos los caracteres dentro de la expresion [a-z|A-Z][a-z|A-Z|0-9|_]*
        self.lexeme = self.current_char
        c = self.peekchar()
        while c.isalpha() or c.isdigit() or c == "_":
            self.getchar()
            self.lexeme += self.current_char
            c = self.peekchar()

    def getNumber(self):
        # Consume todos los caracteres dentro de la expresion [0]|[[1-9][0-9]]*
        self.lexeme = self.current_char
        c = self.peekchar()
        while c.isdigit():
            self.getchar()
            self.lexeme += self.current_char
            c = self.peekchar()
        if len(self.lexeme) > 1 and self.lexeme[0] == "0":
            return False, self.createError("Numero invalido", "El numero no puede tener un 0 a la izquierda")
        if len(self.lexeme) == 10:
            if int(self.lexeme[:9]) == 214748364:
                if int(self.lexeme[9]) > 7:
                    return False, self.createError("Numero invalido", "EL numero es muy grande")
            elif int(self.lexeme[:9]) > 214748364:
                return False, self.createError("Numero invalido", "EL numero es muy grande")
        elif len(self.lexeme) > 10:
            return False, self.createError("Numero invalido", "EL numero es muy grande")
        return True, Token("INTEGER", self.lexeme, self.pos[0], self.pos[1])

    def getTknOper(self):
        self.lexeme = self.current_char
        if self.current_char in self.firstOfDblOper:
            c = self.peekchar()
            oper = self.lexeme + c
            if oper in OPER_DELIMITERS_2:
                self.getchar()
                self.lexeme = oper
                return Token(OPER_DELIMITERS_2[oper], oper, self.pos[0], self.pos[1])
        return Token( OPER_DELIMITERS[self.lexeme], self.lexeme, self.pos[0], self.pos[1] )

    def getTknNEWLINE(self):
        global foundedToken
        foundedToken = False
        token = Token("NEWLINE", " ", self.pos[0],self.pos[1])
        self.pos[0] += 1
        self.pos[1] = 0
        return token

    def isEmptyLine(self):  # Devuelve hasta donde hay que saltar en el buffer
        index = 0
        while self.buffer[index] != "\n":
            if self.buffer[index] == " " or self.buffer[index] == "\t":
                index += 1
            elif self.buffer[index] == "#":
                while index < len(self.buffer) and self.buffer[index] != "\n" and self.buffer[index] != "$":
                    index += 1
                return index
            else:
                return -1 # La linea no esta vacia
        return index

    def ignoreEmptyLine(self):
        global foundedToken
        index = self.isEmptyLine()
        if index != -1 and not foundedToken:
            foundedToken = False
            self.buffer = self.buffer[index + 1 :] # Salta la linea vacia
            self.pos[0] += 1
            self.pos[1] = 0
            return True #Ignoro una linea vacia y pueden venir mas despues
        return False

    def ignoreUselessChars(self): # Ignora espacios
        c = self.peekchar()
        while c == " " or c == "\t" or c == "#":
            if c != "#": self.getchar()
            else:
              self.getchar()
              self.ignoreComents()
            c = self.peekchar()
        index = self.isEmptyLine()

    def getTknEOF(self):
        return Token("EOF", "EOF", self.pos[0], self.pos[1])


    def getIdentation(self):# Esta al inicio de la linea y hay identacion
        global foundedToken

        if not foundedToken: #Esta al inicio de la linea
            tabs = 0
            espacios = 0
            if self.current_char == " ": espacios+=1
            elif self.current_char == "\t":tabs+=1

            while self.current_char in [" ","\t"] and self.peekchar() == " " or self.peekchar()  == "\t":
                self.getchar()
                if self.current_char == " ":
                    espacios += 1
                    if espacios == 4:
                        espacios = 0
                        tabs += 1
                elif espacios: # La identacion no esta completa y vino un tab
                    espacios = 0
                    self.errores.append(self.createError("IDENT", "Error de identacion"))
                else:
                    tabs += 1

            if espacios == 4:
                espacios = 0
                tabs += 1

            if espacios: # Quedaron espacios sueltos
                self.errores.append(self.createError("IDENT", "Error de identacion"))
            dif = tabs - self.ident               #     Bug de dedentación

            if tabs or dif != 0:                          #     Bug de dedentación
                if dif > 0:
                    self.ident = tabs
                    return Token("IDENT", dif, self.pos[0], self.pos[1])
                elif dif < 0:
                    self.ident = tabs
                    self.buffer = self.current_char + self.buffer
                    return Token("DEDENT", -dif, self.pos[0], self.pos[1])
                elif tabs:
                    return Token("IDENT",-1,0,0) #Hay identacion pero no es nueva
        return None

    def getToken(self):  # (tokentype, tokenval)
        global foundedToken
        global foundedError

        foundedError = True

        while foundedError:
            foundedError = False
            self.lexeme = ""
            token = None

            if self.current_char!= "\n":
                self.current_char = None

            if len(self.buffer) == 0: return self.getTknEOF()

            while self.ignoreEmptyLine():
                continue

            if foundedToken: #Significa que no esta al inicio de la linea
                self.ignoreUselessChars()
            self.getchar()

            if self.current_char == "\n" and foundedToken:
                return self.getTknNEWLINE()

            # IDENTATION
            token = self.getIdentation()
            if token and token.value > 0:
                return token
            elif token and token.value < 0: # Si habia identacion pero no es nueva
                token = None
                self.getchar()

            # Esta buscando un id o una palabra reservada
            if self.current_char.isalpha():
                self.getIdentifier()
                if self.lexeme in KEYWORDS:
                    token = Token( KEYWORDS[self.lexeme], self.lexeme, self.pos[0], self.pos[1] )
                else:
                    token = Token( "ID", self.lexeme, self.pos[0], self.pos[1] )

            # Esta buscando un numero
            elif self.current_char.isdigit():
                isNumber, result = self.getNumber()
                if isNumber: token = result
                else: self.errores.append( result )

            # Buscar operadores
            elif self.current_char in OPER_DELIMITERS or self.current_char in self.firstOfDblOper:
                token = self.getTknOper()

            elif self.current_char == '"':
                self.getchar()
                lex = ""
                while self.current_char != '"':
                    if self.current_char == "\n":
                        self.errores.append( self.createError("String error",  "la string no se a cerrado"))
                        break
                    try:
                        int_val = ord(self.current_char)
                        if int_val > 180 or int_val < 32:
                            self.errores.append( self.createError("String error",  "\"" + self.current_char +  "\" fuera de rango"))
                    except Exception as e:
                        print('Error:', e)
                    if self.current_char == "\\":
                        self.getchar()
                        if self.current_char != "\"":
                            self.errores.append( self.createError("String error",  "\"\\" + self.current_char + "\" not recognized"))

                    lex += self.current_char
                    self.getchar()
                token =  Token("STRING", lex, self.pos[0], self.pos[1])

            elif len(self.buffer) == 0:
                return self.getTknEOF()

            elif self.current_char:
                self.errores.append( self.createError("Symbol error",  "el simbolo es invalido"))
                foundedError = True

        return token

    def debug(self):
        print("INFO SCAN - Start scanning...")
        while len(self.buffer):
            token = self.getToken()
            self.tokens.append(token)
            print("DEBUG SCAN - %s " % (token))
        print("INFO SCAN - Completed with %i errors" % (len(self.errores)))
        for i in self.errores:
            print("Error:  %s " % i)
