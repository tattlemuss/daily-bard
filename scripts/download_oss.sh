#!/bin/sh

# Download zip file
curl http://opensourceshakespeare.com/downloads/oss-textdb.zip > oss-textdb.zip

# Extract
unzip -o oss-textdb.zip -d ../oss

rm oss-textdb.zip

