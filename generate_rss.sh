#!/bin/sh
mkdir -p public_html/daily-bard
python generate_rss.py "sections/kinglear" "public_html/daily-bard/atom_kinglear.xml" "King Lear"
