import argparse, tarfile, json
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description="Plot the input ratios (magnitude ratio and phase difference) from a .tar datafile generated from a BM test.")
parser.add_argument(type=str, dest="datafile", help="Tar file with the data to plot.")
parser.add_argument('--nchans', type=int, dest="nchans", default=None, help="Number of channel to plot for each LO combination.")
args = parser.parse_args()

tar_datafile = tarfile.open(args.datafile)
testinfo_json = tar_datafile.extractfile("testinfo.json")
testinfo = json.load(testinfo_json)

freqs = np.linspace(0, testinfo['bw'], testinfo['nchannels'], endpoint=False)
try:
    cal_channels = np.arange(1, testinfo['nchannels'], testinfo['cal_chnl_step'])
except KeyError:
    cal_channels = np.arange(testinfo['nchannels'])
cal_freqs = np.array([freqs[chnl]/1.0e3 for chnl in cal_channels])

fig = plt.figure()
ax1  = fig.add_subplot(1,2,1)
ax2  = fig.add_subplot(1,2,2)

for lo_comb in testinfo['lo_combinations']:
    datadir = '_'.join(['LO'+str(i+1)+'_'+str(lo/1e3)+'GHZ' for i,lo in enumerate(lo_comb)]) 
    ab_datafile = tar_datafile.extractfile(datadir + '/ab_params.npz')
    ab_data = np.load(ab_datafile)

    usb_freqs = lo_comb[0]/1.0e3 + sum(lo_comb[1:])/1.0e3 + freqs/1.0e3
    lsb_freqs = lo_comb[0]/1.0e3 - sum(lo_comb[1:])/1.0e3 - freqs/1.0e3

    ab_ratio_usb = np.conj(ab_data['ab_usb']) / ab_data['a2_usb'] # (ab*)* / aa* = a*b / aa* = b/a
    ab_ratio_lsb = ab_data['ab_lsb'] / ab_data['b2_lsb'] # ab* / bb* = a/b

    n = args.nchans
    ax1.plot(usb_freqs[:n], np.abs(ab_ratio_usb[:n]), '-r')
    ax1.plot(lsb_freqs[:n], np.abs(ab_ratio_lsb[:n]), '-b')
    ax1.grid()
    ax1.set_xlabel('Frequency [GHz]')
    ax1.set_ylabel('Magnitude Ratio [linear]')

    ax2.plot(usb_freqs[:n], np.degrees(np.unwrap(np.angle(ab_ratio_usb[:n]))), '-r')
    ax2.plot(lsb_freqs[:n], np.degrees(np.unwrap(np.angle(ab_ratio_lsb[:n]))), '-b')
    ax2.grid()
    ax2.set_xlabel('Frequency [GHz]')
    ax2.set_ylabel('Angle Difference [degrees]')

plt.tight_layout()
plt.show()
