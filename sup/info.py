from vmlib.log import log,debug,error,warning,emptyline
from blessings import Terminal
import subprocess
import vmlib.process
import os
import re

t = Terminal()

def apache(options):
    """
    Get Apache info
    """
    return [
            apache_version(),
            site(options)
            ]

def apache_version():
    """
    Get the running apache version
    """
    out, err, _ = vmlib.process.execute(['a2query', '-v'])
    return ('Apache version: {t.bold}%s' % out[:-1]).format(t=t)

def site(options):
    """
    Get the a2query site info
    """
    out, err, _ = vmlib.process.execute(['a2query', '-s', '%s' % options.site.domain])
    if out is not '':
        return ('Site status: {t.bold}%s' % out[:-1]).format(t=t)
    else:
        return ('Site status: {t.bold}{t.red}%s' % err[:-1]).format(t=t)

def documentroot(options):
    """
    Get information on project root folder
    - the project path
    - the site root path
    - the size of the project path
    - the tree structure of the project path
    """
    return [
            ('The project path is: {t.bold}%s' % options.project.root).format(t=t),
            ('The site root is: {t.bold}%s' % options.site.root).format(t=t),
            documentroot_size(options),
            documentroot_tree(options)
            ]

def documentroot_size(options):
    """
    Get the filesystem usege stat
    """
    out, err, _ = vmlib.process.execute(['du -sh %s | cut -sf1' % options.project.root])
    if out is not '':
        return ('The project folder use: {t.bold}%s' % out[:-1]).format(t=t)
    else:
        return ('The project folder use: {t.bold}{t.red}%s' % err[:-1]).format(t=t)

def documentroot_tree(options):
    """
    Get tree structure of project root
    """
    out, _, _ = vmlib.process.execute(['tree', '%s' % options.project.root])
    if out.split('\n')[0].find('[error') is not 0:
        error = re.sub(r'.*\[([^\]]+)\].*', r'\1', out.split('\n')[0])
        return ('Project folder tree: {t.bold}{t.red}%s' % error).format(t=t)
    else:
        return ('Project folder tree \n{t.bold}%s' % out[:-1]).format(t=t)

def database(options):
    pass

def archive(options):
    pass

def callback(options):
    info = apache(options)
    info += documentroot(options)
    #info += database(options)
    #info += archive(options)
    log(info)
    emptyline()


