# pylink_tools

Python scripts that use Pylink framework to control a JTAG JLink debugger
device and communicate with a target ARM MCU connected to it.

## Requirements

- [Python 3.X](https://www.python.org/downloads/)
- [SEGGER J-Link Tools >= 6.0b](https://www.segger.com/downloads/jlink)
- [PyLink Framework](https://github.com/square/pylink)


## Installation

### pylink

Get and install pylink framework:

bash
```
git clone https://github.com/square/pylink
cd pylink
git checkout v0.14.3
python3 -m pip install .
```

### Segger J-Link Tools

In order to use this library, you will need to have installed the SEGGER tools.
The tools can be installed from the SEGGER website
[here](https://www.segger.com/downloads/jlink).  This package is compatible
with versions of the SEGGER tool `>= 6.0b`.  Download the software under
`J-Link Software and Documentation Pack` for your specific hardware.  `PyLink`
will automatically find the library if you have installed it this way, but for
best results, you should use one of the two methods listed below depending on
your operating system:

#### On Mac

```
# Option A: Copy the library to your libraries directory.
cp libjlinkarm.dylib /usr/local/lib/

# Option B: Add SEGGER's J-Link directory to your dynamic libraries path.
export DYLD_LIBRARY_PATH=/Applications/SEGGER/JLink:$DYLD_LIBRARY_PATH
```


#### On Windows

Windows searches for DLLs in the following order:

  1. The current directory of execution.
  2. The Windows system directory.
  3. The Windows directory.

You can copy the `JLinkARM.dll` to any of the directories listed above.
Alternatively, add the SEGGER J-Link directory to your `%PATH%`.


#### On Linux

```
# Option A: Copy the library to your libraries directory.
cp libjlinkarm.so /usr/local/lib/

# Option B: Add SEGGER's J-Link library path to your libraries path.
export LD_LIBRARY_PATH=/path/to/SEGGER/JLink:$LD_LIBRARY_PATH
```
