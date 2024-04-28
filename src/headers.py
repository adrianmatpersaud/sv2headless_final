import file_search as fs
import str_process as sp
import type_extract as te

def dev():
    file_name = "cpu_types_pkg.vh"
    working_dir = "/home/janaka/Documents/python/sv2headless/files/"
    path = working_dir + file_name

    with open(path, 'r') as f:
        file_content = f.read() 
    
    f.close()
    return file_content, file_name, working_dir

if __name__ == "__main__":
    vh_file, vh_file_name, working_dir = dev()

    # local passes
    vh_file_processed = sp.pre_process_vh(vh_file)
    typedefs, st_nodes = te.get_typedef_n_stnode(vh_file_processed)
    result = te.full_replace_types(typedefs, st_nodes)

    te.printi(result)
