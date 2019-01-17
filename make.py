import matplotlib.pyplot as plt
import wordcloud as wc
import sys
from PIL import Image
import os
import json
import string

import re
from functools import partial

discard_endswith = []

names_involved = ["helen", "john","you"]
discard_startswith = ["{} sent".format(name) for name in names_involved]
discard_startswith += ["{} started sharing".format(name) for name in names_involved]
discard_endswith += ["{} started a call".format(name) for name in names_involved]
discard_endswith += ["{} joined the call".format(name) for name in names_involved]
discard_match = ["the video chat ended."]
discard_words = names_involved

def txt_from_fbdump(filepath):
        fix_mojibake_escapes = partial(
            re.compile(rb'\\u00([\da-f]{2})').sub,
            lambda m: bytes.fromhex(m.group(1).decode()))

        with open(filepath, 'rb') as binary_data:
            repaired = fix_mojibake_escapes(binary_data.read())
        data = json.loads(repaired.decode('utf8'))
        # get content
        messages = data['messages']
        if len(messages) == 1:
            # not a chat object, skip
            return None
        # lowercase
        content = []
        for d in messages:
            if 'content' in d:
                c = d['content'].lower()
                c = re.sub('['+string.punctuation+']', '', c)
                content.append(c)
        if discard_endswith:
                content = [c for c in content if not any([c.endswith(de) for de in discard_endswith])]
        if discard_startswith:
                content = [c for c in content if not any([c.startswith(de) for de in discard_startswith])]
        if discard_match:
                content = [c for c in content if c not in discard_match]
        content_str = " ".join(content)
        examine=""
        if examine and examine in content_str:
                i=content_str.index(examine)
                print(i, content_str[i-5:i+100])
        return content_str

def txt_from_fbdumpdir(dirpath):
    total_text = ""
    for filename in os.listdir(dirpath):
        filepath = os.path.join(dirpath, filename)
        if not os.path.isfile(filepath):
            continue
        print("Processing file {}".format(filepath))
        content = txt_from_fbdump(filepath)
        print("Text len: {}".format(len(total_text)))
        if content is not None:
            total_text += content
    return total_text



args = sys.argv[1:]
if len(args) > 1:
    txt = " ".join(args)
else:
    txt = ""
    if os.path.isdir(args[0]):
        txt = txt_from_fbdumpdir(args[0])
    else:
        txt = txt_from_fbdump(args[0])

if not txt:
    print("No chat text from file {}".format(args[0]))
    exit(1)
words = list(map(lambda w : w.lower(), txt.strip().split()))
words = list(filter(lambda x: x not in discard_words, words))

# remove stopwords
swpath = "./sw-"
for lang in ["greek", "english", "greeklish"]:
    sw = []
    with open(swpath + lang) as f:
        for line in f:
            sw.append(line.strip().lower())
    words = [t for t in words if t not in sw]

txt = " ".join(words)

www = wc.WordCloud(width=800,height=600).generate(txt)
plt.imshow(www, interpolation='bilinear')
plt.axis("off")
plt.show()
