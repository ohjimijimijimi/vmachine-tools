import subprocess
import vmlib.process
import os
from blessings import Terminal

t = Terminal()

def apache(args, config):
    """
    Get Apache info
    """
    return [
            apache_version(),
            site(args)
            ]

def apache_version():
    """
    Get the running apache version
    """
    apache_version, _, _ = vmlib.process.execute(['a2query', '-v'])
    return ('Apache version: {t.bold}%s' % apache_version[:-1]).format(t=t)

def site(args):
    """
    Get the a2query site info
    """
    site_info, _, _ = vmlib.process.execute(['a2query', '-s', "%s" % args.domain])
    return ('Site status: {t.bold}%s' % site_info[:-1]).format(t=t)

def documentroot(args, config):
    """
    Get information on project root folder
    - the project path
    - the site root path
    - the size of the project path
    - the tree structure of the project path
    """
    tree = subprocess.check_output('tree %s' % args.root, shell=True)[:-1]

    return [
            ('The project path is: {t.bold}%s' % args.root).format(t=t),
            ('The site root is: {t.bold}%s' % os.path.join(args.root, args.siteroot)).format(t=t),
            ('The project folder use: {t.bold}%s' % subprocess.check_output('du -sh %s | cut -sf1' % args.root, shell=True)[:-1]).format(t=t),
            ('Project folder tree \n{t.bold}%s' % tree).format(t=t)
            ]

def database(args, config):
    pass

def archive(args, config):
    pass
