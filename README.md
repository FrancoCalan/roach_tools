# roach_tools

High level Python library for interfacing with ROACH1/2 using the [corr](https://github.com/ska-sa/corr) package.

## Installation

Installation instruction only for Linux-based system provided:

0. It is recommended to use this software in a [Python virtual enviroment](https://virtualenv.pypa.io/en/stable/).
1. `git clone` or download/unzip repository
2. Install repository dependencies, in roach_tools root folder: `pip install -r REQUIREMENTS` (install pip if necesarry)
3. Install repository: `python setup.py install`

## Usage

### Config files

roach_tools use config files to configure all the desired parameters to interface with the ROACH. A config file is a simple Python script which contains only variable definitions. Here is an example the simplest config file:

```python
# Basic settings
simulated  = True         # True: run in simulation, False: run in real ROACH
roach_ip   = '0.0.0.0'    # ROACH IP address
roach_port = 7147         # ROACH communication port
upload     = False        # True: upload .bof/.bof.gz model to ROACH
program    = False        # True: program FPGA with .bof model
boffile    = ''           # .bof file to upload/program
set_regs   = [{'name' : 'reg_name', 'val' : 1}] # Registers to set at startup
reset_regs = ['reg_name'] # Registers to reset (1->0) st startup
bw         = 1000         # Bandwidth used for plotting/simulation propuses (in MHz)
```
For more complete examples check [here](https://github.com/FrancoCalan/roach_tools/tree/master/bin/config_files). for a full description of all posible parameters in a config file check here(add link).

### CalanFpga

CalanFpga is a wrapper around corr's FpgaClient. It implements most of the FpgaClients functions and adds new high level functions for easy ROACH development. Between these you can find:

* ROACH initialization
* Read multiple snapshots/bram at the same time
* Synchronized snapshot data read
* Read and interleave bram data

To create a CalanFpga object you must provide a config file settings file. 
