#!/bin/bash

# This script attempts to build absolutely everything in the stable
#  section of the project.

RTEMS_VERSION="4.12"
# even though there is currently only one target, it's better to keep this line for better readability.
RTEMS_TARGET="i386"
RTEMS_BSP="pc386" # should be matching with RTEMS_TARGET
export PREFIX=$HOME/rtems/${RTEMS_VERSION}
export PATH=$PREFIX/bin:$PATH

cd rtems-source-builder/rtems/
../source-builder/sb-set-builder \
  --log=sb-set-builder.log \
  --prefix="${PREFIX}" \
  "${RTEMS_VERSION}/rtems-${RTEMS_TARGET}"

cd ../../rtems/
./bootstrap
cd ..; mkdir rtems-build; cd rtems-build

../rtems/configure --enable-tests=samples --target=${RTEMS_TARGET}-rtems${RTEMS_VERSION} \
  --enable-rtemsbsp=${RTEMS_BSP} --prefix=${PREFIX}/b-${RTEMS_TARGET}
make all
make install

echo "export PATH=${PREFIX}/bin:$PATH" >> ~/.bashrc
echo "export RTEMS_MAKEFILE_PATH=${PREFIX}/b-${RTEMS_TARGET}/${RTEMS_TARGET}-rtems${RTEMS_VERSION}/${RTEMS_BSP}" >> ~/.bashrc
source ~/.bashrc
