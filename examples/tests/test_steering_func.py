import numpy as np

def calculate_vector(theta, phi):
    # Constants
    freq = 5.81e9           # 5.81 GHz
    c = 3e8                 # speed of light (u can't beat it)
    wavelength = c / freq   # 51.72 mm
    d = wavelength / 2      # separation between array elements

    # Array element positions
    p = np.zeros([4, 4, 3])
    for i in range(4):
        for j in range(4):
            p[i][j] = np.array([d * (i - 1.5), 0, d * (j - 1.5)])
    #print p

    # Direction of Arrival calculations
    theta = np.pi / 180 * (90 - theta)
    phi = np.pi / 180 * (90 - phi)
    a = np.array([-np.sin(theta) * np.cos(phi), -np.sin(theta) * np.sin(phi), -np.cos(theta)])  # DoA
    k = 2 * np.pi / wavelength * a  # wave-number vector

    # Calculate array manifold vector
    v_re = np.zeros([4, 4])
    v_im = np.zeros([4, 4])
    for i in range(4):
        for j in range(4):
            v = np.exp(-1j * np.dot(k, p[i][j]))
            v_re[i][j] = int(np.real(v) * ((1 << 17)-1))
            v_im[i][j] = int(-np.imag(v) * ((1 << 17)-1))

    return v_re, v_im

def angs2phasors(array_info, theta, phi): 
    wavelength = array_info['speed'] / array_info['freq']

    # get array element positions in meters
    el_pos = wavelength * array_info['el_sep'] * np.array(array_info['el_pos'])
    #print el_pos

    # convert angles into standard ISO shperical coordinates
    # (instead of (0,0) being the array perpendicular direction)
    theta = 90 - theta 
    phi = 90 - phi

    # convert angles into radians
    theta = np.pi / 180 * theta
    phi = np.pi / 180 * phi

    a = np.array([-np.sin(theta) * np.cos(phi), -np.sin(theta) * np.sin(phi), -np.cos(theta)])  # direction of arrival
    k = 2 * np.pi / wavelength * a  # wave-number vector

    # Calculate array manifold vector
    v = np.exp(-1j * np.dot(el_pos, k))

    return list(np.conj(v).flatten())
array_info = {'speed'  : 3e8,
              'freq'   : 5.81e9,
              'el_sep' : 0.5,
              'el_pos' : [[(-1.5, 0, -1.5), (-1.5, 0, -0.5), (-1.5, 0, 0.5), (-1.5, 0, 1.5)],
                          [(-0.5, 0, -1.5), (-0.5, 0, -0.5), (-0.5, 0, 0.5), (-0.5, 0, 1.5)],
                          [( 0.5, 0, -1.5), ( 0.5, 0, -0.5), ( 0.5, 0, 0.5), ( 0.5, 0, 1.5)],
                          [( 1.5, 0, -1.5), ( 1.5, 0, -0.5), ( 1.5, 0, 0.5), ( 1.5, 0, 1.5)]]}


v_fco = calculate_vector(30,-30)
#v_fco = (v_fco[0].flatten(), v_fco[1].flatten())
v_new = angs2phasors(array_info, 30, -30)
#v_new = ((np.real(v_new) * ((1 << 17)-1)).astype(int), (np.imag(v_new) * ((1 << 17)-1)).astype(int))


for i in range(4):
    for j in range(4):
        v_new_re = (np.real(v_new[i*4+j]) * ((1 << 17)-1)).astype(int)
        v_new_im = (np.imag(v_new[i*4+j]) * ((1 << 17)-1)).astype(int)
        #print "real: " + str(v_fco[0][i][j]) + ", " + str(v_new_re)
        #print "imag: " + str(v_fco[1][i][j]) + ", " + str(v_new_im)
        print "diff real: " + str(v_fco[0][i][j] - v_new_re) + ", diff imag: " + str(v_fco[1][i][j] - v_new_im) 

#print v_fco[1].astype(int)
#print v_new[1]
#print v_fco[0] - v_new[0]
#print v_fco[1] - v_new[1]
