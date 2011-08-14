#coding: utf-8

# taken from https://github.com/fredreichbier/pyneko/blob/master/pyneko/visitor.py
# thanks!

class Visitor(object):
    def visit(self, node):
        return self.dispatch(node)

    def dispatch(self, node, *args):
        clsname = node.__class__.__name__
        meth = getattr(self, 'visit_' + clsname, self.default)
        return meth(node, *args)

    def default(self, node, *args):
        print 'No visitor for Node %s, args=%s' % (node, args)
        return NotImplemented
