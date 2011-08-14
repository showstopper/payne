from code.symbol import parse
from code.compiler import Compiler
from code.interpreter import Interpreter
import sys

def exec_file(fname):
    with open(fname, "rb") as f:
        data = f.read()
        evaluate(data)       
        
def evaluate(s):
    code = _compile(s)
    interpreter = Interpreter(code)
    interpreter.run()

def _compile(s):
    module = parse(s)
    c = Compiler(module)
    code = c.compile().splitlines()
    return code

def main():
    for f in sys.argv[1:]:
        print "-- EXEC %s --" %(f)
        try:
            exec_file(f)
        except Exception, e:
            print type(e)
            print e
        print ""
        
if __name__ == '__main__':
    main()

