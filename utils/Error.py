class Error:
    def __init__(self, _error_type, _description, _row, _col = None):
        global foundedError #check twice

        self.error_type = _error_type
        self.descripcion = _description
        self.row = _row
        self.col = _col
        foundedError = True

    def __repr__(self):
        if self.col != None:
            return "%s : %s  at (%i,%i)" % (self.error_type, self.descripcion, self.row, self.col)
        return "%s : %s at (%i)" % (self.error_type, self.descripcion, self.row)

