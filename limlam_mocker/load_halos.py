from __future__ import absolute_import, print_function
import numpy as np
from  .tools import *

def load_peakpatch_catalogue(filein):

    halos      = empty_table()            # creates empty class to put any halo info into  
    halo_info  = np.load(filein)     
    print("\thalo catalogue contains:\n\t\t", halo_info.files)

    halos.M          = halo_info['M']     # halo mass in Msun
    
    halos.x_pos      = halo_info['x']     # halo position in comoving Mpc 
    halos.y_pos      = halo_info['y']
    halos.z_pos      = halo_info['z']
    halos.chi        = np.sqrt(halos.x_pos**2+halos.y_pos**2+halos.z_pos**2)

    halos.vx         = halo_info['vx']    # halo velocity in km/s
    halos.vy         = halo_info['vy']
    halos.vz         = halo_info['vz']

    halos.redshift   = halo_info['zhalo'] # redshift of halo
    halos.redshifto  = (halos.redshift+1)*(1+halos.vz/299792.458)
                                          # observed redshift incl velocities
    halos.zformation = halo_info['zform'] # formation redshift of halo

    halos.nhalo = len(halos.M)
    
    halos.ra         = np.arctan2(-halos.y_pos,halos.z_pos)*180./np.pi
    halos.dec        = np.arcsin(  halos.x_pos/halos.chi  )*180./np.pi

    print('\n\t%d halos loaded' % halos.nhalo)

    return halos


def cull_peakpatch_catalogue(halos, min_mass):

    dm = [halos.M > min_mass]

    for i in dir(halos):
        if i[0]=='_': continue
        try:
            setattr(halos,i,getattr(halos,i)[dm])
        except TypeError:
            pass
    halos.nhalo = len(halos.M)

    print('\n\t%d halos remain after mass cut' % halos.nhalo)

    return halos