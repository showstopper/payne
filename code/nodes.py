#coding: utf-8

import errors
from mytypes import BoolType, IntType, VoidType
from opcodes import comparison_symbols, math_symbols

class Statement(object):

    def resolve(self, module):
        pass

class FunctionDecl(Statement):

    def __init__(self, ident, args, body, token):
        self.ident = ident
        self.args = args
        self.body = body
        self.token = token
        self.table = {} #ident-mapping


    def resolve(self, module):
        module.table.push(self.table) # introduce new local scope
        if str(self.ident) in module.table or str(self.ident) in module.functions:
            msg = "FUNCDECL: Redefinition of %s" % (str(self.ident))
            raise errors.FunctionDeclException(msg)

        module.functions[str(self.ident)] = self
        for ident in self.args:
            """
            Prinzipiell ist die Sprache statisch typisiert, jedoch
            ohne explizite Typ-Notationen. Deshalb werden der 
            Einfachheit halber nur Integers als Argumente zugelassen.
            Ohne diese Einschraenkung muesste anhand der an den Call
            uebergebenen Argumente der Typ bestimmt oder explizite Type-Notationen
            eingefuehrt werden. Ebenso koennen auch nur Integer zurueckgegeben
            werden.
            """
            dummy = Expression()
            dummy.type_ = IntType
            self.table[str(ident)] = dummy 

        got_return = False
        for subnode in self.body:
            subnode.resolve(module)
            if isinstance(subnode, ReturnStatement):
                got_return = True

        if not got_return:
            # Adding a default return
            ret = ReturnStatement(Integer(0)) # 'None' might help as default
            ret.resolve(module)
            self.body.append(ret)
        module.table.pop() # back to next-higher scope

class PrintStatement(Statement):

    def __init__(self, expr, token):
        self.expr = expr
        self.token = token

    def __repr__(self):
        return "PRINT: %s" % (str(expr))

    def resolve(self, module):
        self.expr.resolve(module)

class IfStatement(Statement):

    def __init__(self, expr, body, token):
        self.expr = expr
        self.body = body
        self.token = token

    def __repr__(self):
        return "IF: %s" % (str(expr))

    def resolve(self, module):
        self.expr.resolve(module)
        for node in self.body:
            node.resolve(module)

class WhileStatement(Statement):

    def __init__(self, expr, body, token):
        self.expr = expr
        self.body = body
        self.token = token
    
    def __repr__(self):
        return "WHILE: %s" % (str(self.expr))

    def resolve(self, module):
        self.expr.resolve(module)
        for node in self.body:
            node.resolve(module)

class ReturnStatement(Statement):

    def __init__(self, expr, token):
        self.expr = expr

    def __repr__(self):
        return "RETURN: %s" % (str(self.expr))

    def resolve(self, module):
        self.expr.resolve(module)

class Expression(Statement):

    type_ = VoidType # Each expression has got a type
    token = None
    def resolve(self, module):
        pass
    
class FunctionCall(Expression):

    def __init__(self, ident, args, token):
        self.ident = ident
        self.args = args
        self.type_ = IntType
        self.token = token

    def resolve(self, module):
        if not str(self.ident) in module.functions:
            msg = "Call to a (yet?) undefined function: %s" % str(self.ident) 
            raise errors.FunctionCallException(msg)
        expected_args = len(module.functions[str(self.ident)].args)
        if not len(self.args) == expected_args:
            msg = "%s: Expected %s arguments, got %s" % (str(self.ident),
                                                         str(len(self.args)),
                                                         str(expected_args))
            raise errors.ArgumentException(msg)

class Identifier(Expression):
    
    def __init__(self, name, token):
        self.name = name
        self.decl = None

    def __repr__(self):
        return self.name

    def resolve(self, module):
        if not self.name in module:
            msg = "Reference before declaration: %s" % str(self)
            raise errors.VarAccException(msg)

        self.decl = module.table[self.name]
        self.type_ = self.decl.type_

class Integer(Expression):

    def __init__(self, val, token):
        self.val = val
        self.type_ = IntType
        self.token = token

    def __repr__(self):
        return str(self.val)

class Boolean(Expression):

    def __init__(self, val, token):
        self.val = val
        self.type_ = BoolType
        self.token = token

    def __repr__(self):
        return str(self.val)

class Declaration(Expression):
    pass

class VarDecl(Declaration):

    def __init__(self, left, right, token):
        self.left = left
        self.right = right
        self.token = token

    def __repr__(self):
        return "VARDECL: %s = %s" % (str(self.left), str(self.right))

    def resolve(self, module):
        self.right.resolve(module)
        module.table[str(self.left)] = self.right 
        self.type_ = self.right.type_

class BinaryOp(Expression):

    def __init__(self, left, op, right, token):
        self.left = left
        self.op = op
        self.right = right 
        self.token = token

    def __repr__(self):
        return "BINOP: %s %s %s" % (str(self.left), 
                                    str(self.op), 
                                    str(self.right))

    def _create_error_message(self):
        return "%s=> Invalid types: (%s & %s) " % (self.token.buf,
                                    str(self.left.type_),
                                    str(self.right.type_))
    def resolve(self, module):
        self.left.resolve(module)
        self.right.resolve(module)
        l_type = self.left.type_
        r_type = self.right.type_
        if not l_type == r_type:
            raise errors.InvalidTypesException(self._create_error_message())
        if self.op in comparison_symbols:
            self.type_ = BoolType
        elif self.op in math_symbols:
            if not l_type == IntType: # no sense in adding two booleans
                raise errors.InvalidTypesException(self._create_error_message())
            self.type_ = IntType
        
