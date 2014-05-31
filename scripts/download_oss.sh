#!/bin/sh

# Download zip file
curl http://opensourceshakespeare.com/downloads/oss-textdb.zip > oss-textdb.zip

# Extract
unzip oss-textdb.zip -d ../oss

