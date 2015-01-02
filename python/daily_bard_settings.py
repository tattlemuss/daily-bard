# Global settings for dailybard

# URL of where the published site lives
WEBSITE_BASE_URL='http://www.clarets.org/daily-bard/'

# Relative path to where the generated section data goes
SECTION_PATH='../sections'

# Relative path where template files live
TEMPLATE_PATH='../templates'

# Relative path to put generated HTML pages
PUBLIC_HTML_PATH='../public_html'

# Output path to copy cgi scripts into
CGI_PATH='../cgiscripts'

# The set of plays we want to publish -- in the
# order we want them to appear in the index
ALLOWED_PLAYCODES=[
    'allswell',
    'antonycleo',
    'asyoulikeit',
    'comedyerrors',
    'coriolanus',
    'cymbeline',
    'hamlet',
    'henry4p1',
    'henry4p2',
    'henry5',
    'henry6p1',
    'henry6p2',
    'henry6p3',
    'henry8',
    'juliuscaesar',
    'kingjohn',
    'kinglear',
    'loveslabours',
    'macbeth',
    'measure',
    'merchantvenice',
    'merrywives',
    'midsummer',
    'muchado',
    'othello',
    'richard2',
    'richard3',
    'romeojuliet',
    'tamingshrew',
    'tempest',
    'timonathens',
    'titus',
    'troilus',
    '12night',
    'twogents',
    'venusadonis',
    'winterstale']

# Python executable path for stamping into CGI scripts
PATH_TO_PYTHON='/usr/bin/env python'
    
# Set to True to allow CGI debug
IS_DEBUG=False