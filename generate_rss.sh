#!/bin/sh
BASE_DIR=$1
if [${BASE_DIR} -eq '']; then
    exit 1
fi
mkdir -p ${BASE_DIR}
rm ${BASE_DIR}/*.xml
python generate_rss.py "sections/" ${BASE_DIR} "12night"
python generate_rss.py "sections/" ${BASE_DIR} "kinglear"
python generate_rss.py "sections/" ${BASE_DIR} "macbeth"

