#!/bin/bash

# source ROOT if not set
if [ -z $ROOT_INCLUDE_PATH ]; then
	export ROOTSYS=/cvmfs/sft.cern.ch/lcg/app/releases/ROOT/5.34.13/x86_64-slc6-gcc48-opt/root/
	#export GCCLIBS=/cvmfs/sft.cern.ch/lcg/external/gcc/4.7.2/x86_64-slc5/lib64/
	#export LD_LIBRARY_PATH=$GCCLIBS:$LD_LIBRARY_PATH
	. $ROOTSYS/bin/thisroot.sh
fi

# use up-to-date GCC version from CVMFS
#. /cvmfs/cms.cern.ch/slc6_amd64_gcc472/external/gcc/4.7.2/etc/profile.d/init.sh
. /cvmfs/cms.cern.ch/slc6_amd64_gcc491/external/gcc/4.9.1-cms/etc/profile.d/init.sh

export ARCHITECTURE=slc6_amd64_gcc491
for SOFTWARE in lhapdf/6.1.5 yoda/1.3.1 hepmc/2.06.07-cms fastjet/3.1.0 qd/2.3.13-cms/ rivet/2.2.1-kpegke/; do
	. /cvmfs/cms.cern.ch/$ARCHITECTURE/external/$SOFTWARE/etc/profile.d/init.sh
done


export SHERIVFDIR=$(dirname $(dirname $(readlink -mf ${BASH_SOURCE[0]})))
. $SHERIVFDIR/scripts/configures.sh

export PATH=$SHERIVFDIR/scripts:$HOME/local/bin:$PATH
export LD_LIBRARY_PATH=$HOME/local/lib:$LD_LIBRARY_PATH

# output paths
export STORAGE_PATH=/storage/a/${USER}
export SHERIVF_STORAGE_PATH=$STORAGE_PATH/sherivf/
export HERA_STORAGE_PATH=$STORAGE_PATH/hera/


#export MCGRID_OUTPUT_PATH=$PWD
#export MCGRID_PHASESPACE_PATH=$PWD

#export PKG_CONFIG_PATH=$SHERIVFDIR/../enrico/mcgrid/mcgrid/:$PKG_CONFIG_PATH
export PKG_CONFIG_PATH=/storage/a/dhaitz/software/mcgrid-2.0:$PKG_CONFIG_PATH
#export LOCALHOME=/usr/users/${USER}/

# Rivet
#export PATH=$SHERIVFDIR/../Rivet-2.2.0/bin/:/usr/users/${USER}/local/bin:$PATH
#export PATH=$HOME/local/bin:$PATH
#export RIVET_ANALYSIS_PATH=$PWD:$RIVET_ANALYSIS_PATH
#if [ -e $SHERIVFDIR/../Rivet-2.2.0/rivetenv.sh ]
#then
#	. $SHERIVFDIR/../Rivet-2.2.0/rivetenv.sh
#fi


#Sherpa
#export SHERPA_INCLUDE_PATH=$LOCALHOME/local/include/SHERPA-MC
#export SHERPA_SHARE_PATH=$LOCALHOME/local/share/SHERPA-MC
#export SHERPA_LIBRARY_PATH=$LOCALHOME/local/lib/SHERPA-MC
#export LD_LIBRARY_PATH=$SHERPA_LIBRARY_PATH:$LOCALHOME/local/lib:$LD_LIBRARY_PATH


#other stuff
#export QCDNUM_ROOT=/portal/ekpcms6/home/${USER}/qcd/qcdnum-17-00-06
#export PYTHONPATH=$HOME/local/lib/python2.7/site-packages:$PYTHONPATH
#export BOOSTPATH=/cvmfs/cms.cern.ch/slc6_amd64_gcc481/external/boost/1.57.0-cflfif
#export LD_LIBRARY_PATH=$PWD:$LD_LIBRARY_PATH:$BOOSTPATH/lib:$HOME/local/lib64/:/usr/users/${USER}/local/lib/SHERPA-MC/

# aliases
export RIVET_COMPILER_FLAGS="-std=c++0x -Wl,--export-dynamic,-z,defs $(pkg-config mcgrid --cflags) $(pkg-config mcgrid --libs)  -lYODA"
#    -lHepMC -DUSE_FNLO=1"

