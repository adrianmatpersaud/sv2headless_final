import re

def remove_comments(text):
    comment_strip_pattern = r'//.*?(?=\n)'
    text_strip_comments = re.sub(comment_strip_pattern , '', text)

    multiline_strip_pattern = r'\/\*[\s\S]*?\*\/'
    stripped_text = re.sub(multiline_strip_pattern, '\n', text_strip_comments)

    return stripped_text

def strip_extras(text):
    text_strip_newline = text.replace("\n", " ")
    text_strip_tab = text_strip_newline.replace("\t", " ")
    return text_strip_tab 

def replace_interfaces(text):
    text_stripped = strip_extras(text)

    modport = re.findall(r'module.*?\(.*?\)', text_stripped)[0]
    interfaces = re.findall(r'[A-Za-z_]*\.([A-Za-z_]*) ([A-Za-z_]*)', modport)

    for inter in interfaces:
        new_prefix = inter[0] + "_"
        old_prefix = inter[1] + "."
        processed_text = re.sub(old_prefix, new_prefix, text)

    return processed_text

def return_file(file_name):
    with open(file_name, 'r') as f:
        ret = f.read()
        f.close()

    return ret

def replace_modport(text, dir):
    text_strip_newline = text.replace("\n", " ")
    text_strip_tab = text_strip_newline.replace("\t", " ")

    modport = re.findall(r'module.*?\(.*?\)', text_strip_tab)[0]
    interfaces = re.findall(r'([A-Za-z_]*)\.([A-Za-z_]*) [A-Za-z_]*', modport)

    # create a list of these modports that have been extracted, will need a parser here
    for inter in interfaces:
        include_path = dir + inter[0] + ".vh"
        interface_file = return_file(include_path)
        modport_name = inter[1]
        pattern = r'modport ' + inter[1] + r' \(.*?\)'
        matches = re.findall(pattern, interface_file, re.DOTALL)
        print(matches)
        
    '''
    x get working directory
    x open correponsing interface file
    x grab the corresponding modport from file

    this is a roadblock because there are these cpu types being used
    additionally you need to have a corresponding type for each input or output
    also need that file tree, seems these problems are inter-related
    '''

    return interfaces

def delete_imports(text):
    lines = text.split('\n')
    lines_no_include = [line for line in lines if not line.startswith('`include')]
    filtered_lines = [line for line in lines_no_include if 'import' not in line]
    result = '\n'.join(filtered_lines)
    return result

def delete_header_extras(text):
    lines = text.split('\n')
    filter_define = lambda x: x.startswith('`ifndef') or x.startswith('`define') or x.startswith('`endif')
    filter_package = lambda x: x.startswith('package') or x.startswith('endpackage')
    filtered_lines = [line for line in lines if not (filter_define(line) or filter_package(line))]
    result = '\n'.join(filtered_lines)
    return result

def delete_params(text):
    lines = text.split('\n')
    filtered_lines = [line for line in lines if "parameter" not in line and line != '']
    result = '\n'.join(filtered_lines)
    return result

def pre_process_vh(text):
    return delete_params(delete_header_extras(remove_comments(text)))
