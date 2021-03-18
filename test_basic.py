#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 15:15:30 2021

@author: abhijith
"""
from eeganalyse import eegbasic, utils
from os import path

def test_fileloading():
    samplefile = path.join('sample-data', 'sample.mat')
    eegdataDict = eegbasic.loadeeg(samplefile, filetype='MAT')
    keys = list(eegdataDict.keys())
    assert len(keys)==3
    

