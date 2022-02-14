import os
import sys

if len(sys.argv)<3:
    print('Please Input Two Arguments')
    sys.exit(1)
arg0=sys.argv[1]
arg1=sys.argv[2]

os.system('./test_shell_2_para.sh '+arg0+' '+arg1)
