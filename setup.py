import glob
from setuptools import setup, find_packages

setup(name = 'roach_tools',
      version = '0.4',
      description = 'Roach tools for digital development in the MWL.',
      url = 'http://github.com/francocalan/roach_tools',
      author = 'Franco Curotto',
      author_email = 'francocurotto@gmail.com',
      license = 'GPL v3',
      packages = ['roach_tools', 
                  'roach_tools.axes', 
                  'roach_tools.dummies', 
                  'roach_tools.instruments'],
      package_dir = {'roach_tools' : 'src',
                     'roach_tools.axes' : 'src/axes',
                     'roach_tools.dummies' : 'src/dummies',
                     'roach_tools.instruments' : 'src/instruments'},
      scripts = glob.glob('bin/*.py') +
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
