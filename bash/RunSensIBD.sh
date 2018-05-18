#!/bin/sh
#MSUB -N WM_MVAKERSRunner #name of job
#MSUB -A ared   #sets bank account
#MSUB -l nodes=1:ppn=1,walltime=23:59:59,partition=borax #uses one node
#MSUB -q pbatch     #pool
#MSUB -o /usr/gapps/adg/geant4/rat_pac_and_dependency/MVAKERS/GridLog_sensibd.log
#MSUB -e /usr/gapps/adg/geant4/rat_pac_and_dependency/MVAKERS/GridErr_sensibd.err
#MSUB -d /usr/gapps/adg/geant4/rat_pac_and_dependency/MVAKERS #dir to run from
#MSUB -V
#MSUB           # no more psub commands
TANKRADIUS=9000.
HALFHEIGHT=9000.
SHIELDTHICKNESS=2074.


RPDEPENDS=/usr/gapps/adg/geant4/rat_pac_and_dependency
MERGEDIR=/p/lscratchh/pershing/watchmakers_9mtank
#MERGEDIR=/p/lscratche/adg/Watchboy/simplifiedData/rp_sim/apr2018/watchmakers_10mtank/
#Source ROOT for python
source ${RPDEPENDS}/root-v5.34.00-Minuit2-Python/bin/thisroot.sh
source ${RPDEPENDS}/geant4.10.03/geant4.10.03.p02-build/share/Geant4-10.3.2/geant4make/../../../bin/geant4.sh
source ${RPDEPENDS}/geant4.10.03/geant4.10.03.p02-build/share/Geant4-10.3.2/geant4make/geant4make.sh
source ${RPDEPENDS}/rat-g4.10.03/rat-pac/env.sh
source ${RPDEPENDS}/watchmakers/env_wm.sh
export G4NEUTRONHP_USE_ONLY_PHOTONEVAPORATION=1

#Go to the directory containing the MVAKERS, then run them
cd $MERGEDIR
watch --newVers -j 1 --sensIBD -N 400 -C 20pct --shieldThick ${SHIELDTHICKNESS} --tankRadius ${TANKRADIUS} --halfHeight ${HALFHEIGHT}
