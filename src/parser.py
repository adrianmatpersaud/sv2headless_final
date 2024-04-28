from lark import Lark
from lark import Transformer

enum_assign = Lark('''
            // enum logic --------------------
            enum: "typedef" "enum" typeinfo "{" enum_inner "}" type_name ";"
            typeinfo: (array | name)*
            enum_inner: (enum_var ",")* enum_var
            enum_var: name "=" bits
            // -----------------------------------

            array: "[" name ":" name "]"
            bits: /[a-zA-Z0-9_'-]+/
            type_name: /[a-zA-Z0-9_-]+/
            name: /[a-zA-Z0-9_-]+/

            %ignore " "              // Disregard spaces in text
            %ignore /[\\t\\n\\r ]+/ // ignore newlines, this is rly rly weird due to the escapes
         ''',start='enum')

enum_normal = Lark('''
            // enum logic --------------------
            enum: "typedef" "enum" typeinfo "{" enum_inner "}" type_name ";"
            typeinfo: (array | name)*
            enum_inner: (name ",")* name
            // -----------------------------------

            array: "[" name ":" name "]"
            type_name: /[a-zA-Z0-9_-]+/
            name: /[a-zA-Z0-9_-]+/

            %ignore " "              // Disregard spaces in text
            %ignore /[\\t\\n\\r ]+/ // ignore newlines, this is rly rly weird due to the escapes
         ''',start='enum')

simple = Lark('''
            // enum logic --------------------
            de: "typedef" typeinfo type_name ";"
            typeinfo: (array | name)*
            // -----------------------------------

            array: "[" name ":" name "]"
            type_name: /[a-zA-Z0-9_-]+/
            name: /[a-zA-Z0-9_-]+/

            %ignore " "              // Disregard spaces in text
            %ignore /[\\t\\n\\r ]+/ // ignore newlines, this is rly rly weird due to the escapes
         ''',start='de')

struct_packed = Lark('''
            // enum logic --------------------
            de: "typedef" "struct" "packed" "{" packed_inner "}" type_name ";"
            packed_inner: var*
            var: var_types var_name ";"
            var_types: (name | array)*
            var_name: name
            // ----------------------------------- }

            array: "[" name ":" name "]" // remove this in the morning
            type_name: /[a-zA-Z0-9_-]+/
            name: /[a-zA-Z0-9_-]+/

            %ignore " "              // Disregard spaces in text
            %ignore /[\\t\\n\\r ]+/ // ignore newlines, this is rly rly weird due to the escapes
         ''',start='de')

pp = lambda x,y: print( x.parse(y).pretty() )
flatten = lambda xs: [item for sublist in xs for item in sublist]

def printn(ls):
    for x in ls:
        x.print()
        print("")

class STNode:
    def __init__(self, entry, types):
        self.entry = entry
        self.types = types
        self.ispacked = False # relevant for interface swapping
        self.enuminner = False # relevant for interface swapping
    
    def packed(self):
        self.ispacked = True

    def eninner(self):
        self.enuminner = True

    def print(self):
        print("Entry:", self.entry)
        print("types:", self.types)
        print("ispacked:", self.ispacked)
        print("isenuminner:", self.enuminner)


class simple_modT(Transformer):
    def name(self, s):
        return str(s[0])

    def array(self, s):
        arr = "[" + s[0] + ":" + s[1] + "]"
        return arr

    def typeinfo(self, s):
        ret = " ".join(s)
        return ret

    def type_name(self, s):
        return str(s[0])

    def de(self, s):
        node = STNode(s[1], s[0])
        node.simple = True
        return [node]

class enum_normal_modT(Transformer):
    def name(self, s):
        return str(s[0])

    def array(self, s):
        arr = "[" + s[0] + ":" + s[1] + "]"
        return arr

    def enum_inner(self, s):
        ls = [STNode(j,i) for (i, j) in enumerate(s)]

        for i in range(len(ls)):
            ls[i].eninner()

        return ls

    def typeinfo(self, s):
        ret = " ".join(s)
        return ret

    def type_name(self, s):
        return str(s[0])

    def enum(self, s):
        type_name = [STNode(s[2], s[0])]
        return type_name + s[1]

class enum_assign_modT(Transformer):
    def name(self, s):
        return str(s[0])

    def bits(self, s):
        return str(s[0])

    def array(self, s):
        arr = "[" + s[0] + ":" + s[1] + "]"
        return arr

    def typeinfo(self, s):
        ret = " ".join(s)
        return ret

    def type_name(self, s):
        return str(s[0])

    def enum_var(self, s):
        ret = STNode(s[0], s[1])
        ret.eninner()
        return ret

    def enum_inner(self, s):
        return s

    def enum(self, s):
        type_name = [STNode(s[2], s[0])]
        return type_name + s[1]

class packed_modT(Transformer):
    def name(self, s):
        return str(s[0])

    def array(self, s):
        arr = "[" + s[0] + ":" + s[1] + "]"
        return arr

    def var_types(self, s):
        return str(s[0])

    def var_name(self, s):
        return str(s[0])

    def var(self, s):
        ret = STNode(s[1], s[0])
        return ret

    def packed_inner(self, s):
        return s

    def de(self, s):
        ret = s[0]
        for i in range(len(ret)):
            ret[i].packed()

        return ret
        #return s[0] # right now this deletes the name of the packed struct, fix this ig

def try_parse(text):
    if "struct" in text and "packed" in text:
        tree = struct_packed.parse(text)
        return packed_modT().transform(tree)
    elif "enum" in text and "=" in text:
        tree = enum_assign.parse(text)
        return enum_assign_modT().transform(tree)
    elif "enum" in text:
        tree = enum_normal.parse(text)
        return enum_normal_modT().transform(tree)
    else:
        tree = simple.parse(text)
        return simple_modT().transform(tree)
        

if __name__ == "__main__":
    struct1 = '''
      typedef struct packed {
        another_t        another;
        some_t           some1;
        some_t           some2;
        logic [IMM_W-1:0]   imm;
      } someelse_t;
    '''
    
    struct2 = '''
      typedef enum logic [SOM_T-1:0] {
        SLL     = 4'b0000,
        SRL     = 4'b0001,
        ADD     = 4'b0010,
        SUB     = 4'b0011,
        AND     = 4'b0100,
        OR      = 4'b0101,
        XOR     = 4'b0110,
        NOR     = 4'b0111,
        SLT     = 4'b1010,
        SLTU    = 4'b1011
      } types_t;
    '''
    
    struct3 = '''
    typedef enum logic [1:0] {
        USED,
        UNUSED,
        BUSY,
        ELSE
      } state_t;
    '''
    
    struct4 = '''
      typedef logic [SOM_T-1:0] new_t;
    '''

    ls = [struct1, struct2, struct3, struct4]
    ls = [try_parse(x) for x in ls]
    #ls = flatten([try_parse(x) for x in ls])
    #printn(ls)

#tree = struct_packed.parse(struct)
#print(tree.pretty())
#t_f = packed_modT().transform(tree)
#[sv.print() for sv in t_f]
#print(t_f)
