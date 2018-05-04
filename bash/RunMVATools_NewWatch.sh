#!/bin/sh
#MSUB -N WM_MVAToolsRunner #name of job
#MSUB -A ared   #sets bank account
#MSUB -l nodes=1:ppn=1,walltime=23:59:59,partition=borax #uses one node
#MSUB -q pbatch     #pool
#MSUB -o /usr/gapps/adg/geant4/rat_pac_and_dependency/MVATools/GridLog.log
#MSUB -e /usr/gapps/adg/geant4/rat_pac_and_dependency/MVATools/GridErr.err
#MSUB -d /usr/gapps/adg/geant4/rat_pac_and_dependency/MVATools #dir to run from
#MSUB -V
#MSUB           # no more psub commands

#An example of a bash script that will run a MVAKERS job on the Borax cluster

#Dimensions fed to MVATools for generating rates of each background source
SHIELDTHICK=3074
HALFHEIGHT=10000
TANKRADIUS=10000

#Data directory to read WATCHMAKERS merged files from
DATADIR=/p/lscratche/adg/Watchboy/simplifiedData/rp_sim/apr2018/watchmakers_10mtank/bonsai_root_files_tankRadius_${TANKRADIUS}.000000_halfHeight_${HALFHEIGHT}.000000_shieldThickness_${SHIELDTHICK}.000000

#Directory where the MVATools are located
RUNDIR=/usr/gapps/adg/geant4/rat_pac_and_dependency/MVATools

#Source dependencies (only needed if not already defined in environment)
RPDEPENDS=/usr/gapps/adg/geant4/rat_pac_and_dependency
source ${RPDEPENDS}/root-v5.34.00-Minuit2-Python/bin/thisroot.sh
source ${RPDEPENDS}/geant4.10.03/geant4.10.03.p02-build/share/Geant4-10.3.2/geant4make/../../../bin/geant4.sh
source ${RPDEPENDS}/geant4.10.03/geant4.10.03.p02-build/share/Geant4-10.3.2/geant4make/geant4make.sh
source ${RPDEPENDS}/rat-g4.10.03/rat-pac/env.sh
source ${RPDEPENDS}/watchmakers/env_wm.sh
export G4NEUTRONHP_USE_ONLY_PHOTONEVAPORATION=1

#Go to the directory containing the MVATools, then run them
cd $RUNDIR
python $RUNDIR/main.py --singles positron --pc 25pct --tankRadius ${TANKRADIUS}. --shieldThick ${SHIELDTHICK}. --halfHeight ${HALFHEIGHT}. --datadir $DATADIR --buildSB --debug --jobnum 3075
