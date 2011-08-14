# coding: utf-8

class Type(object):
    pass

class BaseType(Type):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return str(self.name)

IntType = BaseType("Integer")
BoolType = BaseType("Boolean")
VoidType = BaseType("Void")
