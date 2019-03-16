from setuptools import setup, find_packages, findall

setup(name             = 'roach_tools',
      version          = '0.7',
      description      = 'Roach tools for digital development in the MWL.',
      url              = 'http://github.com/francocalan/roach_tools',
      author           = 'Franco Curotto',
      author_email     = 'francocurotto@gmail.com',
      license          = 'GPL v3',
      packages         = [pack.replace('src', 'roach_tools') for pack in find_packages()],
      package_dir      = {pack.replace('src', 'roach_tools') : pack.replace('.', '/') for pack in find_packages()},
      scripts          = findall('bin/'),
      install_requires = [line.rstrip('\n') for line in open('REQUIREMENTS') if not line.startswith('git+https://')],
      dependency_links = [line.rstrip('\n') for line in open('REQUIREMENTS') if line.startswith('git+https://')],
      zip_safe         = False)
