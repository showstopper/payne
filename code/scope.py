#coding: utf-8

class Scope(object):

    def __init__(self):
        self.table = [{}]

    def push(self, table):
        self.table.append(table)

    def pop(self):
        self.table.pop()

    def __getitem__(self, ident):
        for table in reversed(self.table):
            if ident in table:
                return table[ident]
        msg = "Couldn't find %s." % (str(ident))
        raise KeyError(msg)

    def __setitem__(self, ident, node):
        # "top-level" table, also der lokalste Scope
        self.table[-1][ident] = node

    def __contains__(self, ident):
        for table in self.table:
            if ident in table:
                return True
        return False


    
