#!/bin/bash
pyuic5 -x interface.ui -o interface.py
mv ../src/interface.py ../src/interfaceI.py
mv interface.py ../src/interface.py
