#coding: utf-8

from collections import namedtuple
import operator as op


math_symbols = {'+' : "ADD",
                '-' : "SUB",
                '*' : "MUL",
                '/' : "DIV"}

comparison_symbols = {'<'  : "LT",
                      '>'  : "GT",
                      '==' : 'EQ'}

operations = {"ADD" : op.add,
              "SUB" : op.sub,
              "MUL" : op.mul,
              "DIV" : op.div,
              "LT"  : op.lt,
              "GT"  : op.gt,
              "EQ"  : op.eq}
