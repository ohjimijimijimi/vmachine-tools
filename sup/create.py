import os
import vmlib.lib
from vmlib.log import log,error,emptyline
import sup.hosts
import sup.apache

def callback(options):
    """
    0. Check if command create could be executed
    1. Make the folders
    2. Fix permissions
    3. Build the VHost
    4. Enable the site
    5. Reload Apache
    6. Add the entry into local /etc/hosts
    """

    # 0. Check if command create could be executed
    verify_environment(options)

    # 1. Make the folders
    os.makedirs(options.site.root)

    # 2. Fix permissions
    vmlib.lib.fix_permission(options.project.root, 0775, options.user.uid, options.user.gid)

    # 3. Build VHost file
    sup.hosts.clone_tpl(options)

    # 4. Enable the site
    sup.apache.site_enable(options)

    # 5. Reload Apache
    sup.apache.server_reload(options)

    # 6. Add entry to /etc/hosts
    sup.hosts.entry_add(options)

    emptyline()
    log('Now you can access to http://%s from your browser.' % options.site.domain)
    emptyline()

def verify_environment(options):
    """
    Verify if command create could be executed
    1. check directories
    """

    # 1. check directories
    if os.path.exists(options.project.root):
        error(['Cannot execute command {t.green}%s{t.red}.' % options.command, 'A site named {t.yellow}%s{t.red} seems to exist already.' % options.site.domain, 'It\'s better you take a look before making some mistakes!'])
        emptyline()
        raise Exception('Site already exists')
