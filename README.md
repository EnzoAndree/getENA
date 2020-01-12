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
Let's say I'm interested in _Clostridium perfringens_ sequencing projects; we have to search ENA for public sequencing projects at https://www.ebi.ac.uk/ena/browser/text-search?query=clostridium%20perfringens. Here, we choose the codes that we need, for example:

`PRJNA350702 PRJNA285473 PRJNA508810`

We have 2 options to download the FASTQ files, (1) add the project codes to the command line separated by spaces as an argument, or (2) make a file containing a list of all the project codes that need.

For the first option (recommended for few projects, e.g. >= 5) we run the following

`getENA.py -acc PRJNA350702 PRJNA285473 PRJNA508810`

For the second option (recommended for many projects, e.g. >= 5) we run the following

`getENA.py -accfile ena.list.txt`

Where ena.list.txt is the file containing a list of all the project codes.

Instead, if you only want to download a few selected genomes from the project, simply add the run_accession as a parameter

`getENA.py -acc SRR096826 SRR8867692 SRR7601184`


If you want, you can increase the performance by increasing the number of reads that are downloaded in parallel (-t option). However, be careful, because ENA aborts the connection if it detects that you have many connections at the same time with its FTP. Empirically I have observed that 12 parallel connections work properly without ENA cancelling the download.

As a crazy example of many parallel connections of the above commands would be the following:

`getENA.py -t 64 -acc PRJNA350702 PRJNA285473 PRJNA508810`

One of the main features of `getENA.py` is that it automatically confirms the integrity of the FASTQ file when you download it. If the connection is lost, if ENA cancels the connection or if the `getENA.py` is stopped, you can run the program again and restart the download without losing the files that were already downloaded.

By default the output directory of `getENA.py` is a folder called ENA_out in the current directory. It can be modified with the -o argument. For example:

`getENA.py -o Cperfringens -t 64 -acc PRJNA350702 PRJNA285473 PRJNA508810`


# Output files

The scheme of the files and folders created follows the next format:

``` 
|ENA_out
|-- metadata.tsv
|-- ERR0001_1.fastq.gz
|-- ERR0001_2.fastq.gz
|-- ...
|-- ERR0009_1.fastq.gz
|-- ERR0009_2.fastq.gz
|-- tmp
|---- PRJNA350702.tsv
|---- PRJNA285473.tsv
|---- PRJNA508810.tsv

```

Where `PRJNA350702.tsv`, `PRJNA285473.tsv` and `PRJNA508810.tsv` are the metadata of selected projects and `metadata.tsv` is a merge of this three files. The folder `ENA_out`, contain all FASTQ file of each project

If you only want to get the assemblies reported in ENA, you can get all the FASTA files for a given taxon ID. In this case the taxon id of _Clostridium perfringens_ is `1502`. So the command line to download all assemblies of this species is:

`python getENA.py -o Cperfringens -tax 1502`

This command line will generate a `genomes` directory within the Cperfringens folder where all assemblies reported to date are placed

# Licence

[GPL v3](https://raw.githubusercontent.com/EnzoAndree/getENA/master/LICENSE)

## Author

* Enzo Guerrero-Araya
* Twitter: [@eguerreroaraya](https://twitter.com/eguerreroaraya)
