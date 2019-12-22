#!/usr/bin/env python
import argparse
from sys import version_info
import pandas as pd
from multiprocessing.pool import ThreadPool
from tqdm import tqdm  # pip3 install tqdm
from hashlib import md5
from os import getcwd
if version_info[0] < 3:
    from StringIO import StringIO
    from pathlib2 import Path  # pip2 install pathlib2
else:
    from io import StringIO
    from pathlib import Path
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

def download_fastq(df):
    index, row = df
    codename = row.name
    md5cheked = False
    while not md5cheked:
        listmd5 = []
        for pair, md5pair in zip(row['fastq_ftp'].split(';'), row['fastq_md5'].split(';')):
            outfile = projectoutpath / pair.split('/')[-1]
            if outfile.is_file() and md5(open(outfile,'rb').read()).hexdigest() == md5pair:
                listmd5.append(1)
            else:
                try:
                    urlretrieve('ftp://' + pair, outfile)
                except Exception as e:
                    listmd5.append(0)
                    break
                if md5(open(outfile,'rb').read()).hexdigest() == md5pair:
                    listmd5.append(1)
                else:
                    listmd5.append(0)
        if all(listmd5):
            md5cheked = True
    return '[OK] {}'.format(codename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--projects', type=str, nargs='*')
    parser.add_argument('-pfile', '--projectfile', type=str)
    parser.add_argument('-o', '--outfiles', type=str, default=getcwd() + '/' + 'ENA_out')
    parser.add_argument('-t', '--threads', type=int, default=12,
                        help='Number of threads to use (default 12)')
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s 1.0.4')
    args = parser.parse_args()
    xmlurl = 'http://www.ebi.ac.uk/ena/data/warehouse/filereport?accession={}&result=read_run'
    if args.projects:
        for projectid in args.projects:
            print('Starting with ' + projectid)
            outputpath = Path(args.outfiles)
            outputpath.mkdir(exist_ok=True, parents=True)
            projectout = outputpath/(projectid+'.tsv')
            projectoutpath = outputpath/projectid
            projectoutpath.mkdir(exist_ok=True, parents=True)
            if not projectout.is_file():
                local_filename, headers = urlretrieve(xmlurl.format(projectid), outputpath/(projectid+'.tsv'))
            df = pd.read_csv(projectout, sep='\t', index_col=5)
            t = ThreadPool(args.threads)
            genome = []
            for result in tqdm(t.imap_unordered(download_fastq, df.iterrows()),
                               total=len(df),
                               desc='Downloading Genomes using {} threads'.
                               format(args.threads), unit='Genomes', leave=False):
                genome.append(result)
            t.close()
            t.join()
    elif args.projectfile:
        projects = [line.rstrip('\n') for line in open(args.projectfile) if line.strip() != '']
        for projectid in projects:
            print('Starting with ' + projectid)
            outputpath = Path(args.outfiles)
            outputpath.mkdir(exist_ok=True, parents=True)
            projectout = outputpath/(projectid+'.tsv')
            projectoutpath = outputpath/projectid
            projectoutpath.mkdir(exist_ok=True, parents=True)
            if not projectout.is_file():
                local_filename, headers = urlretrieve(xmlurl.format(projectid), outputpath/(projectid+'.tsv'))
            df = pd.read_csv(projectout, sep='\t', index_col=5)
            t = ThreadPool(args.threads)
            genome = []
            for result in tqdm(t.imap_unordered(download_fastq, df.iterrows()),
                               total=len(df),
                               desc='Downloading Genomes using {} threads'.
                               format(args.threads), unit='Genomes', leave=False):
                genome.append(result)
            t.close()
            t.join()
    else:
        parser.print_help()
