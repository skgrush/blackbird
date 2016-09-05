#!/usr/bin/env python

import hashlib

def md5(path,blockmult=4):
    blockmult=int(blockmult)
    if blockmult <= 0:
        blockmult = 4
    grabsz = 128 * blockmult
    
    hashm = hashlib.md5()
    with open(path,'rb') as ofile:
        for chunk in iter(lambda: ofile.read(grabsz), ''):
            hashm.update(chunk)
    
    return hashm.hexdigest()

md5_default = '0'*20
