from anytree import Node
class Place:
    def __init__(self):
        self._nodo = None

    def start(self, p = None):
        self._nodo = Node("TO FILL", parent=p)

    @property
    def nodo(self): return self._nodo
    @property
    def parent(self): return self._nodo.parent
    @property
    def name(self): return self._nodo.name
    @property
    def empty(self): return self._nodo == None

    def saveNodo(self,newNodo):
        self._nodo = newNodo
        
    def copyNodo(self,newNodo):
        if self._nodo == None:
            self._nodo = newNodo
        else:
            self._nodo.name = newNodo.name
            for _,c in enumerate(newNodo.children):
                c.parent = self._nodo

    @parent.setter
    def parent(self,_parent):
        self._nodo.parent = _parent
