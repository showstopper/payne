# coding: utf-8

"""
Dieses Modul enthält die Logik zur Übersetzung des AST in Assembler.
"""

import cStringIO
from nodes import Integer, BinaryOp, VarDecl
from opcodes import math_symbols, comparison_symbols
from visitor import Visitor
from writer import Writer
from utils import newline

FILENAME = "out.xx"

class Marker(object):
    """
    Ein Dummy für eine Addresse, zu der aktiv hingesprungen werden soll,
    beispielsweise ein Funktionsaufruf.
    """
    def __init__(self, label):
        self.label = label

class Label(object):

    """
    Gibt eine Zieladdresse an, die von Marker dereferenziert werden kann.
    """
    def __init__(self, label):
        self.label = label

class Compiler(Visitor):

    """
    Die Hauptklasse zur Übersetzung.
    """
    def __init__(self, module):
        self.module = module
        self.buf = Writer() # modul-ebene

        self.function_buf = Writer() # funktionen kommen seperat
        self.label_count = 0

        self.jump_table = {} # offsets der funktionen

    def _gen_label(self):
        """
        Erstellt ein einzigartiges Lebel nach dem Muster "Lx", wobei "x"
        eine beliebige Integerzahl ist.
        """
        self.label_count += 1
        return "".join(("L", str(self.label_count)))

    def compile(self):
        """
        Diese Funktion ist die einzige, die direkt von außerhalb aufgerufen wird.
        Sie steuert den Prozess der Übersetzung.
        """
        for node in self.module.ast:
            node.resolve(self.module)
            self.visit(node)
        self.buf.append("EOF") # ende des globalen scopes
        self.buf.append(self.function_buf) # func-decls kommen ans ende des moduls 
        self.buf.write(FILENAME) # Just for fun file writing
        return str(self.buf)
    
    def visit_FunctionDecl(self, node):
        """
        Während der Übersetzung der Funktion wird ein temporäres Writer-Objekt
        zum neuen Buffer, in den der Bytecode geschrieben wird. Dadurch 
        werden unnötige Sprünge vermieden.
        """
        backup = self.buf
        self.buf = self.function_buf
        func_label = self._gen_label()
        self.buf.append(Label(func_label))
        self.jump_table[str(node.ident)] = func_label 
        for arg in node.args:
            self.buf.append("STORE")
            self.buf.append(str(arg))
        for subnode in node.body:
            self.visit(subnode)

        self.buf = backup

    def visit_FunctionCall(self, node):
        """
        Übersetzt einen Funktionsaufruf.
        """
        for arg in reversed(node.args):
            self.visit(arg) 
        self.buf.append("PUSH_SCOPE") # Scope der Funktion

        jump_back_label = self._gen_label()

        self.buf.append("PUSH_ADDRESS") # Ruecksprung
        self.buf.append(Marker(jump_back_label))


        self.buf.append("JUMP") # Aufruf, func-offset
        self.buf.append(Label(jump_back_label)) # ruecksprung-label
        self.buf.append(Marker(self.jump_table[str(node.ident)]))


    def visit_ReturnStatement(self, node):
        """
        Übersetzt eine Return-Anweisung.
        """
        self.visit(node.expr)
        self.buf.append("POP_SCOPE")
        self.buf.append("RET")
        
    def visit_BinaryOp(self, node):
        """
        Übersetzt einen binären Ausdruck, wie beispielsweise "2 + 2".
        """
        self.visit(node.right)
        self.visit(node.left)
        if node.op in math_symbols:
            operator = math_symbols[node.op]
        elif node.op in comparison_symbols:
            operator = comparison_symbols[node.op]
        self.buf.append(operator)

    def _load_const(self, node):
        self.buf.append("LOAD_CONST")
        self.buf.append(str(node.val))

    def visit_Integer(self, node):
        self._load_const(node)

    def visit_Boolean(self, node):
        self._load_const(node)

    def visit_VarDecl(self, node):
        """
        Übersetzt eine Zuweisung.
        """
        self.visit(node.right)
        self.buf.append("STORE")
        self.buf.append(node.left)

    def visit_PrintStatement(self, node):
        self.visit(node.expr)
        self.buf.append("PRINT")

    def visit_IfStatement(self, node):
        """
        Beispiel:

        if a < b:
            print 27
        print 28

        Wenn die Bedingung zutrifft, kein Sprung, der IP wird
        einfach inkrementiert. Ansonsten wird zu "print 28"
        gesprungen.
        """ 
        self.visit(node.expr)
        self.buf.append("CJUMP")
        label = self._gen_label()
        self.buf.append(Marker(label))
        for subnode in node.body:
            self.visit(subnode)
        self.buf.append(Label(label))


    def visit_WhileStatement(self, node):
        """
        i = 0
        while i < 10:
            print i
        end
        """
        head_label = self._gen_label()
        self.buf.append(Label(head_label))
        self.visit(node.expr)
        self.buf.append("CJUMP")
        body_label = self._gen_label() # eigentlich addresse *nach* dem body
        self.buf.append(Marker(body_label))

        for subnode in node.body:
            self.visit(subnode)
        self.buf.append("JUMP")
        self.buf.append(Marker(head_label))
        self.buf.append(Label(body_label))

    def visit_Identifier(self, node):
        self.buf.append("LOAD")
        self.buf.append(node.name)

