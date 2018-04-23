#!/bin/sh
#MSUB -N WM MVAToolsRunner #name of job
#MSUB -A ared   #sets bank account
#MSUB -l nodes=1:ppn=1,walltime=23:59:59,partition=borax #uses one node
#MSUB -q pbatch     #pool
#MSUB -o /p/lscratche/adg/Watchboy/simplifiedData/rp_sim/MVATools/GridLog.log
#MSUB -e /p/lscratche/adg/Watchboy/simplifiedData/rp_sim/MVATools/GridErr.err
#MSUB -d /p/lscratche/adg/Watchboy/simplifiedData/rp_sim/MVATools #dir to run from
#MSUB -V
#MSUB           # no more psub commands

SHIELDTHICK=3074
HALFHEIGHT=10000
TANKRADIUS=10000


RPDEPENDS=/usr/gapps/adg/geant4/rat_pac_and_dependency
RUNDIR=${RPDEPENDS}/MVATools
DATADIR=/p/lscratche/adg/Watchboy/simplifiedData/rp_sim/apr2018/watchmakers_10mtank/bonsai_root_files_tankRadius_${TANKRADIUS}.000000_halfHeight_${HALFHEIGHT}.000000_shieldThickness_${SHIELDTHICK}.000000
#Source ROOT for python
source ${RPDEPENDS}/root-v5.34.00-Minuit2-Python/bin/thisroot.sh
source ${RPDEPENDS}/geant4.10.03/geant4.10.03.p02-build/share/Geant4-10.3.2/geant4make/../../../bin/geant4.sh
source ${RPDEPENDS}/geant4.10.03/geant4.10.03.p02-build/share/Geant4-10.3.2/geant4make/geant4make.sh
source ${RPDEPENDS}/rat-g4.10.03/rat-pac/env.sh
source ${RPDEPENDS}/watchmakers/env_wm.sh
export G4NEUTRONHP_USE_ONLY_PHOTONEVAPORATION=1

#Go to the directory containing the MVATools, then run them
cd $RUNDIR
python $RUNDIR/main.py --ibd --pc 25pct --datadir $DATADIR --buildSB --MVA --debug --jobnum $SHIELDTHICK
