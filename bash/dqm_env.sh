#!/bin/sh 
export WORKSPACE=`pwd`
export ILCSOFT=/afs/cern.ch/work/x/xshi/public/ILCSOFT
cd $ILCSOFT/v01-12/Eutelescope/HEAD/ 
source build_env.sh 
export dqm=/afs/cern.ch/work/x/xshi/public/dqm/v2/
export simplesub=$dqm/simplesub/
cd ${WORKSPACE} 

export PATH=$dqm/bin:$PATH
export TARGETDIRECTORY=/afs/cern.ch/cms/Tracker/Pixel/HRbeamtest/www/dqm/psi2013

export PXLTB_ROOT=/home/pixel_dev/cmspxltb/trunk

LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/opt/cactus/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${PXLTB_ROOT}/utils/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${PXLTB_ROOT}/generic/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${PXLTB_ROOT}/hwinterface/lib
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${PXLTB_ROOT}/calibration/lib
export LD_LIBRARY_PATH

export PYTHONPATH=$PYTHONPATH:${PXLTB_ROOT}/pycohal
