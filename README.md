# roach_tools

High level python library for interfacing with ROACH1/2 using the [corr](https://github.com/ska-sa/corr) package.

## Installation

Installation instruction only for Linux-based system provided:

0. It is recommended to use this software in a [python virtual enviroment](https://virtualenv.pypa.io/en/stable/).
1. Install these packages (Ubuntu command): `sudo apt install python-dev python-tk g++`
2. `git clone` or download/unzip repository
3. Install repository dependencies, in roach_tools root folder: `pip install -r REQUIREMENTS` (install pip if necesarry)
4. Install repository: `python setup.py install`

*Note: If you are getting errors while installing the dependencies or the package, updating pip and/or virtualenv may help. Installation in virtual environment should work with pip>=10.0.1 and virtualenv>=15.0.1.*

## Usage

### Config files

roach_tools use config files to configure all the desired parameters to interface with the ROACH. A config file is a simple python script which contains only variable definitions. Here is an example a simple config file:

```python
# Basic settings
simulated  = True         # True: run in simulation, False: run in real ROACH
roach_ip   = '0.0.0.0'    # ROACH IP address
roach_port = 7147         # ROACH communication port
upload     = False        # True: upload .bof/.bof.gz model to ROACH
program    = False        # True: program FPGA with .bof model
boffile    = ''           # Filepath of the .bof to upload/program
set_regs   = [{'name' : 'reg_name', 'val' : 1}] # Registers to set at startup
reset_regs = ['reg_name'] # Registers to reset (->1->0) at startup
bw         = 1000         # Bandwidth used for plotting/simulation purposes (in MHz)
```
For more complete examples check [here](https://github.com/FrancoCalan/roach_tools/tree/master/examples/config_files). For a full description of all possible parameters in a config file check [here](https://github.com/FrancoCalan/roach_tools/wiki/Config-File-Parameters).

### CalanFpga

CalanFpga is a wrapper around corr's FpgaClient. It implements most of the FpgaClients functions and adds new high level functions for easy ROACH development. Among these you can find:

* ROACH initialization
* Read multiple snapshots/bram at the same time
* Synchronized snapshot data read
* Read and interleave bram data

To create a CalanFpga object you must provide a config file as a command-line argument. A simple ROACH initialization script would look like this:

```python
# Script: init_roach.py
from roach_tools.calanfpga import CalanFpga
fpga = CalanFpga()
fpga.initialize()
```

Then you run this script by typing in terminal: `python init_roach.py config_file.py`. 

*Note: due to python's importlib module limitations you must always run a roach_tools script in the same location as the config file. The python script can be in other location though.*

To learn about all the functions of CalanFpga, read them directly form the [code documentation](https://github.com/FrancoCalan/roach_tools/blob/master/src/calanfpga.py).

### Script Files

The repository also provides script files to easily perform common ROACH tasks out of the box. For a list of all implemented scripts go here(TODO: add link). For an explanation on how to use the scripts look at the [Calan wiki](https://sites.google.com/site/calandigital/home/tutorials/roach_tools-and-calanfpga).

## TODO
* Add scripts descriptions
* Add support for DRAM spectrograms

## Author
Franco Curotto

Millimeter-wave Laboratory, Department of Astronomy, University of Chile

http://www.das.uchile.cl/lab_mwl
