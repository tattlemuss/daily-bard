"""
    Script which loads in the OSS databases, splits a
    play into fixed-size sections, and serialises the
    sections into files.
"""
import csv
import sys
import os
import pickle

class FormatLine:
    def __init__(self, text, ln, is_end=False):
        self.text = text
        self.score = 0
        self.line_number = ln
        self.is_end = is_end
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

OSS_URL="http://www.opensourceshakespeare.org" 

def generate_site_link(playcode):
    text = "Text from Open Source Shakespeare";
    return "<a href=\"{0}/views/plays/play_view.php?WorkID={1}\">{2}</a>".format(OSS_URL, playcode, text)

def generate_line_link(playcode, line_id, text):
    return "<a href=\"{0}/views/plays/play_view.php?WorkID={1}#{2}\">{3}</a>".format(OSS_URL, playcode, line_id, text)
    
def generate_char_link(playcode, char_id, text):
    return "<a href=\"{0}/views/plays/characters/charlines.php?CharID={1}&WorkID={2}\">{3}</a>".format(OSS_URL, char_id, playcode, text)

def generate_personae(char_dict, char_ids):
    """ Generate text for all the characters supplied in the "char_ids" list """
    unique_ids = unique(char_ids)
    p = []
    p.append("In this episode:<br/>")
    
    unique_ids.sort()
    for char_id in unique_ids:
        ch = char_dict[char_id]
        if ch.description != '':
            p.append("<strong>%s</strong>: %s<br/>" % (ch.full_name, ch.description))
        else:
            p.append("<strong>%s</strong><br/>" % ch.full_name)
            
    return '\n'.join(p)
    
def format_play(play_paras, play_acts):
    """ Build a single play into one big list of formatted lines,
    which can later be split into sections """
    
    chapter_dict = hash_array(play_acts)
    formatted_lines = []

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
                formatted_lines.append(FormatLine("<center><b>ACT {0}, SCENE {1}</b></center><br/>".format(act, scene), ln))
                desc = chapter_dict[ (act, scene) ]
                formatted_lines.append(FormatLine("<center><b>{0}</b></center><br/>".format(desc), ln))
                
            if row.character() == 'xxx':
                # Stage direction
                # Split into chunks?
                formatted_lines.append(FormatLine("<br/>", ln))
                dlines = dialog.split('[p]')
                for d in dlines:
                    formatted_lines.append(FormatLine("<center><em>{}</em></center><br/>".format(d), ln))
            else:
                # Speech
                # Look up character name
                char_id = row.character()
                char_fullname = char_dict[char_id].short_name
                char_text = generate_char_link(playcode, char_id, char_fullname)

                anchor_link = generate_line_link(playcode, ln, "&gt;")
                f = FormatLine("<b>{0}</b>: {1}<br/>".format(char_text, anchor_link), ln)
                f.char_id = char_id
                formatted_lines.append(f)

                # Text
                dlines = dialog.split('[p]')
                for d in dlines:
                    d = d.rstrip()
                    f = FormatLine("{0}<br/>".format(d), ln, False)
                    f.char_id = char_id
                    formatted_lines.append(f)
                    ln += 1

                # Mark the last line of dialog as "is_end"
                formatted_lines.append(FormatLine('<br/>', ln))
                formatted_lines[-1].is_end = True
            last_act = act
            last_scene = scene
    return formatted_lines

def generate_play(our_play, playcode, char_dict, final_path, oss_path):
    os.makedirs(final_path)
    def is_x(a):
        if a.play() == playcode:
            return True
        return False
        
    # Filter to 12th Night
    paras_in_play = filter(is_x, paras)
    acts_in_play = filter(is_x, acts)
    formatted_lines = format_play(paras_in_play, acts_in_play)
    
    # Split into chunks of N lines
    # Simplest possible atm
    base = 0
    readable_id = 1
    chunk_size = 75
    chunk_overlap = 20
    play_title = our_play.short_title()
    section_count = len(formatted_lines) / chunk_size
    line_count = len(formatted_lines)
    while base < line_count:
        # Scan down to find next "end"
        check = base + chunk_size
        end_range = min(base + chunk_size + chunk_overlap, line_count)
        while check < end_range:
            if formatted_lines[check].is_end:
                break
            check += 1
                
        end = check
        text = [x.text for x in formatted_lines[base:end]]
        char_ids = [x.char_id for x in formatted_lines[base:end]]

        # Words...
        final_text = '\n'.join(text)

        personae = generate_personae(char_dict, char_ids)
        
        # ... footer (use rss?)
        final_text += generate_site_link(playcode)
    
        # Generate pickle data
        line_id = formatted_lines[base].line_number

        url = "http://www.opensourceshakespeare.org/views/plays/play_view.php?WorkID=%s#%d" % (playcode, line_id)
        url_title = "%s (%d/%d)" % (play_title, readable_id, section_count)
        
        page_data = { "playcode" : playcode,
                      "line_id" : line_id,
                      "text" : final_text,
                      "personae" : personae,
                      "url" : url,
                      "title" : url_title
                      }
        pickle_filename = "section_%d.sect" % (readable_id)
        pickle_fh = open(os.path.join(final_path, pickle_filename), 'wb')
        pickle_dump = pickle.dump(page_data, pickle_fh, 0)
        pickle_fh.close()
        
        # Move on to next, giving a little overlap
        base = end + 1
        readable_id += 1

    # Pickle the play details
    play_data = {
        'playcode' : playcode,
        'short_title' : our_play.short_title(),
        'full_title' : our_play.full_title(),
        'section_count' : readable_id
        }
    pickle_filename = "play.play"
    pickle_fh = open(os.path.join(final_path, pickle_filename), 'wb')
    pickle_dump = pickle.dump(play_data, pickle_fh, 0)
    pickle_fh.close()
            
if __name__ == '__main__':
    import sys
    output_path = sys.argv[1]
    oss_path = sys.argv[2]

    paras = read_into_array(os.path.join(oss_path, 'Paragraphs.txt'), Para)
    chars = read_into_array(os.path.join(oss_path, 'Characters.txt'), Character)
    acts = read_into_array( os.path.join(oss_path, 'Chapters.txt'),   Chapter)
    plays = read_into_array(os.path.join(oss_path, 'Works.txt'),      Play)

    char_dict = hash_array(chars)
    char_dict['xxx'] = ''

    play_dict = hash_array(plays)

    # Do all plays
    for playcode in play_dict.keys():
        print playcode
        our_play = play_dict[playcode]
        final_path = os.path.join(output_path, playcode)
        generate_play(our_play, playcode, char_dict, final_path, oss_path)
    
