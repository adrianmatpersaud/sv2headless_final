import re
import file_search as fs
import str_process as sp
import parser as parse
import string

def dev():
    file_name = "filtered_cpu.vh"
    working_dir = "/home/janaka/Documents/python/sv2headless/tests/"

    path = working_dir + file_name

    with open(path, 'r') as f:
        file_content = f.read() 
    

    f.close()
    return file_content, file_name, working_dir

def printi(ls):
    for x in ls:
        print(x)
        print("------------------------------")

def return_typedefs(text):
    # - annotation because this seems a little weird;
    # - we do two pattern matches here because there are single and multiline typdefs; think
    #   struct vs just declaring a type eg word_t
    # - the re.DOTALL option allows .* to match literally anything, including new lines,
    #   if the option is off then you only match a single line; its kinda like a regex steamroller

    pattern = r'typedef .*;'
    typedefs_single_line = re.findall(pattern, text)
    pattern = r'(typedef *(enum|struct).*?{.*?}.*?;)' # this is nasty, im sorry
    typedefs_multi_line = re.findall(pattern, text, re.DOTALL)
    typedefs_multi_line = [x[0] for x in typedefs_multi_line] # due to the brackets, we select the first option

    
    ret = typedefs_multi_line + typedefs_single_line
    ret = [x for x in ret if x != []]
    return ret

# this is short for symbol table replace: find matches and replaces them
#                                         also returns if a replacement was made
def st_replace(text, st_nodes):
    did_replace = False
    ret = text
    for i in st_nodes:
        pattern = r'\b' + re.escape(i.entry) + r'\b'

        if (type(i.types) != int) and (not i.ispacked) and (not i.enuminner):
            if(re.search(pattern, text)):
                did_replace = True
            ret = re.sub(pattern, i.types, ret) 

    return ret, did_replace

def type_replace_pass(text_ls, st_node_ls):
    #print("xxxxxxxxxxxx")
    notdone = False
    ret = text_ls
    memo = len(text_ls)
    for i in range(memo):
        symbol_table_list = st_node_ls[i]
        remaining = text_ls[i+1:memo]
        for j in range(len(remaining)):
            iter = i + j + 1
            new_str, doneness = st_replace(remaining[j], st_node_ls[i])
            notdone = notdone or doneness
            #print(ret[iter])
            ret[iter] = new_str

    return ret, notdone

def full_replace_types(typedefs, st_nodes):
    notdone = True
    while notdone:
        typedefs, notdone = type_replace_pass(typedefs, st_nodes)
        st_nodes = [parse.try_parse(x) for x in typedefs]

    #return typedefs
    return st_nodes

def contains_whitespace(s):
    return True in [c in s for c in string.whitespace]

def get_typedef_n_stnode(vh_file):
    #print("xxxxxxxxxxxx")
    ordered_typedefs = ["typedef " + x for x in vh_file.split("typedef") if not x.isspace() and x != ""]
    #printi(ordered_typedefs)
    typedefs = [return_typedefs(x)[0] for x in ordered_typedefs if len(x)]
    #typedefs = [return_typedefs(x)[0] if len(return_typedefs(x)) != 0 else [] for x in ordered_typedefs]
    st_nodes = [parse.try_parse(x) for x in typedefs]
    return typedefs, st_nodes

if __name__ == "__main__":
    vh_file, vh_file_name, working_dir = dev()
    
    typedefs, st_nodes = get_typedef_n_stnode(vh_file)
    full_replace_types(typedefs, st_nodes)
        

    #printi(typedefs)
