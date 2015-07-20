#!/bin/bash

export SHERIVFDIR=$(dirname $(dirname $(readlink -mf ${BASH_SOURCE[0]})))

if ( [[ $HOSTNAME == *"naf"* ]] || [[ $HOSTNAME == *"bird"* ]] ); then
	export SHERIVFDIR=/afs/desy.de/user/d/dhaitz/qcd/sherivf
else
	export SHERIVFDIR=/portal/ekpcms6/home/dhaitz/qcd/sherivf
fi

export PATH=$SHERIVFDIR/../Rivet-2.2.0/bin/:$SHERIVFDIR/scripts:$PATH:/usr/users/dhaitz/local/bin
export PATH=$SHERIVFDIR/../herafitter-1.1.1/bin:$PATH
. $SHERIVFDIR/../Rivet-2.2.0/rivetenv.sh

#harry plotter
export PYTHONCONFIGS=$SHERIVFDIR/harryplotter:$PYTHONCONFIGS
export PYTHONPATH=$SHERIVFDIR/harryplotter:$PYTHONPATH
export MODULES_SEARCH_PATH=$SHERIVFDIR/harryplotter/modules:$MODULES_SEARCH_PATH

export PKG_CONFIG_PATH=$SHERIVFDIR/../enrico/mcgrid/mcgrid/:$PKG_CONFIG_PATH
export RIVET_ANALYSIS_PATH=$PWD:$RIVET_ANALYSIS_PATH

# fastjet plugins
#-L$HOME/local/include/fastjet/.libs
# install fastjet with  "./configure --prefix=$HOME/local  --enable-allcxxplugins --enable-shared"

#MCgrid
#./configure --prefix=$HOME/local CXXFLAGS='-DFASTNLO_ENABLED=1'

#SHERPA
# ./configure --prefix=$HOME/local --with-sqlite3=install --enable-hepmc2=$HOME/local/ --enable-rivet=$HOME/local/ --enable-blackhat=/storage/a/dhaitz/blackhat   --enable-fastjet=$HOME/local/

#fastnlo
# ./configure --prefix=$HOME/local --enable-pyext  PYTHON_VERSION="2.6"

#blackhat
# ./configure --prefix=/storage/a/dhaitz/blackhat --with-QDpath=$HOME/local

# HERAfitter
#./configure --enable-lhapdf  LDFLAGS="-L/usr/users/dhaitz/local/lib/ -lblas -llapack -ltmglib"  --enable-nnpdfWeight
export QCDNUM_ROOT=/portal/ekpcms6/home/dhaitz/qcd/qcdnum-17-00-06

#yoda
# ./configure --prefix=$HOME/local --with-boost=$BOOSTPATH --enable-root


# build plugins
# rivet-buildplugin RivetMyAnalyses.so MCgrid_CMS_2015_Zee.cc -Wl,--export-dynamic,-z,defs  $(pkg-config mcgrid --cflags) $(pkg-config mcgrid --libs)  -lHepMC -lYODA  -DUSE_FNLO=1

export PYTHONPATH=$HOME/local/lib/python2.7/site-packages:$PYTHONPATH

#export BOOSTPATH=$(ls ${VO_CMS_SW_DIR}/${SCRAM_ARCH}/external/boost/* -d | tail -n 1)
export BOOSTPATH=/cvmfs/cms.cern.ch/slc6_amd64_gcc481/external/boost/1.57.0-cflfif

#export BOOSTLIB=${BOOSTPATH}/lib/libboost_regex.so.${BOOSTPATH/*\//}
export LD_LIBRARY_PATH=$PWD:$LD_LIBRARY_PATH:$BOOSTPATH/lib:$HOME/local/lib64/:/usr/users/dhaitz/local/lib/SHERPA-MC/
# -L$(BOOSTPATH)/lib/

#LHAPDF
export PATH=$SHERIVFDIR/../LHAPDF-6.1.5/bin/:$PATH
#export LHAPATH=/storage/a/dhaitz/PDFsets:$LHAPATH

# aliases
alias rivbuild="rivet-buildplugin RivetMyAnalyses.so MCgrid_CMS_2015_Zee.cc -Wl,--export-dynamic,-z,defs  $(pkg-config mcgrid --cflags) $(pkg-config mcgrid --libs)  -lHepMC -lYODA  -DUSE_FNLO=1"
alias riv="rivet  --analysis MCgrid_CMS_2015_Zee ../SHERPA-MC-2.1.1/Examples/V_plus_Jets/LHC_ZJets/sherpa_zjet.hepmc --pwd"

alias newwarmup="rename _warm Z_warm fnlo_*_warmup.tab && mv fnlo_*_warmup.tab $SHERIVFDIR/fnlo-cfg/"

alias herafit="(LHAPATH=/storage/a/dhaitz/PDFsets && cd $SHERIVFDIR/../herafitter-1.1.1 && rm $SHERIVFDIR/../herafitter-1.1.1/output/NNPDF23_nlo_as_0118_HighStat_chi2/* $SHERIVFDIR/../herafitter-1.1.1/NNPDF/data/* -rf && FitPDF)"

alias makeherafile="(merlin.py -x zpt -i ~/home/artus/Excalibur/old_work/data_ee_corr.root -f zcuts_AK5PFJetsCHSL1L2L3  --plot-m ExportHerafitter --x-bins '37,30,400' -w '(0.05/19.712)' --header-file ../../qcd/sherivf/herafitter/herafitter_header.txt --filename CMS_Zee_HFinput -o ~/home/qcd/sherivf/herafitter/)"

nnpdf_analysis(){
	qcd &&
	makeherafile &&
	herafit &&
	pdf_2_root.py --folder pdf_sets  &&
	merlin.py --py nnpdf

}


