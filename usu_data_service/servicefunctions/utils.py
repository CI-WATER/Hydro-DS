__author__ = 'pkdash'

import shlex
import subprocess


def call_subprocess(cmdString=None, debugString=None):
    cmdargs = shlex.split(cmdString)
    # debFile = open('debug_file.txt', 'w')
    # debFile.write('Starting %s \n' % debugString)
    errorString = "Error in "+debugString+". The message returned from the application is: "
    retValue = subprocess.call(cmdargs,stdout=None)
    if (retValue==0):
        # debFile.write('%s Successful\n' % debugString)
        # debFile.close()
        retDictionary = {'success': "True", 'message': "return value from the application is: "+str(retValue)}
    else:
        # debFile.write('There was error in %s\n' % debugString)
        # debFile.close()
        retDictionary = {'success': "False", 'message': errorString+str(retValue)}

    print('call_subprocess retDictionary:')
    print(retDictionary)
    print('\n')
    print('call_subprocess retValue:' + str(retValue))
    return retDictionary