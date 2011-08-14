#coding: utf-8

import cStringIO
from utils import newline
import sys
#from compiler import Marker, Label
import compiler
class Writer(object):

    def __init__(self):
        self.buf = []

    def append(self, node):
        if isinstance(node, Writer):
            for line in node.buf:
                self.buf.append(line)
        elif isinstance(node, compiler.Marker):
            self.buf.append(node) 
        elif isinstance(node, compiler.Label):
            self.buf.append(node)
        else:
            self.buf.append(newline(str(node)))
  
    def eval_offsets(self):
        repeat = True
        offsets = {}
        tmp_buf = self.buf
        while repeat:
            unresolved_markers = False
            unresolved_addresses = False
            for line_cnt, elem in enumerate(tmp_buf):
                if isinstance(elem, compiler.Label):
                    offsets[elem.label] = line_cnt
                    self.buf.remove(elem)
                    unresolved_labels = True
                elif isinstance(elem, compiler.Marker):
                    if not elem.label in offsets:
                        # print "Found an unresolved marker"
                        unresolved_markers = True
                    else:
                        offset = offsets[elem.label]
                        self.buf[self.buf.index(elem)] = newline(offset)
            
            repeat = unresolved_markers or unresolved_addresses
            tmp_buf = self.buf

    def write(self, filename):
        self.eval_offsets()
        with open(filename, "wb") as f:
            for line in self.buf:
                f.write(str(line))

    def __repr__(self):
        return "".join(self.buf)
    
    def get_linecount(self):
        return len(self.buf)

    linecount = property(get_linecount)
