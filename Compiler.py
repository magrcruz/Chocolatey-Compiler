global foundedToken
global foundedError

from Scanner import *
import Parser
from utils.Error import *

class Compiler:
    def __init__(self) :
        global foundedToken
        global foundedError
        foundedToken = False
        foundedError = False
        self.scanner = Scanner()
        self.parser = Parser.Parser(self.scanner)

    def begin(self, archivo):
        self.scanner.begin(archivo)
        self.parser.S()
        #self.showErrors()

    def showErrors(self):
        print("INFO SCAN - Completed with %i errors" % (len(self.scanner.errores)))
        for i in self.scanner.errores:
            print("Error:  %s " % i)

        print("INFO PARSER - Completed with %i errors" % (len(self.parser.error_list)))
        for i in self.parser.error_list:
            print("Error:  %s " % i)

compiler = Compiler()
compiler.begin("file.txt")
