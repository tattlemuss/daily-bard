#!/usr/bin/python
WEBSITE_BASE="http://www.clarets.org/daily-bard/"
DEBUG=True

SECTION_PATH="../sections"
TEMPLATE_PATH="../templates"

import datetime, os
import pickle

def get_module_directory():
    """ Return the full path to this very python file.
        Used to load template/section data"""
    import inspect
    module_fname = inspect.getfile(inspect.currentframe()) # script filename (usually with path) 
    return os.path.dirname(os.path.abspath(module_fname)) # script directory
    
def rfcformat(fmt_date):
    """ Hack a string matching a convincing date 
    of the format https://tools.ietf.org/html/rfc3339 """
    suffix = "T00:00:00Z"
    return fmt_date.strftime("%Y-%m-%d") + suffix
    
def expand_template(tmpl_text, values):
    """ Simplest template expander.
    Matches {{TAG}} and replaces with TAG as a key in the
    supplied values dictionary. """
    
    import re
    search_re = re.compile("{{(.*)}}")
    def replace_func(matchobj):
        key = matchobj.group(1)
        if values.has_key(key):
            return values[key]
        return "MISSING"
    output = re.sub(search_re, replace_func, tmpl_text)
    return output

def load_template_file(fname):
    """ Load a template in the TEMPLATE_PATH directory into a string """
    mod_dir = get_module_directory()
    abs_fname = os.path.join(mod_dir, TEMPLATE_PATH, fname)
    fh = open(abs_fname, "r")
    lines = ''.join(fh.readlines())
    fh.close()
    return lines
    
def expand_template_file(fname, values):
    """ Expand a template in the TEMPLATE_PATH directory """
    lines = load_template_file(fname)
    return expand_template(lines, values)

def get_playcode_load_path(playcode):
    """ Generate the directory path for a given play code """
    mod_dir = get_module_directory()
    load_path = os.path.join(mod_dir, SECTION_PATH, playcode)
    return load_path

def unpickle(fname):
    fh = open(fname, "rb")
    data = pickle.load(fh)
    fh.close()
    return data
    
def generate(playcode, base_day, today):
    load_path = get_playcode_load_path(playcode)

    # Work out how far from "today" we are
    td = today - base_day
    day_delta = td.days

    # Read play details
    play_data = unpickle(os.path.join(load_path, "play.play"))
    section_count   = play_data['section_count']
    title           = play_data['full_title']
    
    # Modulo the day offset
    offset = day_delta % section_count
    curr = offset
    post_tmpl = load_template_file('rss_post.xml')
    all_posts = ''

    # "curr" counts down backwards in time
    while curr >= 0 and curr > offset - 15:
        readable_id = curr + 1
        fname = "section_%d.sect" % (readable_id)
        values = unpickle(os.path.join(load_path, fname))
        
        section = ''.join(values['text'])
        line_id = values['line_id']
        playcode = values['playcode']

        episode_title = "%s (%d/%d)" % (title, readable_id, section_count)
        
        # Generate a date N days back
        date_offset = datetime.timedelta(offset - curr)
        final_post_date = today - date_offset
        post_values = { "content" : section,
                   "personae" : values['personae'],
                   "author" : "Shakespeare, William",
                   "title" : episode_title,
                   "full_url" : values['url'],
                   "postdate" : rfcformat(final_post_date) }
        all_posts += expand_template(post_tmpl, post_values)
        curr -= 1

    values = { 
                "play" : title,
                "url" : WEBSITE_BASE,
                "all_posts" : all_posts
                }

    final = expand_template_file("rss.xml", values)
    return final

def generate_rss():
    """ Generate the RSS feed pages on a daily basis """
    import cgi
    import re
    def parse():
        try:

            form = cgi.FieldStorage()
            form_play = form.getfirst("play", "")
            form_date = form.getfirst("start", "")

            # alphanumeric only for play
            if not re.match("[a-z0-9]+$", form_play):
                return False
            # 8 number only for date. Obviously not exhaustive
            if not re.match("[0-9]{8}$", form_date):
                return False

            base_year  = int(form_date[0:4])
            base_month = int(form_date[4:6])
            base_day   = int(form_date[6:8])
            base_date = datetime.date(base_year, base_month, base_day)
            today = datetime.datetime.utcnow().date()

            final = generate(form_play, base_date, today)
            print final
        except:
            # Swallow any error
            raise
            return False
        return True

    print "Content-Type: text/html"     # HTML is following
    print                               # blank line, end of headers
    if not parse():
        print "Failure"
        
def generate_rss_link(date, playcode, title):
    fmt_date = date.strftime("%Y%m%d")
    return "<li><a href=\"rss.py?play={}&start={}\">{}</a></li>\n".format(playcode, fmt_date, title)
    
def generate_frontpage():
    """ Generate the front page with RSS links """
    
    today = datetime.datetime.utcnow().date()
    playcodes = ['kinglear', '12night']
    
    links = ''
    for playcode in playcodes:
        load_path = get_playcode_load_path(playcode)
        # Read play details
        fh = open(os.path.join(load_path, "play.play"), "rb")
        play_data = pickle.load(fh)
        fh.close()
        
        links += generate_rss_link(today, playcode, play_data['short_title'])
        
    values = { 'rss_links' : links }    
    tmpl_path = "frontpage.html"
    txt = expand_template_file(tmpl_path, values)
    
    print "Content-Type: text/html"     # HTML is following
    print                               # blank line, end of headers
    print txt
    
    