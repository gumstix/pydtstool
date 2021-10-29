*Author: Keith Lee*

*Contact: keith.lee@altium.com*

Copyright 2021 Altium Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and 
associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial 
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT 
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# PyDtsTool
A Python3 library for interpreting, editing and exporting device tree data as an abstract data structure. 
**WIP**.

## The Library
The PyDtsTool library has an API for importing DTS files, exporting YAML representations, an early implementation
of a graphing tool, showing the interactions between DT nodes, and exporting back into DTS format.

### DeviceTree Class
The DeviceTree class is a container for all Node objects and any C-style precompile declarations, such as `#include`
and `#define`.

#### DeviceTree Public Methods

1. DeviceTree.copy():  
    Creates a new DeviceTree object identical to the original

2. DeviceTree.get_node_from_tuple(*sig_tuple*)