# coding: utf-8

import nodes as nod
from collections import namedtuple
from scope import Scope
from dparser import Parser
import errors

class Module(object):

    def __init__(self, ast):
        self.ast = ast
        self.table = Scope() 
        self.functions = {} # mapping of the functions

    def __contains__(self, ident):
        for table in self.table.table:
            if ident in table:
                return True
        return ident in self.functions 
    
KEYWORDS = ["def", "if", "while"]

def parse(program):
    parser = Parser(file_prefix='.d_parser_assign')
    # ohne die ambiguity function gibt es einen segfault
    return Module(parser.parse(program, ambiguity_fn=lambda a: None).structure) 

def d_program(t, nodes, this):
    ''' program: statement* '''
    return t[0]

def d_statement(t, nodes, this):
    ''' statement: simple_statement
                 | function_decl
    '''
    return t[0]

def d_function_decl(t, nodes, this):
    ''' function_decl: 'def' ident param_body ":\n" simple_statement* "end" '''
    return nod.FunctionDecl(t[1], t[2], t[4], this)

def d_param_body(t, nodes, this):
    """ param_body: '(' parameters? ')' """
    if t[1]:
        return t[1][0]
    else:
        return []

def d_parameters(t, nodes, this):
    ''' parameters: ident (',' ident)* '''
    return [t[0]] + map(lambda x: x[1], t[1])

def d_simple_statement(t, nodes, this):

    ''' simple_statement: printstmt
                 | ifstmt
                 | whilestmt
                 | expression 
                 | returnstmt ''' # BOESE ohne function => Runtime-error
    return t[0]


def d_returnstmt(t, nodes, this):
    ''' returnstmt: 'return' expression '''
    return nod.ReturnStatement(t[1], this)

def d_printstmt(t, nodes, this):
    ''' printstmt: 'print' expression '''
    return nod.PrintStatement(t[1], this)

def d_ifstmt(t, nodes, this):
    ''' ifstmt: "if" expression ":\n" simple_statement* "end" '''
    return nod.IfStatement(t[1], t[3], this)

def d_whilestmt(t, nodes, this):
    ''' whilestmt: "while" expression ":\n" simple_statement* "end" '''
    return nod.WhileStatement(t[1], t[3], this)

def d_expression(t, nodes, this):
    ''' expression: 
                  | mathexpr 
                  | declaration '''
    return t[0]

def d_declaration(t, nodes, this):
    ''' declaration: vardecl '''
    return t[0]

def d_vardecl(t, nodes, this):
    ''' vardecl: ident '=' expression '''
    return nod.VarDecl(t[0], t[2], this)

def d_mathexpr(t, nodes, this):
    ''' mathexpr: term
                | expression addop term '''
    if len(t) == 3:
        return nod.BinaryOp(t[0], t[1], t[2], this)
    return t[0]

def d_term(t, nodes, this):
    ''' term: atom
            | term mulop atom 
            | term cmpop atom ''' # comparison

    if len(t) == 3:
        return nod.BinaryOp(t[0], t[1], t[2], this)
    return t[0]

def d_atom(t, nodes, this):
    ''' atom: number
              | '(' expression ')' 
              | boolean 
              | ident 
              | function_call
              '''

    if len(t) == 3: # geklammerter Ausdruck
        return t[1]  
    return t[0]

def d_function_call(t, nodes, this):
    ''' function_call: ident call_body '''
    return nod.FunctionCall(t[0], t[1], this)

def d_call_body(t, nodes, this):
    """ call_body: '(' arguments? ')' """
    if t[1]:
        return t[1][0]
    else:
        return []

def d_arguments(t, nodes, this):
    ''' arguments: expression (',' expression)* '''
    return [t[0]] + map(lambda x: x[1], t[1])

def d_number(t, nodes, this):
    ''' number: "[0-9]+" '''
    return nod.Integer(int(t[0]), this)

def d_boolean(t, nodes, this):
    ''' boolean: "True" | "False" '''
    return nod.Boolean(t[0], this)

def d_addop(t, nodes, this):
    ''' addop: '+' | '-' '''
    return t[0]

def d_mulop(t, nodes, this):
    ''' mulop: '*' | '/' '''
    return t[0]

def d_cmpop(t, nodes, this):
    ''' cmpop: '>' | '==' | '<' '''
    return t[0]

def d_ident(t, nodes, this):
    ''' ident: "[a-zA-Z_][a-zA-Z0-9_]*" '''
    if t[0] in KEYWORDS:
        msg = "Invalid use of reserved keyword: %s" % (this.buf)
        raise errors.KeywordException(msg)
    return nod.Identifier(t[0], this)



