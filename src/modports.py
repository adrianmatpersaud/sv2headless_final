from lark import Lark
from lark import Transformer
import re

mp_types = Lark('''
            // enum logic --------------------
            start: "logic" types (name ",")* name ";"
            types: array*
            // -----------------------------------

            array: "[" name ":" name "]"
            bits: /[a-zA-Z0-9_'-]+/
            type_name: /[a-zA-Z0-9_-]+/
            name: /[a-zA-Z0-9_-]+/

            %ignore " "              // Disregard spaces in text
            %ignore /[\\t\\n\\r ]+/ // ignore newlines, this is rly rly weird due to the escapes
         ''',start='start')

class MPNode:
    def __init__(self, types, var):
        self.types = types
        self.var = var
    
    def printl(self):
        print("types:", self.types)
        print("vars:", self.var)

class mp_types_modT(Transformer):
    def name(self, s):
        return str(s[0])

    def array(self, s):
        arr = "[" + s[0] + ":" + s[1] + "]"
        return arr

    def types(self, s):
        ret = "logic " + " ".join(s)
        return ret

    def start(self, s):
        node = MPNode(s[0], s[1:])
        #node.printl()
        return node

struct = '''
  logic     WEN;
  logic [REG_W-1:0] wsel, rsel1, rsel2;
  logic [WORD_W-1:0]    wdat, rdat1, rdat2;
'''

def get_modvars(text):
    lines = text.split('\n')
    logic_lines = [line.lstrip() for line in lines if line.strip().startswith('logic')]
    return logic_lines

def parse_modT(text):
    tree = mp_types.parse(text)
    struct = mp_types_modT().transform(tree)
    return struct

# main return function
def return_modtypes(text):
    mod = get_modvars(text)
    mod_nodes = [parse_modT(x) for x in mod]
    return mod_nodes

def printi(ls):
    for i in ls:
        i.printl()
        print()

pp = lambda x,y: print( x.parse(y).pretty() )
n = return_modtypes(struct)
#printi(n)

modport = Lark('''
            // enum logic --------------------
            start: "modport" name "(" inner ");"
            inner: (inp | out)*
            inp: "input" (name ",")* name ","?
            out: "output" (name ",")* name ","?
            // -----------------------------------

            array: "[" name ":" name "]"
            bits: /[a-zA-Z0-9_'-]+/
            type_name: /[a-zA-Z0-9_-]+/
            name: /[a-zA-Z0-9_-]+/

            %ignore " "              // Disregard spaces in text
            %ignore /[\\t\\n\\r ]+/ // ignore newlines, this is rly rly weird due to the escapes
         ''',start='start')


class MPIONode:
    def __init__(self, inp, out):
        self.name = "uninit"
        self.inp = inp
        self.out = out

    def put_in(self, inp):
        self.inp = inp

    def put_out(self, out):
        self.out = out

    def name_me(self, name):
        self.name = name
    
    def printl(self):
        print("name:", self.name)
        print("inp:", self.inp)
        print("out:", self.out)

class mpio_types_modT(Transformer):
    def name(self, s):
        return str(s[0])

    def inp(self, s):
        ret = ("inp", s)
        return ret

    def out(self, s):
        ret = ("out", s)
        return ret
    
    def inner(self, s):
        node = MPIONode([], [])
        for i in s:
            if i[0] == "inp":
                node.put_in(i[1])
            elif i[0] == "out":
                node.put_out(i[1])
        return node

    def start(self, s):
        name = s[0]
        node = s[1]
        node.name_me(name)
        return node

def parse_modIOT_single(text):
    tree = modport.parse(text)
    struct = mpio_types_modT().transform(tree)
    return struct

def grab_modport(text):
    pattern = r'modport.*?\);'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

def parse_modIOT(text):
    matches = grab_modport(text)
    ls = []
    for i in matches:
        ls.append(parse_modIOT_single(i))

    return ls

struct = '''
  modport mod1 (
    input   abc, def, qrx,
    output  val, val2
  );

  modport mod2 (
    input  val, val2,
    output   abc, def, qrx
  );
'''

ls = parse_modIOT(struct)

def type_dict(n):
    result_dict = {}
    for instance in n:
        for var in instance.var:
            result_dict[var] = instance.types
    return result_dict
