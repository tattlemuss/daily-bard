"""
    Script which loads in the OSS databases, splits a
    play into fixed-size sections, and serialises the
    sections into files.
"""
import csv
import sys
import os
import pickle
import daily_bard_settings
import templating

class FormatLine:
    def __init__(self, text, ln):
        self.text = text
        self.score = 0      # Updated by scanning
        self.line_number = ln
        self.is_direction = False      # Mark if this is stage / act direction
        self.is_last_of_speech = False # Mark if this is the last line of a speech
        self.char_id = None

class NormalLine:
    def __init__(self, row):
        self.row = row
        
class Character:
    """ ~CharID~,~CharName~,~Abbrev~,~Works~,~Description~,~SpeechCount~ """
    def __init__(self, row):
        self.row = row
        self.full_name = row[1]
        self.short_name = row[2]
        self.description = row[4]
    def key(self):
        return self.row[0]
    def value(self):
        return self
        
class Para:
    def __init__(self, row):
        self.row = row
    def play(self):
        return self.row[0]
    def character(self):
        return self.row[3]

class Chapter:
    def __init__(self, row):
        self.row = row
    def play(self):
        return self.row[0]
    def key(self):
        return (self.row[2], self.row[3])
    def value(self):
        return self.row[4]
        
class Play:
    def __init__(self, row):
        self.row = row
    def key(self):
        return self.row[0]
    def value(self):
        return self
    def short_title(self):
        return self.row[1]
    def full_title(self):
        return self.row[2]
                
def hash_array(array):
    res = {}
    for row in array:
        res[ row.key() ] = row.value()
    return res

def unique(inputs):
    h = {}
    for i in inputs:
        if i:
            h[i] = True
    k = h.keys()
    return k
    
def read_into_array(filename, classname):
    array = []
    fh = open(filename, 'rb')
    spamreader = csv.reader(fh, delimiter=',', quotechar='~')
    add = False
    for row in spamreader:
        if add:     # skip first row
            array.append(classname(row))
        add = True
    fh.close()
    return array

OSS_URL='http://www.opensourceshakespeare.org' 

def generate_line_link(playcode, line_id, text):
    return "<a href=\"{0}/views/plays/play_view.php?WorkID={1}#{2}\">{3}</a>".format(OSS_URL, playcode, line_id, text)
    
def generate_char_link(playcode, char_id, text):
    return "<a href=\"{0}/views/plays/characters/charlines.php?CharID={1}&WorkID={2}\">{3}</a>".format(OSS_URL, char_id, playcode, text)

def generate_personae(char_dict, char_ids):
    """ Generate text for all the characters supplied in the "char_ids" list """
    unique_ids = unique(char_ids)
    p = []
    unique_ids.sort()
    for char_id in unique_ids:
        ch = char_dict[char_id]
        if ch.description != '':
            p.append('<strong>%s</strong>: %s<br/>' % (ch.full_name, ch.description))
        else:
            p.append('<strong>%s</strong><br/>' % ch.full_name)
    return '\n'.join(p)
    
def format_play(play_paras, play_acts):
    """ Build a single play into one big list of formatted lines,
    which can later be split into sections """
    
    chapter_dict = hash_array(play_acts)
    lines = []

    # Calculate number of lines
    last_line = int(play_paras[-1].row[2])
    
    line_jump = 0
    last_act = None
    last_scene = None
    for row in play_paras:
            play = row.play()      
            ln = int(row.row[2])
            dialog = row.row[4]
            act = row.row[8]
            scene = row.row[9]
            if act != last_act or scene != last_scene:
                # "ACT"
                # "SCENE"
                # Insert this chapter
                f = FormatLine("<center><b>ACT {0}, SCENE {1}</b></center>".format(act, scene), ln)
                f.is_direction = True
                lines.append(f)
                desc = chapter_dict[ (act, scene) ]
                f = FormatLine("<center><b>{0}</b></center>".format(desc), ln)
                f.is_direction = True
                lines.append(f)
                
            if row.character() == 'xxx':
                # Stage direction
                # Split into chunks?
                lines.append(FormatLine('', ln))
                dlines = dialog.split('[p]')
                for d in dlines:
                    lines.append(FormatLine('<center><em>{}</em></center>'.format(d), ln))
            else:
                # Speech
                # Look up character name
                char_id = row.character()
                char_fullname = char_dict[char_id].short_name
                char_text = generate_char_link(playcode, char_id, char_fullname)

                anchor_link = generate_line_link(playcode, ln, '&gt;')
                f = FormatLine('<b>{0}</b>: {1}<br/>'.format(char_text, anchor_link), ln)
                f.char_id = char_id
                lines.append(f)

                # Text
                # TODO: if going to break, better in the middle
                dlines = dialog.split('[p]')
                for d in dlines:
                    d = d.rstrip()
                    f = FormatLine(d, ln)
                    f.char_id = char_id
                    lines.append(f)
                    ln += 1
                lines[-1].is_last_of_speech = True
                
                lines.append(FormatLine('', ln))
            last_act = act
            last_scene = scene
    return lines
    
def colour_breaks(lines):
    # Scan through to score elements
    # The score is the rating of how good it would be to break
    # **after** this line.
    
    def downscore_lines(start_line, line_inc, penalty, penalty_inc):
        to_downscore = start_line
        while penalty > 0 and to_downscore > 0 and to_downscore < len(lines):
            lines[to_downscore].score -= penalty
            penalty -= penalty_inc
            to_downscore += line_inc
    
    for x in range(0, len(lines)):
        # Check if we are starting a direction
        if x > 0 and lines[x].is_direction and not lines[x-1].is_direction:
            # x - 1 is a great place to break after (just before us)
            lines[x - 1].score += 100
            downscore_lines(x - 2, -1, 90, 3)
        if lines[x].is_direction and not lines[x + 1].is_direction:
            downscore_lines(x + 1, +1, 90, 4)
            
        if lines[x].is_direction:
            # Another really bad place to break
            lines[x].score -= 100
            
        # Colouring speeches:
        # Best to break at the end of a speech.
        # If we can't break at the end, ideally we want somewhere
        # in the middle?
        if lines[x].is_last_of_speech:
            lines[x].score += 20

    # Downscore the last lines of the play
    downscore_lines(len(lines) - 1, -1, 90, 3)
       
    return lines

def generate_play(our_play, playcode, char_dict, final_path, oss_path):
    html_base_path = os.path.join(daily_bard_settings.PUBLIC_HTML_PATH, playcode)

    os.makedirs(final_path)
    try:
        os.makedirs(html_base_path)
    except:
        pass

    def is_x(a):
        if a.play() == playcode:
            return True
        return False
        
    # Filter to 12th Night
    paras_in_play = filter(is_x, paras)
    acts_in_play = filter(is_x, acts)

    lines = format_play(paras_in_play, acts_in_play)
    colour_breaks(lines)
    
    # Split into chunks of N lines
    # Simplest possible atm
    base = 0
    readable_id = 1
    chunk_size = 50
    chunk_overlap = 100
    play_title = our_play.short_title()
    section_count = len(lines) / chunk_size
    line_count = len(lines)
    html_tmpl = templating.load('html_section.html')
    page_datas = []
    
    def format_row(x):
        return '   {}<br/>'.format(x.text)
        
    while base < line_count:
        # Choose the best endpoint
        start_range = min(base + chunk_size, line_count)
        end_range = min(base + chunk_size + chunk_overlap, line_count)
        best_score = -1000
        best_entry = start_range
        
        # The "score" is the likelihood to break
        for check in range(start_range, end_range):    # never reaches "end_range"
            this_score = lines[check].score
            if this_score >= best_score:  # Choose last equivalent
                best_entry = check
                best_score = this_score
        
        end = best_entry + 1
        
        print end, line_count
        text = [format_row(x) for x in lines[base:end]]
        char_ids = [x.char_id for x in lines[base:end]]

        # Words...
        final_text = '\n'.join(text)
        personae = generate_personae(char_dict, char_ids)
        
        # Generate pickle data
        line_id = lines[base].line_number

        page_data = { 'playcode' : playcode,
                      'short_title' : our_play.short_title(),
                      'full_title' : our_play.full_title(),
                      'line_id' : line_id,
                      'text' : final_text,
                      'personae' : personae,
                      'section_num' : readable_id,
                      'next_section_num' : readable_id + 1,
                      'url' : daily_bard_settings.WEBSITE_BASE_URL
                      }
        page_datas.append(page_data)
                
        # Move on to next, giving a little overlap
        base = end
        readable_id += 1

    section_count = readable_id - 1
    play_data = {
        'playcode' : playcode,
        'short_title' : our_play.short_title(),
        'full_title' : our_play.full_title(),
        'section_count' : section_count
        }
    # Pickle the play details
    pickle_filename = 'play.play'
    pickle_fh = open(os.path.join(final_path, pickle_filename), 'wb')
    pickle_dump = pickle.dump(play_data, pickle_fh, 0)
    pickle_fh.close()

    # Pickle each page
    for page_data in page_datas:
        section_id = page_data['section_num']
        page_data['section_total'] = section_count
        pickle_filename = 'section_%d.sect' % section_id
        pickle_fh = open(os.path.join(final_path, pickle_filename), 'wb')
        pickle_dump = pickle.dump(page_data, pickle_fh, 0)
        pickle_fh.close()

        # Create html
        html_filename = 'section_%d.html' % section_id
        html_fh = open(os.path.join(html_base_path, html_filename), 'wb')
        html_fh.write(templating.expand(html_tmpl, page_data))
        html_fh.close()

if __name__ == '__main__':
    import sys
    output_path = daily_bard_settings.SECTION_PATH
    oss_path = sys.argv[1]

    paras = read_into_array(os.path.join(oss_path, 'Paragraphs.txt'), Para)
    chars = read_into_array(os.path.join(oss_path, 'Characters.txt'), Character)
    acts = read_into_array( os.path.join(oss_path, 'Chapters.txt'),   Chapter)
    plays = read_into_array(os.path.join(oss_path, 'Works.txt'),      Play)

    char_dict = hash_array(chars)
    char_dict['xxx'] = ''

    play_dict = hash_array(plays)

    # Do all plays
    for playcode in daily_bard_settings.ALLOWED_PLAYCODES:
        print playcode
        our_play = play_dict[playcode]
        final_path = os.path.join(output_path, playcode)
        generate_play(our_play, playcode, char_dict, final_path, oss_path)
