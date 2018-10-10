from __future__ import absolute_import, print_function
import numpy as np
from  .tools import *
from . import debug

@timeme
def Lco_to_map(halos,map,units='temperature'):
    """
    Converts Luminosity to brightness temperature 
    and bins into 3d intensity map data cube

    Parameters
    ----------
    halos : class
        Contains all halo information (position, redshift, etc..) 
    map : class
       contains all information about the map that the halos will be binned into

    Returns
    -------
    maps :
        The 3D data cube of brightness temperature
    """

    ### Calculate line freq from redshift
    halos.nu  = map.nu_rest/(halos.redshift+1)       
    
    # Transform from Luminosity to Temperature (uK)
    # ... or to flux density (Jy/sr)
    if (units=='intensity'):
        if debug.verbose: print('\n\tcalculating halo intensities')
        halos.Tco = I_line(halos, map)
    else:
        if debug.verbose: print('\n\tcalculating halo temperatures')
        halos.Tco = T_line(halos, map)

    # flip frequency bins because np.histogram needs increasing bins
    bins3D = [map.pix_binedges_x, map.pix_binedges_y, map.nu_binedges[::-1]]

    # bin in RA, DEC, NU_obs
    if debug.verbose: print('\n\tBinning halos into map')
    maps, edges = np.histogramdd( np.c_[halos.ra, halos.dec, halos.nu], 
                                  bins    = bins3D,
                                  weights = halos.Tco )
    if (units=='intensity'):
        maps/= map.Ompix
    # flip back frequency bins
    return maps[:,:,::-1]

def I_line(halos, map):
    ''' 
     calculates I_line = L_line/4/pi/D_L^2/dnu
     output units of Jy/sr
     assumes L_line in units of L_sun, dnu in GHz

     then 1 L_sun/Mpc**2/GHz = 4.0204e-2 Jy/sr
    ''' 
    convfac = 4.0204e-2 # Jy/sr per Lsol/Mpc/Mpc/GHz
    Ico     = convfac * halos.Lco/4/np.pi/halos.chi**2/(1+halos.redshift)**2/map.dnu

    return Ico

def T_line(halos, map):
    """
    The line Temperature in Rayleigh-Jeans limit
    T_line = c^2/2/kb/nuobs^2 * I_line

     where the Intensity I_line = L_line/4/pi/D_L^2/dnu
        D_L = D_p*(1+z), I_line units of L_sun/Mpc^2/Hz

     T_line units of [L_sun/Mpc^2/GHz] * [(km/s)^2 / (J/K) / (GHz) ^2] * 1/sr
        = [ 3.48e26 W/Mpc^2/GHz ] * [ 6.50966e21 s^2/K/kg ] 
        = 2.63083e-6 K = 2.63083 muK 
    """ 
    convfac = 2.63083
    Tco     = 1./2*convfac/halos.nu**2 * halos.Lco/4/np.pi/halos.chi**2/(1+halos.redshift)**2/map.dnu/map.Ompix

    return Tco

@timeme
def save_maps(map):
    """
    save 3D data cube in .npz format, including map header information
    """
    if debug.verbose: print('\n\tSaving Map Data Cube to\n\t\t',map.output_file)
    np.savez(map.output_file,
             fov_x=map.fov_x, fov_y=map.fov_y,
             pix_size_x=map.pix_size_x, pix_size_y=map.pix_size_y,
             npix_x=map.npix_x, npix_y=map.npix_y,
             map_pixel_ra    = map.pix_bincents_x,
             map_pixel_dec   = map.pix_bincents_y,
             map_frequencies = map.nu_bincents,
             map_cube        = map.maps)

    return
