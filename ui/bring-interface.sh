#!/bin/bash
rm -f interface.py
pyuic5 -x interface.ui -o interface.py
mv ../src/gui/interface.py ../src/gui/interfaceI.py
mv interface.py ../src/gui/interface.py
