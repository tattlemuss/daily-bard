header_tmpl = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
 <title>$$TITLE/$</title>
    <link href="{{page.node.full_url}}/atom.xml" rel="self"/>
    <link href="{{site.full_url}}"/>
 <updated>{{now|xmldatetime}}</updated>
 <id>{{site.full_url}}</id>
"""

post_tmpl = """
        <entry>
        <title>{{node_page.title}}</title>
        <author><name>{{site.author}}</name></author>
        <link href="{{node_page.full_url}}"/>
        <updated>{{node_page.updated|default:node_page.created|xmldatetime}}</updated>
        <published>{{node_page.created|xmldatetime}}</published>
        <id>{{node_page.full_url}}</id>
        {%block entry_extra%}{%endblock%}
        <content type="html">
            {%filter force_escape%}{% render_article node_page %}{%endfilter%}
        </content>
        </entry>
"""

footer_tmpl = """
</feed>"""


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
        
        section = ''.join(fh.readlines())
        fh.close()
        final += section
        curr -= 1

    final += footer_tmpl
    
    fh = open(output_path, 'w')
    fh.write(final)   
    fh.close()

if __name__ == '__main__':
    # Generate the last 10 posts
    generate('12night', 2, 'atom.xml')


