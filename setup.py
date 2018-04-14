# what does vim do?

import os, sys

shell_name = os.environ["SHELL"].split('/')[-1]
dim_dir = os.getcwd()
os.chdir(os.path.expanduser('~'))

with open('.'+shell_name+'rc', 'a') as fs:
    fs.write('\n'+
            "# this is the alias for dim\n"+
            'alias dim="cd '+dim_dir+'/src; python3 main.py"\n'
            )
