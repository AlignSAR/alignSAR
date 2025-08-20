#!/usr/bin/env python3
import os
import sys
import time

def usage():
    print('\nUsage: python sec2hhmmss.py time')
    print('  where time is the time of day in seconds.')
    print(' ')
    print(' Example ')
    print(' sec2hhmmss.py 59800.445398')
    print(' 16:36:40.393')

try:
    timeOfDay = sys.argv[1]
except Exception:
    print('Unrecognized input')
    usage()
    sys.exit(1)

timeOfDay = float(sys.argv[1])

hh = timeOfDay // 3600
timeOfDay = timeOfDay % 3600
mm = timeOfDay // 60
ss = timeOfDay % 60
print(f"{int(hh)}:{int(mm)}:{ss:.3f}")
