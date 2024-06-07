#!/bin/bash

# Clone the full repository
git clone https://github.com/JDAI-CV/fast-reid.git


# Copy the 'fastreid' subfolder to the current directory under the same name
mv  fast-reid/fastreid .

# Remove the original cloned directory
rm -rf fast-reid
