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
    def __init__(self, text, ln, is_start=False):
        self.text = text
        self.score = 0
        self.line_number = ln
        self.is_start = is_start

class NormalLine:
    def __init__(self, row):
        self.row = row
        
class Character:
    def __init__(self, row):
        self.row = row
    def key(self):
        return self.row[0]
    def value(self):
        return self.row[2]
    
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
        
def hash_array(array):
    res = {}
    for row in array:
        res[ row.key() ] = row.value()
    return res
    
def read_into_array(filename, classname):
    array = []
    fh = open(filename, 'rb')
    spamreader = csv.reader(fh, delimiter=',', quotechar='~')
    for row in spamreader:
        array.append(classname(row))
    fh.close()
    return array
    
def format_play(play_paras, play_acts):
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
            if act != last_act:
                # "ACT"
                # Insert this chapter
                formatted_lines.append(FormatLine("<center><b>{0}</b></center><br/>".format("ACT " + act), ln, True))
            if scene != last_scene:
                # "SCENE"
                # Insert this chapter
                formatted_lines.append(FormatLine("<center><b>{0}</b></center><br/>".format("SCENE " + scene), ln, True))
                desc = chapter_dict[ (act, scene) ]
                formatted_lines.append(FormatLine("<center><b>{0}</b></center><br/>".format(desc), ln, True))
                
            if row.character() == 'xxx':
                # Stage direction
                # Split into chunks?
                formatted_lines.append(FormatLine("<br/><center><em>{}</em></center><br/>".format(dialog), ln, True))
            else:
                # Speech
                # Look up character name
                character = char_dict[row.character()]
                formatted_lines.append(FormatLine("<b>{0}</b>:<br/>".format(character), ln, True))

                # Text
                dlines = dialog.split('[p]')
                for d in dlines:
                    d = d.rstrip()
                    formatted_lines.append(FormatLine("{0}<br/>".format(d), ln, True))
                    ln += 1

                formatted_lines.append(FormatLine('<br/>', ln))
            last_act = act
            last_scene = scene

    return formatted_lines

def generate_play(playcode, output_path, oss_path):
    def is_x(a):
        if a.play() == playcode:
            return True
        return False
        
    # Filter to 12th Night
    para12 = filter(is_x, paras)
    acts12 = filter(is_x, acts)

    formatted_lines = format_play(para12, acts12)

    # Split into chunks of N lines
    # Simplest possible atm
    base = 0
    chunk_id = 1
    chunk_size = 50
    while base < len(formatted_lines):

        end = base + chunk_size + 10 # add 10 lines of overlap for next time...
        text = [x.text for x in formatted_lines[base:end]]
        final_text = '\n'.join(text)

        # Generate pickle data
        line_id = formatted_lines[base].line_number
        page_data = { "playcode" : playcode,
                      "line_id" : line_id,
                      "text" : final_text
                      }
        pickle_filename = "section_%d.pck" % (chunk_id)
        pickle_fh = open(os.path.join(output_path, pickle_filename), 'wb')
        pickle_dump = pickle.dump(page_data, pickle_fh, 0)
        pickle_fh.close()
        
        base += chunk_size
        chunk_id += 1

            
if __name__ == '__main__':
    import sys
    playcode = sys.argv[1]
    output_path = sys.argv[2]
    oss_path = sys.argv[3]

    paras = read_into_array(os.path.join(oss_path, 'Paragraphs.txt'), Para)
    chars = read_into_array(os.path.join(oss_path, 'Characters.txt'), Character)
    acts = read_into_array( os.path.join(oss_path, 'Chapters.txt'),   Chapter)
    char_dict = hash_array(chars)
    char_dict['xxx'] = ''

    generate_play(playcode, output_path, oss_path)
    
