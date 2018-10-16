import argparse, tarfile, json
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description="Plot SRR results from a .tar datafile generated from a DSS test.")
parser.add_argument(type=str, dest="datafile", help="Tar file with the data to plot.")
args = parser.parse_args()

tar_datafile = tarfile.open(args.datafile)
testinfo_json = tar_datafile.extractfile("testinfo.json")
testinfo = json.load(testinfo_json)

freqs = np.linspace(0, testinfo['bw'], testinfo['nchannels'], endpoint=False)
syn_channels = np.arange(1, testinfo['nchannels'], testinfo['srr_chnl_step'])
srr_freqs = np.array([freqs[chnl]/1.0e3 for chnl in syn_channels])

fig = plt.figure()
for lo_comb in testinfo['lo_combinations']:
    datadir = '_'.join(['LO'+str(i+1)+'_'+str(lo/1e3)+'GHZ' for i,lo in enumerate(lo_comb)]) 
    srr_datafile = tar_datafile.extractfile(datadir + '/srr.npz')
    srrdata = np.load(srr_datafile)

    usb_freqs = lo_comb[0]/1.0e3 + sum(lo_comb[1:])/1.0e3 + srr_freqs
    lsb_freqs = lo_comb[0]/1.0e3 - sum(lo_comb[1:])/1.0e3 - srr_freqs
        
    plt.plot(usb_freqs, srrdata['srr_usb'], '-r')
    plt.plot(lsb_freqs, srrdata['srr_lsb'], '-b')
    plt.grid()
    plt.xlabel('Frequency [GHz]')
    plt.ylabel('SRR [dB]')

plt.show()

    
