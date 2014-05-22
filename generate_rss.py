header_tmpl = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
 <title>The Daily Bard: {{play}}</title>
 <id>{{url}}</id>
"""

post_tmpl = """
        <entry>
        <title>{{title}}</title>
        <author><name>{{site.author}}</name></author>
        <link href="{{full_url}}"/>
        <published>{{postdate}}</published>
        <updated>{{postdate}}</updated>
        <id>{{full_url}}</id>
        <content type="html">
<![CDATA[{{content}}
        ]]>
        </content>
        </entry>
"""

footer_tmpl = """
</feed>"""

WEBSITE_BASE="http://www.clarets.org/daily-bard/"

import datetime, os
import pickle

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

def generate(load_path, output_path, title, base_day, today):
    # Work out how far from "today" we are
    td = today - base_day
    day_delta = td.days
    
    # Scan the sections directory for number of sections
    # the play is made from
    import fnmatch
    # TODO: just use count
    all_files = []
    files = os.listdir(load_path)
    for f in fnmatch.filter(files, '*.sect'):
        all_files.append(f)

    values = { 
                "play" : title,
                "url" : WEBSITE_BASE
            }
    final = expand_template(header_tmpl, values)
    section_count = len(all_files)
    
    # Modulo the day offset
    offset = day_delta % section_count
    curr = offset

    # "curr" counts down backwards in time
    while curr >= 0 and curr > offset - 10:
        readable_id = curr + 1
        fname = "section_%d.sect" % (readable_id)

        fh = open(os.path.join(load_path, fname), "rb")
        values = pickle.load(fh)
        fh.close()
        
        section = ''.join(values['text'])
        line_id = values['line_id']
        playcode = values['playcode']

        # Generate a date N days back
        date_offset = datetime.timedelta(offset - curr)
        final_post_date = today - date_offset
        values = { "content" : section,
                   "site.author" : "Shakespeare, William",
                   "title" : values['title'],
                   "full_url" : values['url'],
                   "postdate" : rfcformat(final_post_date) }
        final += expand_template(post_tmpl, values)
        curr -= 1

    final += footer_tmpl
    
    fh = open(output_path, 'w')
    fh.write(final)   
    fh.close()

if __name__ == '__main__':
    # Generate the last 10 posts
    base_day = datetime.date(2014, 05, 21)
    today = datetime.date.today()
    import sys
    (section_path, atom_output_path, title) = sys.argv[1:4]
    generate(section_path, atom_output_path, title, base_day, today)

