#!/bin/bash

# This script attempts to build absolutely everything in the stable
#  section of the project.

RTEMS_VERSION="4.12"
# even though there is currently only one target, it's better to keep this line for better readability.
RTEMS_TARGETS="sparc"
export PREFIX=$HOME/rtems/${RTEMS_VERSION}
export PATH=$PREFIX/bin:$PATH

cd rtems-source-builder/rtems/
../source-builder/sb-set-builder \
  --log=sb-set-builder.log \
  --prefix="${PREFIX}" \
  "${RTEMS_VERSION}/rtems-sparc"

cd ../../rtems/
./bootstrap
cd ..; mkdir rtems-build; cd rtems-build

../rtems/configure --enable-tests=samples --target=${RTEMS_TARGETS}-rtems${RTEMS_VERSION} \
  --enable-rtemsbsp=sis --prefix=${PREFIX}/b-sparc
make all
make install
