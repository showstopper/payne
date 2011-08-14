# coding: utf-8

"""
blah
"""
class ArgumentException(Exception):
    pass

class KeywordException(Exception):
    pass

class InvalidOpcodeException(Exception):
    pass

class InvalidOperandException(Exception):
    pass

class EmptyStackException(Exception):
    pass

class VarAccException(Exception):
    pass

class FunctionDeclException(Exception):
    pass

class FunctionCallException(Exception):
    pass

class InvalidTypesException(Exception):
    pass
