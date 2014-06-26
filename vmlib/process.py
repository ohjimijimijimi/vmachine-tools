from vmlib.log import debug,error
import vmlib.log
import subprocess

def execute(cmd, raise_exception=False):
    proc = subprocess.Popen(' '.join(cmd),
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    out, err = proc.communicate()
    if raise_exception and (err is not '' or proc.returncode is not 0):
        raise Exception('Process %s exit with code %s saying: %s' % (proc.returncode, err))

    return out, err, proc.returncode

def log(outmsg, errmsg, err, returncode, throw=False):
    if returncode is not 0:
        error([errmsg, err])
        if throw:
            raise Exception('Subprocess exit with error:[%d]: %s' % (returncode, err))
    else:
        vmlib.log.log(outmsg)
