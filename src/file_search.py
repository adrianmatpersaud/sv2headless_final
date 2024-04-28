import re
import file_search as fs
import str_process as sp
import type_extract as te
import modports as mp
import sys

def return_includes(text):
    # assumption that comments are removed! that's why there a comment remover function
    pattern = '`include "([0-9A-Za-z_]*)'
    matches = re.findall(pattern, text)

    return [m + ".vh" for m in matches]


def dev():
    args = sys.argv
    if(len(args) != 3):
        sys.exit()
    
    working_dir = args[1]
    file_name = args[2]
    path = working_dir + file_name

    with open(path, 'r') as f:
        file_content = f.read() 

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

    return typedefs_multi_line + typedefs_single_line

def return_file_contents(working_dir, file_name):
    # very important to remove comments
    path = working_dir + file_name

    with open(path, 'r') as f:
        file_content = f.read()

    return sp.remove_comments(file_content)

class FileNode:
    def __init__(self, name):
        self.name = name
        self.visited = False

    def mark_visited(self):
        self.visited = True

    def update(self, dir):
        includes = return_includes(return_file_contents(dir, self.name))
        #print(includes)
        if(len(includes) == 0):
            self.visited = True


    def __str__(self):
        visited_status = "Visited" if self.visited else "Not Visited"
        return f"Place: {self.name}, Status: {visited_status}"

def print_nodes(ls):
    [print(x.name + ": " + str(x.visited)) for x in ls]

# Essentially a tree search that checks if current nodes are visited or not
def deliberate_files(text, dir):
    includes = [FileNode(inc) for inc in return_includes(text)]

    # rule is to mark as visited only if there are no includes left
    for i in range(len(includes)):
        node = includes[i]
        node.update(dir)
        if not node.visited:
            dependencies = return_includes(return_file_contents(dir, node.name))
            present_nodes = [inc.name for inc in includes]
            for file in dependencies:
                if file not in present_nodes:
                    includes.append(FileNode(file))

    return includes

def convert_type(dir, name):
    path = dir + name
    with open(path, 'r') as f:
        vh_file = f.read() 
    f.close() 

    vh_file_processed = sp.pre_process_vh(vh_file) # <- comment removal makes parsing steps a bit easier; not necessary
    typedefs, st_nodes = te.get_typedef_n_stnode(vh_file_processed)
    #result = te.full_replace_types(typedefs, st_nodes)
    st = te.full_replace_types(typedefs, st_nodes)
    return st


    #return result

def convert_intermediates(dir, name):
    sv = return_file_contents(dir, name)
    dependencies = return_includes(sv)

    for i in dependencies:
        if "pkg" in i:
            st = convert_type(dir, i)
            for j in st:
                sv, _ = te.st_replace(sv, j)

    return sv

def get_params(dir, name):
    path = dir + name
    with open(path, 'r') as f:
        vh_file = f.read() 
    f.close() 

    params = "\n".join([line for line in vh_file.splitlines() if "param" in line])
    print(params)

if __name__ == "__main__":
    # have these be inputs
    vh_file, vh_file_name, working_dir = dev()
    
    # vh_file, vh_file_name, working_dir = dev()
    includes = deliberate_files(vh_file, working_dir)
  
    # get parameters
    params = []
    for i in includes:
        if i.visited:
            get_params(working_dir, i.name)

    vh = ""
    # deliberate on types
    for i in includes:
        if not i.visited:
            vh = convert_intermediates(working_dir, i.name)

    if vh != "":
        modports_st = mp.parse_modIOT(vh)
        type_dict = mp.type_dict(mp.return_modtypes(vh))

    sv = convert_intermediates(working_dir, vh_file_name)
    
    # final replace
    pattern = r'([A-Za-z_]+)\.([A-Za-z_]+) +([A-Za-z_]+)'
    matches = re.findall(pattern, sv)[0]

    # grab the rest
    port_name = matches[1]
    if vh != "":
        for i in modports_st:
            if i.name == port_name:
                node = i

    # Get types
    conjunc = " " + matches[2] + "_"
    mod_input_types = [type_dict[x] for x in node.inp]
    inputs = [conjunc.join(pair) for pair in zip(mod_input_types, node.inp)]

    mod_output_types = [type_dict[x] for x in node.out]
    outputs = [conjunc.join(pair) for pair in zip(mod_output_types, node.out)]

    # build modport & replace
    mod = ",\n".join(inputs) + ",\n"  + ",\n".join(outputs)
    replacee = matches[0] + "." + matches[1] + " " + matches[2]
    sv = sv.replace(replacee, mod)
    sv = sv.replace(".", "_")

    # cleanup
    filtered_lines = "\n".join([line for line in sv.splitlines() if "import" not in line])
    filtered_lines = "\n".join([line for line in filtered_lines.splitlines() if "include" not in line])
    print(filtered_lines)
