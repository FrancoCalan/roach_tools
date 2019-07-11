import argparse, tarfile, json
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description="Plot cancellation results from a .tar datafile generated from a BM test.")
parser.add_argument(type=str, dest="datafile", help="Tar file with the data to plot.")
args = parser.parse_args()

tar_datafile = tarfile.open(args.datafile)
testinfo_json = tar_datafile.extractfile("testinfo.json")
testinfo = json.load(testinfo_json)

freqs = np.linspace(0, testinfo['bw'], testinfo['nchannels'], endpoint=False)

for lo_comb in testinfo['lo_combinations']:
    plt.figure()
    datadir = '_'.join(['LO'+str(i+1)+'_'+str(lo/1e3)+'GHZ' for i,lo in enumerate(lo_comb)]) 
    cancellation_datafile = tar_datafile.extractfile(datadir + '/cancellation.npz')
    cancellation_data = np.load(cancellation_datafile)

    usb_freqs = lo_comb[0]/1.0e3 + sum(lo_comb[1:])/1.0e3 + freqs
        
    plt.plot(usb_freqs, cancellation_data['uncalibrated'], label='Uncalibrated')
    plt.plot(usb_freqs, cancellation_data['ideal'], label='Ideal Constants')
    plt.plot(usb_freqs, cancellation_data['calibrated'], label='Calibrated Constants')
    plt.grid()
    plt.xlabel('Frequency [GHz]')
    plt.ylabel('Power [dB]')
    plt.gcf().canvas.set_window_title(datadir)
    plt.legend()

plt.show()

    
