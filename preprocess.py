# read comment xml files and extract, process, save data
# Python2

import os
import numpy as np
import xml.etree.ElementTree as ET

from natto import MeCab

from collections import Counter
from collections import OrderedDict

def read_xml(path):
    return ET.fromstring(open(path, 'r').read())

def extract_data(root):
    d = {k:[] for k in ['date', 'no', 'vpos', 'text']}# unixtime, number, 1 / 100 sec
    for r in root:
        if not r.text == None:
            for k in d.keys():
                if k == 'text':
                    d[k].append(r.text)
                else:
                    d[k].append(int(r.attrib[k])) 
    return d

def uniq_by_key(data, k='no'):
    d = {n: i for i, n in enumerate(data[k])}
    uniq_data = {k:[] for k in data.keys()}
    for i in d.values():
        for k in data.keys():
            uniq_data[k].append(data[k][i])
    return uniq_data

def load_all_comments(comment_path):
    comment_file_name = os.listdir(comment_path)
    data = {k:[] for k in ['date', 'no', 'vpos', 'text']}
    for name in comment_file_name:
        xml = read_xml(comment_path + name)
        _data = extract_data(xml)
        for k, v in _data.iteritems():
            data[k].extend(v)
    data = uniq_by_key(data)
    return data

def get_tokens(text):
    mecab = MeCab()
    tokens = []
    pos_word_dict = {}
    for t in text:
        res_raw = mecab.parse(t.encode('utf-8'))
        res = [r.split('\t') for r in res_raw.split('\n')]
        res = [r for r in res if len(r) == 2]
        res = [[r[0], r[1].split(',')[0]] for r in res]

        for r in res:
            if r[1] in pos_word_dict:
                pos_word_dict[r[1]].append(r[0])
            else:
                pos_word_dict[r[1]] = [r[0]]
        tokens.append(' '.join([r[0] for r in res]))
    return tokens, pos_word_dict

def make_dict(tokens=None, from_word_list=False, dict_count=None):
    if dict_count == None:
        if from_word_list:
            w_list = tokens
        else:
            w_list = [w for token in tokens for w in token]
        dict_count = Counter(w_list)
    dict_ordered_by_count = OrderedDict(sorted(dict_count.items(), key = lambda x:x[0]))
    dict_ordered_by_count = OrderedDict(sorted(dict_ordered_by_count.items(), key = lambda x:-x[1]))
    wordtoix = {k:i for i,k in enumerate(dict_ordered_by_count.keys())}
    ixtoword = {vv:kk for kk, vv in wordtoix.iteritems()}
    return wordtoix, ixtoword, dict_count, dict_ordered_by_count

def make_dict_and_save(pos_word_dict):
    all_word_count = Counter([])
    for k, v in pos_word_dict.iteritems():
        wordtoix, ixtoword, dict_count, dict_ordered_by_count = make_dict(v, from_word_list=True)
        all_word_count += dict_count
        d = {   'wordtoix':wordtoix, 'ixtoword':ixtoword, 'dict_count':dict_count,
                'dict_ordered_by_count':dict_ordered_by_count}
        for _k, _v in d.iteritems():np.save(save_path + 'dict/' + _k + '_' + k, _v)

    wordtoix, ixtoword, dict_count, dict_ordered_by_count = make_dict(dict_count=all_word_count)
    d = {   'wordtoix':wordtoix, 'ixtoword':ixtoword, 'dict_count':dict_count,
            'dict_ordered_by_count':dict_ordered_by_count}
    for k, v in d.iteritems():np.save(save_path + 'dict/' + k + '_all', v)

comment_path = 'commtents/gochiusa/raw/'
save_path = 'commtents/gochiusa/extracted/'
data = load_all_comments(comment_path)
for k, v in data.iteritems():np.save(save_path + k, v)

tokens, pos_word_dict = get_tokens(data['text'])
np.save(save_path + 'tokens', tokens)

make_dict_and_save(pos_word_dict)

# check
dict_ordered_by_count = np.load('commtents/gochiusa/extracted/dict/dict_ordered_by_count_名詞.npy')[None][0]
for s in dict_ordered_by_count.items()[:100]: print s[0], s[1]
counts = [s[1] for s in dict_ordered_by_count.items()]
total_word_num = sum(counts)

import datetime
print datetime.datetime.fromtimestamp(min(data['date']))

