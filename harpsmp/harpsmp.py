import os
import re
from glob import glob
import numpy as np 
import matplotlib.pyplot as plt

this_dir = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(this_dir, '..', 'data')


def get_star_name_from_path(full_path):
    """ Return the name of the star (works for standard HARPS filenames) """
    bn = os.path.basename(full_path)
    pattern = '|'.join(['HD\d+', 'HIP\d+', 'HR\d+', 'BD-\d+', 'CD-\d+',
                        'NGC\d+No\d+', 'GJ\d+', 'Gl\d+'])
    return re.findall(pattern, bn)[0]


available_stars = list(map(get_star_name_from_path, 
                          glob(os.path.join(data_path, '*'))
                          ))


class RVseries:
    """ A container class that holds the observed radial velocity data."""

    def __repr__(self):
        return f"HARPS RVs of {self.star}"

    def __init__(self, star, ms=True, verbose=False):
        assert star in available_stars, f'Data for {star} is not available'

        self.star = star
        filename = f'{data_path}/{star}_harps.rdb'
        if verbose: print(f'Reading file "{filename}"')
        self.data = np.loadtxt(filename, unpack=True, skiprows=2)
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
        fig.show()
    
    def plot_fwhm(self):
        fig, ax = plt.subplots(1, 1)
        ax.errorbar(self.time, self.fwhm, **self.plot_kwargs)
        ax.set(title=f'HARPS FWHM observations of {self.star}', 
               xlabel='Time [MJD]', ylabel=f'FWHM ({self.units})')
        fig.show()

    def plot_bis(self):
        fig, ax = plt.subplots(1, 1)
        ax.errorbar(self.time, self.bis, **self.plot_kwargs)
        ax.set(title=f'HARPS BIS observations of {self.star}', 
               xlabel='Time [MJD]', ylabel=f'BIS ({self.units})')
        fig.show()

    def plot_contrast(self):
        fig, ax = plt.subplots(1, 1)
        ax.errorbar(self.time, self.contrast, **self.plot_kwargs)
        ax.set(title=f'HARPS CCF contrast observations of {self.star}', 
               xlabel='Time [MJD]', ylabel='contrast (%)')
        fig.show()    