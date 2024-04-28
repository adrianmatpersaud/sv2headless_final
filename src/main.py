import file_search as fs
import str_process as sp

def dev():
    path = '/home/janaka/Documents/python/sv2headless/files/register_file.sv'
    with open(path, 'r') as f:
        file_content = f.read() 
    
    f.close()

    working_dir = '/home/janaka/Documents/python/sv2headless/files/'
    return file_content, "register_file.sv", working_dir

if __name__ == "__main__":
    sv_file, sv_file_name, working_dir = dev()


# sv_file_processed = sp.remove_comments(sv_file) # <- comment removal makes parsing steps a bit easier; not necessary
# sv_interface_swapped = sp.replace_interfaces(sv_file_processed)
# sv_modport_swapped = sp.replace_modport(sv_interface_swapped, working_dir)
# cleaned = sp.delete_imports(sv_interface_swapped)
