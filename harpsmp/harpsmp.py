# Copyright 2018 João Faria
#
# This file is part of harpsmp.
#
# harpsmp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# harpsmp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with harpsmp. If not, see <https://www.gnu.org/licenses/>.


import os
import re
from glob import glob
import urllib.request
import requests
import numpy as np 
import matplotlib.pyplot as plt

this_dir = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(this_dir, '..', 'data')

# def get_star_name_from_path(full_path):
#     """ Return the name of the star (works for standard HARPS filenames) """
#     bn = os.path.basename(full_path)
#     pattern = '|'.join(['HD\d+', 'HIP\d+', 'HR\d+', 'BD-\d+', 'CD-\d+',
#                         'NGC\d+No\d+', 'GJ\d+', 'Gl\d+'])
#     return re.findall(pattern, bn)[0]


def url_is_alive(url):
    """ Checks that a given URL is reachable. """
    request = urllib.request.Request(url)
    request.get_method = lambda: 'HEAD'
    try:
        urllib.request.urlopen(request)
        return True
    except urllib.request.HTTPError:
        return False

def get_file(url):
    """ Get the data file from a github url. """
    result = requests.get(url)
    return result.text.split('\n')


github_url = 'https://raw.githubusercontent.com/j-faria/HARPSmp/master/'\
             'data/%s_harps.rdb'


class RVseries:
    """ A container class that holds the observed radial velocity data."""

    def __repr__(self):
        return f"HARPS RVs of {self.star}"

    def __init__(self, star, ms=True, verbose=False):
        if not url_is_alive(github_url % star):
            raise ValueError(f'Data for {star} is not available')

        self.star = star
        filename = f'{star}_harps.rdb'
        fileurl = get_file(github_url % star)
        if verbose: print(f'Reading file "{filename}"')

        self.data = np.genfromtxt(fileurl, unpack=True, skip_header=2)
        self.units = 'km/s'

        self.time = self.data[0]
        self.vrad = self.data[1]
        self.error = self.data[2]

        self.fwhm = self.data[3].copy()
        self.contrast = self.data[4].copy()
        self.bis = self.data[5].copy()
        self.rhk = self.data[9].copy()
        
        if ms:
            self.transform_to_ms()

        self.N = self.time.size
        self.plot_kwargs = {'fmt':'o', 'ms':3, 'capsize':0}

    def transform_to_ms(self, verbose=False, add_original_mean=False):
        assert self.units == 'km/s', 'Units are already m/s?'
        self.mean_vrad_original = self.vrad.mean()
        self.vrad = (self.vrad - self.mean_vrad_original)*1e3 
        if add_original_mean:
            self.vrad += self.mean_vrad_original
        self.error *= 1e3

        # indicators
        self.fwhm = (self.fwhm - self.fwhm.mean())*1e3
        self.bis *= 1e3 # self.bis = (self.bis - self.bis.mean())*1e3

        self.units = 'm/s'
        if verbose: print(f'Transformed observations to m/s')

    def plot(self):
        fig, ax = plt.subplots(1, 1)
        ax.errorbar(self.time, self.vrad, self.error, **self.plot_kwargs)
        ax.set(title=f'HARPS RV observations of {self.star}', 
               xlabel='Time [MJD]', ylabel=f'RV ({self.units})')
    
    def plot_fwhm(self):
        fig, ax = plt.subplots(1, 1)
        ax.errorbar(self.time, self.fwhm, **self.plot_kwargs)
        ax.set(title=f'HARPS FWHM observations of {self.star}', 
               xlabel='Time [MJD]', ylabel=f'FWHM ({self.units})')

    def plot_bis(self):
        fig, ax = plt.subplots(1, 1)
        ax.errorbar(self.time, self.bis, **self.plot_kwargs)
        ax.set(title=f'HARPS BIS observations of {self.star}', 
               xlabel='Time [MJD]', ylabel=f'BIS ({self.units})')

    def plot_contrast(self):
        fig, ax = plt.subplots(1, 1)
        ax.errorbar(self.time, self.contrast, **self.plot_kwargs)
        ax.set(title=f'HARPS CCF contrast observations of {self.star}', 
               xlabel='Time [MJD]', ylabel='contrast (%)')



github_results_url = 'https://raw.githubusercontent.com/j-faria/HARPSmp/master/'\
                     'results/%s.pickle'

try:
    import pykima
    pykima_available = True
except ImportError:
    pykima_available = False

class Analysis:
    """ A simple class to hold the results of a kima analysis """

    def __init__(self, star, verbose=False):
        if not pykima_available:
            raise ValueError('You need to install pykima to load the results')
            
        if not url_is_alive(github_results_url % star):
            raise ValueError(f'Results for {star} are not yet available')

        self.star = star