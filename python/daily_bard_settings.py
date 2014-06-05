# Global settings for dailybard

# URL of where the published site lives
WEBSITE_BASE_URL="http://www.clarets.org/daily-bard/"

# Relative path to where the generated section data goes
SECTION_PATH="../sections"

# Relative path where template files live
TEMPLATE_PATH="../templates"

# Output path to copy cgi scripts into
CGI_PATH="../cgiscripts"

# The set of plays we want to publish -- in the
# order we want them to appear in the index
ALLOWED_PLAYCODES=['kinglear', 'macbeth', '12night']

# Python executable path for stamping into CGI scripts
PATH_TO_PYTHON='/usr/bin/python'
    
# Set to True to allow CGI debug
IS_DEBUG=False