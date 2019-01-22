import glob
from setuptools import setup, find_packages

setup(name = 'roach_tools',
      version = '0.6',
      description = 'Roach tools for digital development in the MWL.',
      url = 'http://github.com/francocalan/roach_tools',
      author = 'Franco Curotto',
      author_email = 'francocurotto@gmail.com',
      license = 'GPL v3',
      packages = ['roach_tools', 
                  'roach_tools.adc5g_calibration',
                  'roach_tools.adc_histogram',
                  'roach_tools.adc_synchronator',
                  'roach_tools.axes', 
                  'roach_tools.digital_sideband_separation',
                  'roach_tools.dram_spectrogram', 
                  'roach_tools.dummies', 
                  'roach_tools.instruments',
                  'roach_tools.kesteven_filter',
                  'roach_tools.multi_beam_former',
                  'roach_tools.transfer_function',
                  'roach_tools.vector_voltmeter'],
      package_dir = {'roach_tools' : 'src',
                     'roach_tools.adc5g_calibration' : 'src/adc5g_calibration',
                     'roach_tools.adc_histogram' : 'src/adc_histogram',
                     'roach_tools.adc_synchronator' : 'src/adc_synchronator',
                     'roach_tools.axes' : 'src/axes',
                     'roach_tools.digital_sideband_separation' : 'src/digital_sideband_separation',
                     'roach_tools.dram_spectrogram' : 'src/dram_spectrogram', 
                     'roach_tools.dummies' : 'src/dummies',
                     'roach_tools.instruments' : 'src/instruments',
                     'roach_tools.kesteven_filter' : 'src/kesteven_filter',
                     'roach_tools.multi_beam_former' : 'src/multi_beam_former',
                     'roach_tools.transfer_function' : 'src/transfer_function',
                     'roach_tools.vector_voltmeter' : 'src/vector_voltmeter'},
      scripts = glob.glob('bin/*.py') +
                glob.glob('bin/general_utils/*.py') +
                glob.glob('bin/dss_utils/*.py'),
      install_requires = [
            'construct', 
            'corr', 
            'katcp', 
            'h5py',
            'numpy', 
            'matplotlib',
            'numexpr',
            'spead',
            'pyserial',
            'pyvisa'],
      dependency_links = ['https://github.com/nrao/ValonSynth'],
      zip_safe = False)
