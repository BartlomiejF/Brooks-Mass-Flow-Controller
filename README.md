# Brooks-Mass-Flow-Controller
For now this project has some basic commands to control mass flow controllers with Brooks Secondary Electronics and computer.



Example of usage:

Considering that the mass flow controller is connected to Secondary Electronics channel number 1 and basic options are properly
chosen. 

import classes
SecondaryElectronics=classes.MFCPanel('/dev/ttyUSB0')
controller=classes.MFC(panel=SecondaryElectronics, channel=1)

controller.OpenCloseValve()

controller.setSPRate(value=15000) 
controller.updatePVRate()
print(controller.PVRate)
