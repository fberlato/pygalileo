import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
import pyipn
from scipy.io import matlab
import h5py

import matplotlib.pyplot as plt
from pkg_resources import resource_stream

#data = matlab.loadmat('data/sat_data.mat')
stream = resource_stream(__name__, 'data/sat_data.mat')
data = matlab.loadmat(stream)

const_pos = data['satxyz']
const_vect = data['nvec']


det_sc_side = ['+x', '-x', '+y', '-y', '+z', '-z']

det_side_to_name_dict = {'+x': 'plus_x', '-x': 'minus_x', 
                         '+y': 'plus_y', '-y': 'minus_y', 
                         '+z': 'plus_z', '-z': 'minus_z'}

class ConstellationGenerator(object):
    
    def __init__(self, mask, det_sides, a_geo, bkg_rate=None):
        '''
        Generates the detector setup for the chosen constellation.
        
        :param mask: mask array to select which slots in the cosntellation to use (used=1, empty=0)
        "param det_sides: which sides of each spacecraft are equipped with a detector (e.g. ['+z', '-x', '+x'])
        :param a_geo: effective area of the detectors
        :param bkg_rate: bkg rate of in the detectors (default is set to 4 * a_geo)
        '''
        
        
        self.mask = mask
        self.det_sides = det_sides
        self.a_geo = a_geo
        
        if bkg_rate != None:
            self.bkg_rate = bkg_rate
        else:
            self.bkg_rate = 4. * self.a_geo
        
        self.det_dict = dict()
        self._generate_constellation()
        
        
    def plot_detector_pointings(self):
        
        assert len(self.det_dict) != 0, "There are no instatiated detectors!"
  
        det_pointings = []

        for key, det in self.det_dict.items():
        
            det_pointings.append(np.array([det.pointing.coord.ra.value, det.pointing.coord.dec.value]))
        
        det_pointings = np.array(det_pointings)
        
        fig, ax = plt.subplots(subplot_kw=dict(projection='astro degrees mollweide'))

        ax.scatter(det_pointings[:,0], det_pointings[:,1], c='blue', alpha=0.4, transform=ax.get_transform("icrs"), 
                   s=20, zorder=2, label='Detector pointings', marker='o')

        ax.grid()
        
        return fig
        
        
    def _generate_constellation(self):
        
        self._spacecrafts = []
        
        for i in range(len(self.mask)):

            if self.mask[i] == 0:
                continue

            det_pos = SkyCoord(x=const_pos[i][0], y=const_pos[i][1], z=const_pos[i][2], frame='icrs', unit=u.km, representation_type='cartesian')

            altitude = np.linalg.norm(det_pos.cartesian.xyz.value)

            det_ra, det_dec = det_pos.spherical.lon.value, det_pos.spherical.lat.value

            #same for all detectors on the same spacecraft
            detector_loc = pyipn.geometry.DetectorLocation(ra=det_ra, dec=det_dec, altitude=altitude*u.km, obs_time='2010-01-01T00:00:00')

            # pointing vectors for each axis
            x_plus = SkyCoord(x=const_vect[i][0][0], y=const_vect[i][0][1], z=const_vect[i][0][2], frame='icrs', unit=u.km, representation_type='cartesian')
            x_minus = SkyCoord(x=const_vect[i][1][0], y=const_vect[i][1][1], z=const_vect[i][1][2], frame='icrs', unit=u.km, representation_type='cartesian')
            y_plus = SkyCoord(x=const_vect[i][2][0], y=const_vect[i][2][1], z=const_vect[i][2][2], frame='icrs', unit=u.km, representation_type='cartesian')
            y_minus = SkyCoord(x=const_vect[i][3][0], y=const_vect[i][3][1], z=const_vect[i][3][2], frame='icrs', unit=u.km, representation_type='cartesian')
            z_minus = SkyCoord(x=const_vect[i][4][0], y=const_vect[i][4][1], z=const_vect[i][4][2], frame='icrs', unit=u.km, representation_type='cartesian')
            z_plus = SkyCoord(x=const_vect[i][5][0], y=const_vect[i][5][1], z=const_vect[i][5][2], frame='icrs', unit=u.km, representation_type='cartesian') 

            det_side_dict = {'+x': x_plus, '-x': x_minus, '+y': y_plus, '-y': y_minus, '+z': z_plus, '-z': z_minus}
            


            for key, pointing in det_side_dict.items():

                if key not in self.det_sides:
                    continue
                
                det_icrs_pointing = pointing.spherical


                detector_pointing = pyipn.geometry.Pointing(ra=det_icrs_pointing.lon.value, dec=det_icrs_pointing.lat.value)

                det_name = f'sat_{i}_{det_side_to_name_dict[key]}'

                altitude = altitude
                effective_area = pyipn.effective_area.EffectiveArea(self.a_geo)

                detector = pyipn.detector.Detector(location=detector_loc, pointing=detector_pointing, 
                                                    effective_area=effective_area, name=det_name, bkg_value=self.bkg_rate)
                
                
                self.det_dict[det_name] = detector
                


