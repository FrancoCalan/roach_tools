import glob
from setuptools import setup

setup(name = 'roach_tools',
      version = '0.3',
      description = 'Roach tools for digital development in the MWL.',
      url = 'http://github.com/francocalan/roach_tools',
      author = 'Franco Curotto',
      author_email = 'francocurotto@gmail.com',
      license = 'GPL',
      packages = ['roach_tools'],
      package_dir = {'roach_tools' : 'src'},
      scripts = glob.glob('bin/*.py'),
      install_requires = [
            'construct', 
            'corr', 
            'katcp', 
            'numpy', 
            'matplotlib',
            'numexpr',
            'spead',
            'pyserial'],
      dependency_links = ['https://github.com/nrao/ValonSynth'],
      zip_safe = False)
