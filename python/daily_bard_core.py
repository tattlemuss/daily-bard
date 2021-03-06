import datetime, os
import pickle
import daily_bard_settings
import templating

if daily_bard_settings.IS_DEBUG:
    import cgitb
    cgitb.enable()

def get_module_directory():
    """ Return the full path to this very python file.
        Used to load template/section data"""
    import inspect
    module_fname = inspect.getfile(inspect.currentframe()) # script filename (usually with path) 
    return os.path.dirname(os.path.abspath(module_fname)) # script directory
    
def rfcformat(fmt_date):
    """ Hack a string matching a convincing date 
    of the format https://tools.ietf.org/html/rfc3339 """
    suffix = 'T00:00:00Z'
    return fmt_date.strftime('%Y-%m-%d') + suffix
    
def get_playcode_load_path(playcode):
    """ Generate the directory path for a given play code """
    mod_dir = get_module_directory()
    load_path = os.path.join(mod_dir, daily_bard_settings.SECTION_PATH, playcode)
    return load_path

def unpickle(fname):
    fh = open(fname, 'rb')
    data = pickle.load(fh)
    fh.close()
    return data
    
def generate(playcode, base_day, today):
    load_path = get_playcode_load_path(playcode)

    # Work out how far from "today" we are
    td = today - base_day
    day_delta = td.days
    updated = rfcformat(today)

    # Read play details
    play_data = unpickle(os.path.join(load_path, 'play.play'))
    section_count   = play_data['section_count']
    title           = play_data['full_title']
    
    post_tmpl = templating.load('rss_post.xml')
    all_posts = ''

    # Loop back 30 days, wrapping round if necessary
    for sub in range(0, 30):
        final_day_offset = day_delta - sub

        # Cull out-of-range entries
        if (final_day_offset < 0):
            continue
        if (final_day_offset >= section_count):
            continue

        # Modulo the day offset
        readable_id = final_day_offset
        fname = 'section_%d.sect' % (readable_id)
        values = unpickle(os.path.join(load_path, fname))
        
        section = ''.join(values['text'])
        line_id = values['line_id']
        playcode = values['playcode']
        
        # Generate a date N days from the base
        date_offset = datetime.timedelta(final_day_offset)
        final_post_date = base_day + date_offset
        post_values = { 
                   'content' : section,
                   'playcode' : playcode,
                   'line_id' : line_id,
                   'personae' : values['personae'],
                   'author' : 'Shakespeare, William',
                   'full_title' : title,
                   'full_url' : values['url'],
                   'postdate' : rfcformat(final_post_date),
                   'unique_id' : final_day_offset,
                   'section_num' : readable_id,
                   'day_num' : readable_id + 1,
                   'section_total' : section_count
                   }
                   
        all_posts += templating.expand(post_tmpl, post_values)

    values = { 
                'updateddate' : updated,
                'play' : title,
                'url' : daily_bard_settings.WEBSITE_BASE_URL,
                'all_posts' : all_posts
                }

    final = templating.expand_file('rss.xml', values)
    return final

def generate_rss():
    """ Generate the RSS feed pages on a daily basis """
    import cgi
    import re
    def parse():
        try:
            form = cgi.FieldStorage()
            form_play = form.getfirst('play', '')
            form_date = form.getfirst('start', '')

            # alphanumeric only for play
            if not form_play in daily_bard_settings.ALLOWED_PLAYCODES:
                return False
            # 8 number only for date. Obviously not exhaustive
            if not re.match('[0-9]{8}$', form_date):
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
            return False
        return True

    if not parse():
        # Show empty page in failure case
        print "Content-Type: text/xml"
        print
        print "<?xml version=\"1.0\" encoding=\"utf-8\"?><feed/>"

def generate_rss_link(date, playcode, title, section_count):
    fmt_date = date.strftime('%Y%m%d')
    return '<li><a href="rss.py?play={}&start={}">{}</a> ({} episodes)</li>\n'.format(playcode, fmt_date, title, section_count)
    
def generate_index():
    """ Generate the front page with RSS links """
    today = datetime.datetime.utcnow().date()
    links = ''
    for playcode in daily_bard_settings.ALLOWED_PLAYCODES:
        load_path = get_playcode_load_path(playcode)
        
        # Read play details
        fh = open(os.path.join(load_path, 'play.play'), 'rb')
        play_data = pickle.load(fh)
        fh.close()
        links += generate_rss_link(today, playcode, play_data['short_title'], play_data['section_count'])
        
    values = { 'rss_links' : links }    
    tmpl_path = 'frontpage.html'
    txt = templating.expand_file(tmpl_path, values)    
    print txt
