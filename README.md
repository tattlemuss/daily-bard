Our Daily Bard
==============
Give us this day our daily bard. Shakespeare plays serialized into RSS content.

Some scripts to create daily RSS feed from the content on http://opensourceshakespeare.com/

This code is designed to run on bare-bones Unix system needing very minimal dependencies:

* [Curl](http://curl.haxx.se/) (only to download the corpus)
* Python 2.x to generate the data
* Any webserver (e.g. Apache) that can run CGI scripts.

How to use
==========
Copy the repository to somewhere on your server,

* `cd scripts`
* Run `./download_oss.sh` to pull down a version of OSS using curl and place in oss/
* Run `./generate_sections.sh` to read the OSS database and write out sections for each work into sections/
* Use `./publish_cgi.sh <dest directory>` to stamp the CGI files and copy them into web-accessible areas. These CGI scripts read the data written into `sections/`, plus the template text in `templates`.

The section data can remain in an area not publicly visible (depending on what setup your webserver supports.)

You can see this code in action at [http://www.clarets.org/daily-bard](http://www.clarets.org/daily-bard)



