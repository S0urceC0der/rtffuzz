#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
import os
import sys
import json
import random
from random import choice


rtf = "{\\rtf1"
oo = "{\\*"
pp = "}"


def genrandomtagindex(len):
    index = []
    for i in range(0, len - 1):
        index.append(random.randint(0, 1700))
    return index


def genstarttagitem(obj, target, pp):
    group = []
    i = 0
    while i < len(pp):
        if obj == str(pp[i]["description"]) and target != i:
            cr = str(pp[i]["controlwd"])
            indexN = cr.find("N")
            if indexN != -1:
                value = genrandomvalue(1000)
                cr = cr[:indexN] + str(value)
            group.append(cr)
        i = i + 1
    return group


def getgrouptag(returntag):
    count = random.randint(len(returntag) / 2, len(returntag))
    slice1 = random.sample(returntag, count)
    tag = ""
    j = 0
    while len(slice1) > j:
        tag = tag + slice1[j]
        j = j + 1
    return tag


def genrandomvalue(max):
    return random.randint(0, max)


def generate_tag(tags, target_index):
    groups = []
    target_tag = tags[target_index]
    for index, tag in enumerate(tags):
        if index == target_index:
            continue
        if tag["description"] == target_tag["description"]:
            group_obj = tag["controlwd"]
            if group_obj.endswith("N"):
                group_obj = group_obj[:-1] + str(random.randint(0, 1000))
            groups.append(group_obj)

    random_count = random.randint(len(groups) / 2, len(groups))
    sliced_groups = random.sample(groups, random_count)
    return "".join(sliced_groups)

def run_fuzz(out_dir, gen_count):
    for i in range(gen_count):
        out_path = os.path.join(out_dir, str(i) + ".rtf")
        data = generate_rtf()
        with open(out_path, "wb") as f:
            f.write(data)


def generate_rtf():
    RTF_HEAD = "{\\rtf1"
    TAG_START = "{\\*"
    TAG_END = "}"
    tags = []
    item = ""
    with open("rtf.json", "r") as f_in:
        for line in f_in:
            tags.append(json.loads(line.strip()))
    # 生成随机序列
    tag_index_list = [random.randint(0, len(tags)) for c in range(10)]
    for tag_index in tag_index_list:
        if tags[tag_index]["type"] == "Destination":
            tag_name = TAG_START + str(tags[tag_index]["controlwd"])
            tag_name += generate_tag(tags, tag_index) + "}"
        else:
            tag_name = str(tags[tag_index]["controlwd"])
            if tag_name.endswith("N"):
                rand_int = random.randint(0, 1000)
                tag_name = tag_name[:-1] + str(rand_int)
        item = tag_name + item
    rtf_string = RTF_HEAD + item + "}"
    return rtf_string


def generate(obj, out_path):
    pp = []
    for line in obj:
        pp.append(json.loads(line.strip()))
    index = genrandomtagindex(len(pp))
    item = ""
    rtf = "{\\rtf1"
    oo = "{\\*"
    returntag = []
    selfgroup = ""
    filename = "filename"
    for i in index:
        cr = str(pp[i]["controlwd"])
        filename = cr
        indexN = cr.find("N")
        if indexN != -1:
            value = genrandomvalue(1000)
            cr = cr[:indexN] + str(value)
        if pp[i]["type"] == "Destination":
            cr = oo + str(pp[i]["controlwd"])
            returntag = genstarttagitem(pp[i]["description"], i, pp)
            selfgroup = getgrouptag(returntag)
            cr = cr + selfgroup + "}"
        item = cr + item
    # item=item+"}"
    rtf = rtf + item + "}"
    value = random.randint(0, 0x20000)

    file_name = filename + "%s" % value + ".rtf"
    out_file = os.path.join(out_path, file_name)
    print("Generate " + file_name)
    with open(out_file, "w") as f:
        f.write(rtf)


if __name__ == '__main__':
    if len(sys.argv) not in [2, 3]:
        print("Usage: python generate.py out_path [count]")
        sys.exit(0)
    out_path = sys.argv[1]
    if len(sys.argv) == 3:
        count = int(sys.argv[2])
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    run_fuzz(out_path, count)
