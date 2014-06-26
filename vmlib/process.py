from vmlib.log import debug
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
