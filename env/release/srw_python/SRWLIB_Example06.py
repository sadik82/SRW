#############################################################################
# SRWLIB Example#6: Calculating spectral flux of undulator radiation 
# by finite-emittance electron beam collected through a finite aperture
# and power density distribution of this radiation (integrated over all photon energies)
# v 0.02
#############################################################################

from __future__ import print_function #Python 2.7 compatibility
from srwlib import *
import os
import sys

print('SRWLIB Python Example # 6:')
print('Calculating spectral flux of undulator radiation by finite-emittance electron beam collected through a finite aperture and power density distribution of this radiation (integrated over all photon energies)')

#**********************Input Parameters:
strExDataFolderName = 'data_example_06' #example data sub-folder name
strFluxOutFileName = 'ex06_res_flux.dat' #file name for output UR flux data
strPowOutFileName = 'ex06_res_pow.dat' #file name for output power density data
strTrjOutFileName = 'ex06_res_trj.dat' #file name for output trajectory data

#***********Undulator
harmB = SRWLMagFldH() #magnetic field harmonic
harmB.n = 1 #harmonic number
harmB.h_or_v = 'v' #magnetic field plane: horzontal ('h') or vertical ('v')
harmB.B = 1. #magnetic field amplitude [T]
und = SRWLMagFldU([harmB])
und.per = 0.02 #period length [m]
und.nPer = 150 #number of periods (will be rounded to integer)
magFldCnt = SRWLMagFldC([und], array('d', [0]), array('d', [0]), array('d', [0])) #Container of all magnetic field elements

#***********Electron Beam
eBeam = SRWLPartBeam()
eBeam.Iavg = 0.5 #average current [A]
eBeam.partStatMom1.x = 0. #initial transverse positions [m]
eBeam.partStatMom1.y = 0.
eBeam.partStatMom1.z = 0. #initial longitudinal positions (set in the middle of undulator)
eBeam.partStatMom1.xp = 0 #initial relative transverse velocities
eBeam.partStatMom1.yp = 0
eBeam.partStatMom1.gamma = 3./0.51099890221e-03 #relative energy
sigEperE = 0.00089 #relative RMS energy spread
sigX = 33.33e-06 #horizontal RMS size of e-beam [m]
sigXp = 16.5e-06 #horizontal RMS angular divergence [rad]
sigY = 2.912e-06 #vertical RMS size of e-beam [m]
sigYp = 2.7472e-06 #vertical RMS angular divergence [rad]
#2nd order stat. moments:
eBeam.arStatMom2[0] = sigX*sigX #<(x-<x>)^2> 
eBeam.arStatMom2[1] = 0 #<(x-<x>)(x'-<x'>)>
eBeam.arStatMom2[2] = sigXp*sigXp #<(x'-<x'>)^2> 
eBeam.arStatMom2[3] = sigY*sigY #<(y-<y>)^2>
eBeam.arStatMom2[4] = 0 #<(y-<y>)(y'-<y'>)>
eBeam.arStatMom2[5] = sigYp*sigYp #<(y'-<y'>)^2>
eBeam.arStatMom2[10] = sigEperE*sigEperE #<(E-<E>)^2>/<E>^2

#***********Precision Parameters
arPrecF = [0]*5 #for spectral flux vs photon energy
arPrecF[0] = 1 #initial UR harmonic to take into account
arPrecF[1] = 21 #final UR harmonic to take into account
arPrecF[2] = 1.5 #longitudinal integration precision parameter
arPrecF[3] = 1.5 #azimuthal integration precision parameter
arPrecF[4] = 1 #calculate flux (1) or flux per unit surface (2)

arPrecP = [0]*5 #for power density
arPrecP[0] = 1.5 #precision factor
arPrecP[1] = 1 #power density computation method (1- "near field", 2- "far field")
arPrecP[2] = 0 #initial longitudinal position (effective if arPrecP[2] < arPrecP[3])
arPrecP[3] = 0 #final longitudinal position (effective if arPrecP[2] < arPrecP[3])
arPrecP[4] = 20000 #number of points for (intermediate) trajectory calculation

#***********UR Stokes Parameters (mesh) for Spectral Flux
stkF = SRWLStokes() #for spectral flux vs photon energy
stkF.allocate(10000, 1, 1) #numbers of points vs photon energy, horizontal and vertical positions
stkF.mesh.zStart = 30. #longitudinal position [m] at which UR has to be calculated
stkF.mesh.eStart = 10. #initial photon energy [eV]
stkF.mesh.eFin = 20000. #final photon energy [eV]
stkF.mesh.xStart = -0.0015 #initial horizontal position [m]
stkF.mesh.xFin = 0.0015 #final horizontal position [m]
stkF.mesh.yStart = -0.00075 #initial vertical position [m]
stkF.mesh.yFin = 0.00075 #final vertical position [m]

stkP = SRWLStokes() #for power density
stkP.allocate(1, 101, 101) #numbers of points vs horizontal and vertical positions (photon energy is not taken into account)
stkP.mesh.zStart = 30. #longitudinal position [m] at which power density has to be calculated
stkP.mesh.xStart = -0.02 #initial horizontal position [m]
stkP.mesh.xFin = 0.02 #final horizontal position [m]
stkP.mesh.yStart = -0.015 #initial vertical position [m]
stkP.mesh.yFin = 0.015 #final vertical position [m]

#sys.exit(0)

#**********************Calculation (SRWLIB function calls)
print('   Performing Spectral Flux (Stokes parameters) calculation ... ', end='')
srwl.CalcStokesUR(stkF, eBeam, und, arPrecF)
print('done')

#partTraj = SRWLPrtTrj() #defining auxiliary trajectory structure
#partTraj.partInitCond = eBeam.partStatMom1
#partTraj.allocate(20001) 
#partTraj.ctStart = -1.6 #Start Time for the calculation
#partTraj.ctEnd = 1.6
#partTraj = srwl.CalcPartTraj(partTraj, magFldCnt, [1])

#print('   Performing Power Density calculation (from trajectory) ... ', end='')
#srwl.CalcPowDenSR(stkP, eBeam, partTraj, 0, arPrecP)
#print('done')

print('   Performing Power Density calculation (from field) ... ', end='')
srwl.CalcPowDenSR(stkP, eBeam, 0, magFldCnt, arPrecP)
print('done')

#**********************Saving results
#Auxiliary function to write tabulated resulting Intensity data to ASCII file:
def AuxSaveS0Data(stk, filePath):
    f = open(filePath, 'w')
    f.write('#C-aligned Intensity (inner loop is vs photon energy, outer loop vs vertical position)\n')
    f.write('#' + repr(stk.mesh.eStart) + ' #Initial Photon Energy [eV]\n')
    f.write('#' + repr(stk.mesh.eFin) + ' #Final Photon Energy [eV]\n')
    f.write('#' + repr(stk.mesh.ne) + ' #Number of points vs Photon Energy\n')
    f.write('#' + repr(stk.mesh.xStart) + ' #Initial Horizontal Position [m]\n')
    f.write('#' + repr(stk.mesh.xFin) + ' #Final Horizontal Position [m]\n')
    f.write('#' + repr(stk.mesh.nx) + ' #Number of points vs Horizontal Position\n')
    f.write('#' + repr(stk.mesh.yStart) + ' #Initial Vertical Position [m]\n')
    f.write('#' + repr(stk.mesh.yFin) + ' #Final Vertical Position [m]\n')
    f.write('#' + repr(stk.mesh.ny) + ' #Number of points vs Vertical Position\n')
    for i in range(stk.mesh.ne*stk.mesh.nx*stk.mesh.ny): #write all data into one column using "C-alignment" as a "flat" 1D array
        f.write(' ' + repr(stk.arS[i]) + '\n')
    f.close()

#Auxiliary function to write tabulated Trajectory data to ASCII file:
def AuxSaveTrajData(traj, filePath):
    f = open(filePath, 'w')
    f.write('#ct [m], X [m], BetaX [rad], Y [m], BetaY [rad], Z [m], BetaZ [m]\n')
    ctStep = 0
    if traj.np > 0:
        ctStep = (traj.ctEnd - traj.ctStart)/(traj.np - 1)
    ct = traj.ctStart
    for i in range(traj.np):
        f.write(str(ct) + '\t' + repr(traj.arX[i]) + '\t' + repr(traj.arXp[i]) + '\t' + repr(traj.arY[i]) + '\t' + repr(traj.arYp[i]) + '\t' + repr(traj.arZ[i]) + '\t' + repr(traj.arZp[i]) + '\n')        
        ct += ctStep
    f.close()

#print('   Saving trajectory data to file ... ', end='')
#AuxSaveTrajData(partTraj, os.path.join(os.getcwd(), strExDataFolderName, strTrjOutFileName))
#print('done')

print('   Saving intensity data to file ... ', end='')
AuxSaveS0Data(stkF, os.path.join(os.getcwd(), strExDataFolderName, strFluxOutFileName))
AuxSaveS0Data(stkP, os.path.join(os.getcwd(), strExDataFolderName, strPowOutFileName))
print('done')
