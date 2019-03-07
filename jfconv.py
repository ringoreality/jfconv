#!/usr/bin/env python
# -*- coding: utf-8 -*-

#######################################################################
#                           all the imports                           #
#######################################################################

import os
import argparse
from tqdm import tqdm
from joblib import dump, load
from urllib.request import urlretrieve
from common import common

#######################################################################
#                           get dictionary                            #
#######################################################################

def get_dictionary():
    def parse_fp(fp, debug=False):
        operator = [None, None]
        operand = [None, None]
        js = []
        fs = []
        with open(fp, 'r', encoding='utf-8') as fi:
            for l in fi:
                if '(' not in l:
                    continue
                else:
                    for c in l.strip():
                        if c.isspace():
                            continue
                        if c in '【】()*[]':
                            operator.append(c)
                        else:
                            operand.append(c)
                        if operator[-2] == '【' and operator[-1] == '】':
                            operator = operator[:-2]
                            operand = []
                        if operator[-2] == '(' and operator[-1] == ')':
                            operator = operator[:-2]
                            j = operand[-1]
                            f = operand[-2]
                            if j is not None and f is not None:
                                js.append(j)
                                fs.append(f)
                            operand = operand[:-2]
                        if operator[-1] == '*' or operator[-1] == ']':
                            operator = [None, None]
                            operand = [None, None]
                        if debug:
                            print('c:', c)
                            print('operator:', operator)
                            print('operand:', operand)
                            print('js:', js)
                            print('fs:', fs)
                            wait = input()
        jf = {}
        fj = {}
        for i, (j, f) in enumerate(zip(js, fs)):
            # escape common chars, escape bad subsitutions like 乾坤 to 干坤
            if ord(j) != ord(f) and f not in common:
                jf[j] = f
                fj[f] = j
        return (jf, fj)
    dumpfile = 'dictionary.dump'
    if dumpfile in os.listdir('./'):
        dictionary = load(dumpfile)
    else:
        url = 'http://ws.moe.edu.tw/001/Upload/userfiles/%E6%A8%99%E6%BA%96%E5%AD%97%E5%B0%8D%E7%85%A7%E7%B0%A1%E5%8C%96%E5%AD%97.pdf'
        urlretrieve(url, 'dictionary.pdf')
        os.system('pdftotext -f 8 -l 92 -layout dictionary.pdf dictionary.txt')
        jf, fj = parse_fp('dictionary.txt')
        dictionary = {'jf': jf, 'fj': fj}
        dump(dictionary, dumpfile)
    return dictionary

#######################################################################
#                                conv                                 #
#######################################################################

def conv(args):
    assert (args.direction in set(['jf', 'fj'])), 'invalid conversion direction'
    mapper = dictionary[args.direction]
    if args.convert_quotation:
        if args.direction == 'fj':
            mapper['「'] = '“'
            mapper['」'] = '”'
        if args.direction == 'jf':
            mapper['“'] = '「'
            mapper['”'] = '」'
    with open(args.fp + '.' + args.direction, 'w') as fo:
        with open(args.fp, 'r', encoding='utf-8') as fi:
            for l in tqdm(fi) if args.verbose else fi:
                for c in l.strip():
                    if c not in mapper:
                        pass
                    else:
                        c = mapper[c]
                    fo.write(c)
                fo.write('\n')

#######################################################################
#                              argparse                               #
#######################################################################

dictionary = get_dictionary()
parser= argparse.ArgumentParser(
    description = 'convert between simplified and traditional Chinese',
    usage = """jfconv.py <fp> <direction> [<args>]"""
)
parser.add_argument('fp', type=str,
    help = 'path to the file to be converted')
parser.add_argument('direction', type=str,
    help = 'conversion direction, {jf|fj}')
parser.add_argument('--verbose', action='store_true',
    help = 'show a progress bar when converting')
parser.add_argument('--convert-quotation', action='store_true', dest='convert_quotation',
    help = 'convert between 「...」and “...”')
args = parser.parse_args()
conv(args)
