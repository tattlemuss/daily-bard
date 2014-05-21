#!/bin/sh
BASE_DIR=$1
if [${BASE_DIR} -eq '']; then
    exit 1
fi
mkdir -p ${BASE_DIR}
rm ${BASE_DIR}/*.xml
python generate_rss.py "sections/12night" "${BASE_DIR}/atom_12night.xml" "Twelfth Night"
python generate_rss.py "sections/kinglear" "${BASE_DIR}/atom_kinglear.xml" "King Lear"
