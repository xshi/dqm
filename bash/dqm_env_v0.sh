#!/bin/sh 
export WORKSPACE=`pwd`

export TB_ANALYSIS=/home/rslu/EuDEt/local/TestBeam/Analysis
export ILCSOFT=${TB_ANALYSIS}/ilcsoft 

source /home/rslu/EuDEt/local/TestBeam/Analysis/ilcsoft/v01-12/Eutelescope/HEAD/build_env.sh  

export simplesub=/home/pixel_dev/EUTEL_PIXELTB/TestBeam/Analysis/ilcsoft/v01-12/Eutelescope/HEAD/simplesub/
cd $simplesub/dqm/ && source setup.sh && cd 

cd ${WORKSPACE} 
export TARGETDIRECTORY=/var/www/html/pixel_dev/dqm/psi2013

export PXLTB_ROOT=/home/pixel_dev/cmspxltb/trunk

LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/opt/cactus/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${PXLTB_ROOT}/utils/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${PXLTB_ROOT}/generic/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${PXLTB_ROOT}/hwinterface/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${PXLTB_ROOT}/calibration/lib
export LD_LIBRARY_PATH

export PYTHONPATH=$PYTHONPATH:${PXLTB_ROOT}/pycohal
