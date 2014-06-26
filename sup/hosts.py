from __future__ import print_function
import uuid
import os
import shutil
from vmlib.log import log,emptyline,debug
import vmlib.process

def clone_tpl(options):
    with open(options.apache.vhost.tpl, 'r') as f:
        vhost_tpl = f.read()
        vhost_content = vhost_tpl.format(domain=options.site.domain, documentroot=options.site.root, mail=options.site.mail)
        with open(os.path.join(options.apache.vhost.path, options.site.domain + '.conf'), 'w') as vhost_file:
            print(vhost_content, file=vhost_file)
        vhost_file.closed
    f.closed

def entry_add(options):
    if entry_exists(options):
        return
    temp_hosts = os.path.join('/tmp', 'hosts__' + str(uuid.uuid1()))
    shutil.copyfile(options.hosts.path, temp_hosts)
    with open(options.hosts.path, 'a') as f:
        print('127.0.0.1\t%s' % options.site.domain, file=f)
        if options.site.alias is not None:
            [ print('127.0.0.1\t%s' % alias, file=f) for x in options.site.alias.split(',') ]
    f.closed
    log(['{t.green}Hosts entry added successfully{t.normal}', 'You can restore the previous version of /etc/hosts executing:', '\tsudo mv %s %s' % (temp_hosts, options.hosts.path)])
    emptyline()

def entry_remove(options):
    pass

def entry_exists(options):
    out, err, returncode = vmlib.process.execute(['grep', '-q', options.site.domain, options.hosts.path])
    if returncode is 0:
        return False
    else:
        log('{t.yellow}There are already an entry for %s in %s. {t.bold}{t.green}Skip{t.normal}' % (options.site.domain, options.hosts.path))
        return True
