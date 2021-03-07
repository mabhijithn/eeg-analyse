#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Abhijith Mundanad Narayanan (mabhijithn@fastmail.com)
"""

from scipy.signal import butter, filtfilt
import resampy

def butter_bandpass(lowcut, highcut, fs, order=5):
    '''
    Create butterworth IIR bandpass filter with cutoff lowcut 
    and highcut

    Parameters
    ----------
    lowcut : float
        Low cut-off (Hz) of band pass filter
    highcut : float
        High cut-off (Hz) of band pass filter
    fs: float
        Sampling frequency of filter
    order: int
        Order of the filter

    Returns
    -------
    b: float
        Numerator coefficients of Butterworth IIR fiter
    a: float
        Denominator coefficients of Butterworth IIR fiter
    '''     
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def apply_bandpass_filter(data, lowcut, highcut, fs, order=5):
    '''
    Apply butterworth bandpass filter with cutoff lowcut (Hz)
    and highcut (Hz) on numpy array data
    
    Parameters
    ----------
    data: numpy array
        Shape (number of channels X number of samples). Note that time samples are on the second
        dimension
    lowcut : float
        Low cut-off (Hz) of band pass filter
    highcut : float
        High cut-off (Hz) of band pass filter
    fs: float
        Sampling frequency of filter
    order: int
        Order of the filter
    
    Returns
    -------
    
    y: numpy array
        Bandpass filtered data.
    '''
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def resample_data(data, fs, fs_new):
    '''
    Apply resample function of resampy module on data
    
    
    Parameters
    ----------
    data: numpy array
        Shape (number of channels X number of samples). Note that time samples are on the second
        dimension
    fs: float
        Original sampling frequency of data
    fs_new: float
        Downsample frequency
        
    
    Returns
    -------
    
    y: numpy array
        Resampled data.
    '''
    
    y = resampy.resample(data, fs, fs_new, filter='kaiser_best')
    return y