header_tmpl = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
 <title>The Daily Bard</title>
 <id>{{site.full_url}}</id>
"""

post_tmpl = """
        <entry>
        <title>{{title}}</title>
        <author><name>{{site.author}}</name></author>
        <link href="{{full_url}}"/>
        <published>{{created|xmldatetime}}</published>
        <updated>{{created|xmldatetime}}</updated>
        <id>{{full_url}}</id>
        <content type="html">
<![CDATA[<pre>{{content}}</pre>]]>
        </content>
        </entry>
"""

footer_tmpl = """
</feed>"""

def expand_template(tmpl_text, values):
    import re
    search_re = re.compile("{{(.*)}}")
    def replace_func(matchobj):
        key = matchobj.group(1)
        if values.has_key(key):
            return values[key]
        return "MISSING"
    output = re.sub(search_re, replace_func, tmpl_text)
    return output

def generate(load_path, offset, output_path):
    # Scan for number of items
    import os, fnmatch
    all_files = []
    files = os.listdir(load_path)
    for f in fnmatch.filter(files, '*.html'):
        all_files.append(f)

    final = header_tmpl
    module_count = len(all_files)
    curr = offset
    while curr >= 0 and curr > offset - 10:
        chunk_id = curr
        fname = "section_%d.html" % (chunk_id + 1)

        fh = open(os.path.join(load_path, fname))
        section = '<br/>'.join(fh.readlines())
        fh.close()

        values = { "content" : section,
                   "site.author" : "Shakespeare, William",
                   "title" : "Section %d" % chunk_id,
                   "full_url" : "http://clarets.org",
                   "created|xmldatetime" : "2014-02-15T09:00:00Z"   }
        final += expand_template(post_tmpl, values)
        curr -= 1

    final += footer_tmpl
    
    fh = open(output_path, 'w')
    fh.write(final)   
    fh.close()

if __name__ == '__main__':
    # Generate the last 10 posts
    generate('sections/kinglear', 2, 'atom_kinglear.xml')


