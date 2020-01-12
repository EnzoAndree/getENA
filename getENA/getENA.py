#!/usr/bin/env python
import argparse
from sys import version_info
import pandas as pd
from multiprocessing.pool import ThreadPool
from tqdm import tqdm  # pip3 install tqdm
from hashlib import md5
from itertools import repeat
from os import getcwd
from re import compile
if version_info[0] < 3:
    from StringIO import StringIO
    from pathlib2 import Path  # pip2 install pathlib2
else:
    from io import StringIO
    from pathlib import Path
try:
    from urllib.request import urlretrieve
    from urllib.error import (ContentTooShortError, URLError)
except ImportError:
    from urllib import urlretrieve
    from urllib.error import (ContentTooShortError, URLError)

def download_fastq(inputdata):
    df, outpath = inputdata
    index, row = df
    codename = row.name
    md5cheked = False
    while not md5cheked:
        listmd5 = []
        for pair, md5pair in zip(row['fastq_ftp'].split(';'), row['fastq_md5'].split(';')):
            outfile = outpath / pair.split('/')[-1]
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

def urlretrieve_converter(url_path, attmp=0):
    if attmp > 15:
        print('Error', *url_path)
        return False
    try:
        return urlretrieve(*url_path)
    except ContentTooShortError as e:
        print('Retry {}/15'.format(attmp + 1), *url_path)
        urlretrieve_converter(url_path, attmp + 1)
    except URLError as e:
        print('Retry {}/15'.format(attmp + 1), *url_path)
        urlretrieve_converter(url_path, attmp + 1)

if __name__ == '__main__':
    V = '%(prog)s v1.2.2'
    parser = argparse.ArgumentParser(description='Download FASTQ files from ENA ({})'.format(V))
    parser.add_argument('-acc', '--acc', type=str, nargs='*')
    parser.add_argument('-accfile', '--accfile', type=str)
    parser.add_argument('-tax', '--taxid', type=str, nargs='*')
    parser.add_argument('-o', '--outfiles', type=str, default=getcwd() + '/' + 'ENA_out')
    parser.add_argument('-t', '--threads', type=int, default=12,
                        help='Number of threads to use (default 12)')
    parser.add_argument('-V', '--version', action='version',
                        version=V)
    args = parser.parse_args()
    xmlurl = 'http://www.ebi.ac.uk/ena/data/warehouse/filereport?accession={}&result=read_run'
    if args.acc:
        outputpath = Path(args.outfiles)
        tmpoutputpath = outputpath/'tmp'
        tmpoutputpath.mkdir(exist_ok=True, parents=True)
        accurl = [xmlurl.format(accid) for accid in args.acc]
        accout = [tmpoutputpath/(accid+'.tsv') for accid in args.acc]
        metadata = []
        multipleargs = [(u, a) for (u, a) in zip(accurl, accout) if not a.is_file()]
        with ThreadPool(args.threads) as p:
            for result in tqdm(p.imap_unordered(urlretrieve_converter, multipleargs), total=len(multipleargs), desc='Downloading metadatas using {} threads'.format(args.threads), unit='metadatas'):
                metadata.append(result)
        frames = [pd.read_csv(tsv, sep='\t', index_col=5) for tsv in accout]
        concat_frames = pd.concat(frames, ignore_index=True)
        genome = []
        with ThreadPool(args.threads) as p:
            multipleargs = list(zip(concat_frames.iterrows(), repeat(outputpath)))
            for result in tqdm(p.imap_unordered(download_fastq, multipleargs), total=len(multipleargs), desc='Downloading Genomes using {} threads'.format(args.threads), unit='Genomes'):
                genome.append(result)
        concat_frames.to_csv(outputpath/'metadata.tsv', index=False, sep='\t')
    elif args.accfile:
        accs = [line.rstrip('\n') for line in open(args.accfile) if line.strip() != '']
        outputpath = Path(args.outfiles)
        tmpoutputpath = outputpath/'tmp'
        tmpoutputpath.mkdir(exist_ok=True, parents=True)
        accurl = [xmlurl.format(accid) for accid in accs]
        accout = [tmpoutputpath/(accid+'.tsv') for accid in accs]
        metadata = []
        multipleargs = [(u, a) for (u, a) in zip(accurl, accout) if not a.is_file()]
        with ThreadPool(args.threads) as p:
            for result in tqdm(p.imap_unordered(urlretrieve_converter, multipleargs), total=len(multipleargs), desc='Downloading metadatas using {} threads'.format(args.threads), unit='metadatas'):
                metadata.append(result)
        frames = [pd.read_csv(tsv, sep='\t', index_col=5) for tsv in accout]
        concat_frames = pd.concat(frames, ignore_index=True)
        genome = []
        with ThreadPool(args.threads) as p:
            multipleargs = list(zip(concat_frames.iterrows(), repeat(outputpath)))
            for result in tqdm(p.imap_unordered(download_fastq, multipleargs), total=len(multipleargs), desc='Downloading Genomes using {} threads'.format(args.threads), unit='Genomes'):
                genome.append(result)
        concat_frames.to_csv(outputpath/'metadata.tsv', index=False, sep='\t')
    elif args.taxid:
        regex = r'<URL>(ftp://.*fasta\.gz)</URL>'
        rgx = compile(regex)
        xmltaxid = 'https://www.ebi.ac.uk/ena/browser/api/xml/links/taxon?accession={}&result=assembly&subtree=true'
        outputpath = Path(args.outfiles)
        tmpoutputpath = outputpath/'tmp'
        tmpoutputpath.mkdir(exist_ok=True, parents=True)
        accurl = [xmltaxid.format(tax) for tax in args.taxid]
        accout = [tmpoutputpath/('tax_'+tax+'.xml') for tax in args.taxid]
        metadata = []
        multipleargs = [(u, a) for (u, a) in zip(accurl, accout)if not a.is_file()]
        with ThreadPool(args.threads) as p:
            for result in tqdm(p.imap_unordered(urlretrieve_converter, multipleargs), total=len(multipleargs), desc='Downloading metadatas using {} threads'.format(args.threads), unit='metadatas'):
                metadata.append(result)
        taxs = tmpoutputpath.glob('tax_*.xml')
        fastas = []
        for t in taxs:
            with open(t) as file:
                data = file.read()
                assemblies = rgx.finditer(data)
                for assemblie in assemblies:
                    fastas.append(assemblie.group(1))
        genomeoutputpath = outputpath/'genomes'
        genomeoutputpath.mkdir(exist_ok=True, parents=True)
        accout = [genomeoutputpath/(fasta.split('/')[-1]) for fasta in fastas]
        metadata = []
        multipleargs = [(u, a) for (u, a) in zip(fastas, accout)]
        with ThreadPool(args.threads) as p:
            for result in tqdm(p.imap_unordered(urlretrieve_converter, multipleargs), total=len(multipleargs), desc='Downloading genomes using {} threads'.format(args.threads), unit='metadatas'):
                metadata.append(result)

    else:
        parser.print_help()
