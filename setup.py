from setuptools import setup

setup(name='roach_tools',
      version='0.1',
      description='Roach tools for digital development in the MWL.',
      url='http://github.com/francocalan/roach_tools',
      author='Franco Curotto',
      author_email='francocurotto@gmail.com',
      license='GPL',
      packages=['roach_tools', 'roach_utils'],
      package_dir={'roach_tools' : 'experiments',
                   'roach_utils' : 'utilities'},
      install_requires=[
            'construct', 
            'corr', 
            'katcp', 
            'numpy', 
            'numexpr'],
      dependency_links=['https://github.com/nrao/ValonSynth'],
      zip_safe=False)
