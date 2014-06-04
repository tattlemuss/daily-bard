"""
    Copy the templated CGI scripts out, and stamp them
    with the path to import our core code.
    
    Effectively the cgi files just act as simple frontends
    to pass through to daily_bard_core.py.
"""

import os, stat, daily_bard_settings

def get_module_directory():
    """ Return the full path to this very python file.
        Used to load template/section data"""
    import inspect
    module_fname = inspect.getfile(inspect.currentframe()) # script filename (usually with path) 
    return os.path.dirname(os.path.abspath(module_fname)) # script directory
     
def expand_template(tmpl_text, values):
    """ Simplest template expander. """
    from string import Template
    tmpl = Template(tmpl_text)
    return tmpl.substitute(values)

def load_template_file(fname):
    """ Load a template in the TEMPLATE_PATH directory into a string """
    mod_dir = get_module_directory()
    abs_fname = os.path.join(mod_dir, daily_bard_settings.TEMPLATE_PATH, fname)
    fh = open(abs_fname, "r")
    lines = ''.join(fh.readlines())
    fh.close()
    return lines

def publish_cgi(output_fname, function_call):
    l = load_template_file("front_cgi.txt")
    values = { 'path_to_python'    : daily_bard_settings.PATH_TO_PYTHON,
               'path_to_dailybard' : get_module_directory(),
               'function_call'     : function_call}
    tmpl = expand_template(l, values)
    full_fname = os.path.join(daily_bard_settings.CGI_PATH, output_fname)
    fh = open(full_fname, 'w')
    fh.write(tmpl)
    fh.close()
    #os.chmod(full_fname, stat.S_IXUSR)
    
if __name__ == '__main__':
    publish_cgi('index.py', 'generate_index')
    publish_cgi('rss.py',   'generate_rss')
         
    
