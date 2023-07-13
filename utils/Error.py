class Error:
    def __init__(self, _error_type, _description, _row):
        global foundedError #check twice

        self.error_type = _error_type
        self.descripcion = _description
        self.row = _row
        foundedError = True

    def __repr__(self):
        return "%s : %s  en la linea %i" % (self.error_type, self.descripcion, self.row)

