#coding: utf-8
from opcodes import operations
from utils import newline
from scope import Scope
import sys

class Interpreter(object):

    def __init__(self, code):
        self.code = code

    def run(self):
        if len(self.code) == 0:
            return

        stack = []
        table = Scope() 
        addresses = []
        #print self.code
        i = 0

        while i < len(self.code):
            current = self.code[i]
            if current == 'LOAD_CONST':
                i += 1
                current = self.code[i]
                stack.append(current)
            elif current == 'STORE':
                try:
                    i += 1
                    current = self.code[i]
                    table[current] = stack.pop()
                except IndexError:
                    msg = "Index: %s - Current: %s" % (str(i), str(current))
                    raise errors.EmptyStackException(msg)
            elif current == 'LOAD':
                i += 1 
                current = self.code[i]
                stack.append(table[current])
            elif current == 'PRINT':
                print stack.pop()
            elif current == 'CJUMP':
                """
                JNE
                <absoluter offset>
                Springt zum offset, falls der aktuelle Wert auf dem Stack 
                ´False´ ist. 
                """
                i += 1
                offset = int(self.code[i])
                condition = stack.pop()
                if not condition:
                    i = offset # sprung
                    continue
            elif current == 'JUMP':
                """
                JUMP
                <absoluter offset>
                Bedingungsloser Sprung zum offset.
                """
                i += 1
                offset = int(self.code[i])
                i = offset # sprung
                continue
            elif current in operations:
                try:
                    val1 = int(stack.pop())
                    val2 = int(stack.pop())
                except ValueError:
                    msg = """ Index: %s - Invalid operand for arithmetical 
                              operation: %s %s""" % (str(val1), str(val2))
                    raise errors.InvalidOperandException(msg)
                except IndexError:
                    msg = "Index: %s - Current: %s" % (str(i), str(current))
                    raise errors.EmptyStackException(msg)
                res = operations[current](val1, val2)
                stack.append(res)
            elif current == "EOF":
                return
            elif current == "PUSH_SCOPE":
                table.push({})
            elif current == "POP_SCOPE":
                table.pop()
            elif current == "PUSH_ADDRESS":
                i += 1
                offset = int(self.code[i])
                addresses.append(offset)
            elif current == "RET":
                assert addresses # Return without address doesn't make sense ;)
                offset = addresses.pop()
                i = offset
            else:
                try:
                    int(current)
                except ValueError:
                    msg = """Index: %s - 
                             Invalid Opcode: %s""" % (str(i), str(current))
                    raise errors.InvalidOpcodeException(msg) 
            i += 1
            #print stack
            #print table
