# rs5_test.py
#
# use localnet  E459abb
#
# python -i ..\py3\startup.py

import requests
# import rwsuis
from rwsuis import RWS

norbert = 'http://152.94.0.38'

#  Hmmm
# c:>curl --digest -u "Default User":robotics "http://152.94.0.38/rw/panel/ctrlstate"
#                     ^
# SyntaxError: invalid syntax

auth=requests.auth.HTTPDigestAuth('Default User', 'robotics')
response = requests.get(norbert+"/rw/panel/ctrlstate", auth=auth)
print(response)
print(response.text)

new_rt = [0,0,314] 
robot = RWS.RWS(norbert)
robot.request_rmmp()
 
robot.set_robtarget_translation("target_K0", new_rt)   # a valid (VAR) robtarget in RAPID

# exit()