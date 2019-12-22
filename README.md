[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI release](https://img.shields.io/pypi/v/ncbi-genome-download.svg)](https://pypi.python.org/pypi/getENA/)
# getENA
Sometimes we need to download a sequencing project from ENA; fortunately ENA offers in its platform a link to the 
file that we need. However, we can spend a lot of time downloading files manually if the amount of files is large.

I have developed a small project in Python to be able to do this work in an automated and parallel way to increase the performance.
## Installation
`pip install getENA`

Alternatively, from GitHub

`pip install git+https://github.com/EnzoAndree/getENA`
## Usage
Let's say I'm interested in _Clostridium perfringens_ sequencing projects, we have to search ENA for public sequencing projects at https://www.ebi.ac.uk/ena/browser/text-search?query=clostridium%20perfringens. Here, we choose the codes that we need, for example:

`PRJNA350702 PRJNA285473 PRJNA508810`

We have 2 options to download the FASTQ files, (1) add the project codes to the command line separated by spaces as an argument, or (2) make a file containing a list of all the project codes that need.

For the first option (recommended for few projects for example < 5) we run the following

`getENA.py -p PRJNA350702 PRJNA285473 PRJNA508810`

For the second option (recommended for many projects e.g. >= 5) we run the following

`getENA.py -pfile ena.list.txt`

Where ena.list.txt is the file containing a list of all the project codes.

If you want, you can increase the performance by increasing the number of reads that are downloaded in parallel (-t option). However, be careful, because ENA aborts the connection if it detects that you have many connections at the same time with its FTP. Empirically I have observed that 12 parallel connections work properly without ENA cancelling the download.

As a crazy example of many parallel connections of the above commands would be the following:

`getENA.py -t 64 -p PRJNA350702 PRJNA285473 PRJNA508810`

One of the main features of `getENA.py` is that it automatically confirms the integrity of the FASTQ file when you download it. If the connection is lost, if ENA cancels the connection or if the `getENA.py` is stopped, you can run the program again and restart the download without losing the files that were already downloaded.

# Licence

[GPL v3](https://raw.githubusercontent.com/EnzoAndree/getENA/master/LICENSE)

## Author

* Enzo Guerrero-Araya
* Twitter: [@eguerreroaraya](https://twitter.com/eguerreroaraya)
