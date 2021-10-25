import numpy as np
from pygalileo.constellation_generator import ConstellationGenerator


def test_constellation_generator():


    mask = np.ones(24)
    a_geo = 1000.
    bkg_rate = 500.
    det_sides=['+x', '-x', '+y', '-y']
    
    test_const = ConstellationGenerator(mask=mask, det_sides=det_sides, a_geo=a_geo, bkg_rate=bkg_rate)

    assert len(list(test_const.det_dict.keys())) == len(det_sides) * len(mask)
    assert test_const.a_geo == a_geo
    assert test_const.bkg_rate == bkg_rate







if __name__ == "__main__":
    test_constellation_generator()
