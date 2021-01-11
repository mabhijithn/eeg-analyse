#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 17:43:56 2021

@author: Abhijith Mundanad Narayanan (mabhijithn@fastmail.com)
"""
import pyedflib
from scipy.io import loadmat
import numpy as np
import re
import os.path as path

def loadeeg(filename,filetype='EDF'):
    '''
    

    Parameters
    ----------
    filename : string/path
        path to EEG recording
    filetype : string, optional
        The type of EEG recording. The default is 'EDF'. Currently supported:
        TUSZ corpus format
        Options:
            'MAT' : MATLAB file format. The file should follow the following
            structure:
                a struct with following fields:
                    data : T X N matrix with T samples and N channels
                    fs: Sampling frequency (in Hz)
            'CURRY': EEG data recorded using Curry Neuro Imaging Suite by 
            Compumedics. There should be 3 files associated with a recording 
            with following extensions: '.dat','.rs3' and '.dap'. All three
            files should have the name and "this name" should be passed as
            the argument to the function.

    Returns
    -------
    eegdataDict: dict
        A dictionary with (at least) the following two keys
        data: numpy array of size T X N with T samples and N channels.
        fs: sampling frequency of the EEG data
    '''
    eegdataDict = {}
    eegdataDict['data'] = []
    eegdataDict['fs'] = 0
    eegdataDict['channels'] = {}
    if filetype=='EDF':
         # Open an EDF file 
         fp = pyedflib.EdfReader(filename)
                          
         num_chans = fp.signals_in_file
         labels_tmp = fp.getSignalLabels()
         labels = [str(lbl.replace(' ', '')) for lbl in labels_tmp]
         channames = []
         for label in labels:
             if 'EEG' in label:
                 robject = re.search('^EEG',label)
                 if robject:
                     strt = robject.span()[1]
                     stp = label.index('-')
                     chname = label[strt:stp]
                     channames.append(chname)
          # load each channel
         eegchans = len(channames)
         sig = []
         fsamp = []
         for i in range(eegchans):
             x = fp.readSignal(i)
             if i == 0:
                 data = np.reshape(x,(len(x),1))
             else:
                 x = np.reshape(x,(len(x),1))
                 data = np.append(data,x,axis=1)
             fsamp.append(fp.getSampleFrequency(i))
        
        # Extract sampling frequency
         fs = fsamp[_index(labels, 'FP1')]
         fp.close()
         channels = [{i: channames[i]} for i in range(len(channames))]
         
         eegdataDict['data'] = data
         eegdataDict['fs'] = fs
         eegdataDict['channels'] = channels
    elif filetype=='MAT':
        dataDict = loadmat(filename)
        for key in dataDict:
            robject = re.search('^__',key)
            if not robject:
                eegstruct = dataDict[key]
                break
        eegdata = eegstruct[0.0]
        if 'data' in eegdata:
            data = eegdata['data']
        else:
            raise Exception(r' "data" field not found in MAT file')
        if 'fs' in eegdata:
            fs = eegdata['fs']
        eegdataDict['data'] = data
        eegdataDict['fs'] = fs
    elif filetype=='CURRY':
        eegdataDict = loadcurryfile(filename)
    return eegdataDict

def loadcurryfile(filename):
    '''
    

    Parameters
    ----------
    filename : string/path
         path to EEG recording

    Returns
    -------
    eegdataDict: dict
        A dictionary with (at least) the following two keys
        data: numpy array of size T X N with T samples and N channels.
        fs: sampling frequency of the EEG data

    '''
    eegdataDict = {}
    eegdataDict['data'] = []
    eegdataDict['fs'] = 0
    eegdataDict['channels'] = {}
    eegdataDict['markers'] = []
    
    fileparts = filename.split('/')
    mainfilename = fileparts[-1]
    robject = re.search('.[a-z]+',mainfilename)
    if robject:
        mainfilename = mainfilename[:-4]   
    # Check for all the extensions of the EEG recording
    extns = ['dat','rs3','dap']
    for ext in extns:
        file = mainfilename+'.'+ ext
        filepath = '/'.join(fileparts[:-1])
        if not path.isfile(path.join(filepath,file)):        
            raise Exception( f'{file} not accessible/available.')
    # Extract meta data of the recording
    file = mainfilename+'.' + 'dap'
    f = open(path.join(filepath,file),'r')
    params = {}
    for line in f:
        line = line.strip()
        if '=' in line:
            linesplit = line.split('=')
            splits = [s.strip() for s in linesplit]
            params[splits[0]] = splits[1]
    f.close()
    
    #Extract channel/sensor info from rs3 file
    file = mainfilename+'.' + 'rs3'
    f = open(path.join(filepath,file),'r')
    channums = []
    channames = []
    numflag = 0
    nameflag = 0
    othernumflag = 0
    othernameflag = 0
    lastchan = 0
    for line in f:
        line = line.strip()
        if '#' in line:
            linesplit = line.split('#')
            line = linesplit[0].strip()
        if line=='NUMBERS END_LIST':
            numflag = 0
        if numflag==1:
            channums.append(int(line))
        if line=='NUMBERS START_LIST':
            numflag = 1
        
        if line=='LABELS END_LIST':
            nameflag = 0
        if nameflag==1:
            channames.append(line)
        if line=='LABELS START_LIST':
            nameflag = 1
            
        if line=='NUMBERS_OTHERS END_LIST':
            othernumflag = 0
        if othernumflag==1:        
            newchannum = int(line)+lastchan
            channums.append(newchannum)
        if line=='NUMBERS_OTHERS START_LIST':
            othernumflag = 1
            lastchan = channums[-1]
        
        if line=='LABELS_OTHERS END_LIST':
            othernameflag = 0
        if othernameflag==1:
            channames.append(line)
        if line=='LABELS_OTHERS START_LIST':
            othernameflag = 1
            
    f.close()
    channels = [{key:channames[count] for count,key in enumerate(channums)}]

    # Read data in dat file
    file = mainfilename+'.' + 'dat'
    data = np.fromfile(path.join(filepath,file), dtype='float32')
    nbchans = len(channums)
    nsamples = int(params['NumSamples'])
    ntrials = int(params['NumTrials'])
    newdata = data.reshape((nsamples*ntrials,nbchans))
    
    # Get trigger index
    idx = next((i for i,key in enumerate(channames) if key=='Trigger'),None)
    if idx is not None:
        markers = newdata[:,idx]
        data = np.delete(newdata,idx,axis=1)
    eegdataDict['data'] = data
    eegdataDict['fs'] = params['SampleFreqHz']
    eegdataDict['channels'] = channels
    eegdataDict['markers'] = markers
    eegdataDict['params'] = params
    return eegdataDict
    
def _index(labels, match):
    regex = re.compile('^EEG\ ?{}-(REF|LE)'.format(match))
    for i, item in enumerate(labels):
        if re.search(regex, item):
            return i