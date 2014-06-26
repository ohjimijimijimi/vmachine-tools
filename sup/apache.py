import subprocess
from vmlib.log import log
import vmlib.process

def server_reload(options):
    out, err, returncode = vmlib.process.execute(['service', 'apache2', 'reload'])
    vmlib.process.log(
            '{t.green}Apache was successfully reloaded{t.normal}',
            'There was a problem reloading Apache.',
            err, returncode)

def site_enable(options):
    out, err, returncode = vmlib.process.execute(['a2ensite', options.site.domain])
    vmlib.process.log(
            '{t.green}Site %s enabled successfully{t.normal}' % options.site.domain,
            'There was a problem enabling the site.',
            err, returncode)

def site_disable(options):
    out, err, returncode = vmlib.process.execute(['a2dissite', options.site.domain])
    vmlib.process.log(
            '{t.green}Site %s disabled successfully{t.normal}' % options.site.domain,
            'There was a problem disabling the site.',
            err, returncode)
