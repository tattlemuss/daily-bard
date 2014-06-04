"""
    Wrapper functions round the Python standard templating lib
"""

import os, daily_bard_settings

def get_module_directory():
    """ Return the full path to this very python file.
        Used to load template/section data"""
    # TODO: factor out
    import inspect
    module_fname = inspect.getfile(inspect.currentframe()) # script filename (usually with path) 
    return os.path.dirname(os.path.abspath(module_fname)) # script directory
    
def expand(tmpl_text, values):
    """ Simplest template expander. """
    from string import Template
    tmpl = Template(tmpl_text)
    return tmpl.substitute(values)

def load(fname):
    """ Load a template in the TEMPLATE_PATH directory into a string """
    mod_dir = get_module_directory()
    abs_fname = os.path.join(mod_dir, daily_bard_settings.TEMPLATE_PATH, fname)
    fh = open(abs_fname, "r")
    lines = ''.join(fh.readlines())
    fh.close()
    return lines

def expand_file(fname, values):
    """ Expand a template in the TEMPLATE_PATH directory """
    lines = load(fname)
    return expand(lines, values)
