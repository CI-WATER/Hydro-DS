__author__ = 'pkdash'

import shlex
import subprocess
import logging

logger = logging.getLogger(__name__)

def call_subprocess(cmdString=None, debugString=None):
    cmdargs = shlex.split(cmdString)
    # debFile = open('debug_file.txt', 'w')
    # debFile.write('Starting %s \n' % debugString)
    errorString = "Error in " + debugString + ". The message returned from the application is: "
    retValue = subprocess.call(cmdargs, stdout=None)
    if (retValue==0):
        # debFile.write('%s Successful\n' % debugString)
        # debFile.close()
        logger.info("subprocess success." + debugString + ". Return value from the application is: " + str(retValue))
        retDictionary = {'success': "True", 'message': debugString + ". Return value from the application is: "
                                                       + str(retValue)}
    else:
        # debFile.write('There was error in %s\n' % debugString)
        # debFile.close()
        logger.error("subprocess failed." + debugString + ". Return value from the application is: " + str(retValue))
        retDictionary = {'success': "False", 'message': errorString + str(retValue)}

    # print('call_subprocess retDictionary:')
    # print(retDictionary)
    # print('\n')
    # print('call_subprocess retValue:' + str(retValue))
    return retDictionary

