import time
from PH_Sensor import PH
phvalue = 0 

#for x in range(10):
phvalue += PH.getPHValue(30.0)

#phlast = phvalue/10.0
print(phvalue)
