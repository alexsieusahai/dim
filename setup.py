# have to check if environ is windows, and if it is handle accordingly

import os, sys

shell_name = os.environ["SHELL"].split('/')[-1]
dim_dir = os.getcwd()
os.chdir(os.path.expanduser('~'))
with open('.'+shell_name+'rc', 'a') as fs:
    fs.write('\n'+
            "# this is the alias for dim\n"+
            'alias="python3 '+dim_dir+'/main.py"\n'
            )
