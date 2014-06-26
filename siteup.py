#!/usr/bin/env python

from __future__ import print_function
from vmlib.log import log,warning,error,debug, emptyline
from vmlib.lib import enum
from vmlib.jsonconfig import JSONConfig
import sup.info
import json
import argparse
import os
import shutil
import subprocess
import uuid
import time

Actions = enum(CREATE='add', DESTROY='remove', ALIAS='alias', INFO='info')

parser = argparse.ArgumentParser(
    description='Install the environment for a new site under Apache 2 - Ubuntu',
    epilog='!!! REMEMBER: TO RUN THIS SCRIPT YOU MUST HAVE ROOT PRIVILEGES !!!')
parser.add_argument('command', metavar='COMMAND', help='the command to execute')
parser.add_argument('domain', metavar='DOMAIN', help='the domain name eg. example.com')
parser.add_argument('--root', help='the root folder of you project')
parser.add_argument('--siteroot', help='the folder for your site root', default='site')
parser.add_argument('--destroy', help='destroy an existing site', action='store_true')
parser.add_argument('--redo', help='rewrite an existing site', action='store_true')
parser.add_argument('--config', help='configuration folder', default=os.path.expanduser('~/.siteup'))
parser.add_argument('--alias', help='add the domain as an alias to')
parser.add_argument('--info', help='show information about the domain')

# Need to be root
euid = os.geteuid()
if euid is not 0:
    parser.print_help()

    raise EnvironmentError, "Need to be root!"

args = parser.parse_args()

# get login user uid
login = os.getlogin()
login_uid = int(os.popen("id -u %s" % login).read().strip())
login_gid = int(os.popen("id -g %s" % login).read().strip())

# set default root based on domain
if args.root is None:
    args.root = '/var/www/%s' % args.domain

siteroot = os.path.join(args.root, args.siteroot)

hosts_file = '/etc/hosts'


#debug(args)

def __fix_permission(path, mode, uid, gid):
    os.mkdir(path, mode)
    os.chown(path, uid, gid)

def check_configuration(args):
    """
    Check if the configuration folder exists.
    if not exists
        create the folder
        initialize the VHost template
    """
    if not os.path.exists(args.config):
        os.mkdir(args.config, 0755)
        os.chown(args.config, login_uid, login_gid)

    # if not exists create the VHost template
    vhosttemplate = 'vhost.tpl'
    vhostpath = os.path.join(args.config, vhosttemplate)
    if not os.path.exists(vhostpath):
        f = open(vhostpath, 'w')
        print('<VirtualHost *:80>', file=f)
        print('\tServerName {domain}', file=f)
        print('\tServerAlias {domain}' , file=f)
        print('\tServerAdmin {mail}', file=f) # TODO: get the mail from the command line
        print('\tDocumentRoot {documentroot}/', file=f)
        print('\t<Directory "{documentroot}">', file=f)
        print('\t\tOptions -Indexes -FollowSymlinks', file=f)
        print('\t\tAllowOverride All', file=f)
        print('\t\tOrder allow,deny', file=f)
        print('\t\tAllow from all', file=f)
        print('\t</Directory>', file=f)
        print('</VirtualHost>', file=f)
        f.close();
        os.chown(vhostpath, login_uid, login_gid)

    # if not exists create a basic configuration
    configpath = os.path.join(args.config, 'config')
    if not os.path.exists(configpath):
        config = {
                'apache': {
                    'config path': '/etc/apache2',
                    'vhost dir': 'sites-available'
                    },
                'vhost template': vhosttemplate
                }
        f = file(configpath, 'w')
        f.write(json.dumps(config, sort_keys=True, indent=4, separators=(',', ': ')))
        f.close()


#def get_action(args):
#     default action is create
#    if args.redo is False and args.destroy is False and args.alias is None:
#        return Actions.CREATE
#    elif args.destroy is True:
#        return Actions.DESTROY
#    elif args.redo is True:
#        return Actions.RECREATE
#    elif args.alias is not None:
#        return Actions.ALIAS
#    else:
#        return Actions.CREATE

def action_callback_create(args, config):
    """
    1. Make the folders
    2. Fix permissions
    3. Build the VHost
    4. Enable the site
    5. Reload Apache
    6. Add the entry into local /etc/hosts
    """
    sitepath = os.path.join(args.root, args.siteroot)

    # 1. Make the folders
    os.makedirs(os.path.join(args.root, args.siteroot))

    # 2. Fix permissions
    os.chmod(args.root, 0775)
    os.chmod(sitepath, 0775)
    os.chown(args.root, login_uid, login_gid)
    os.chown(sitepath, login_uid, login_gid)

    # 3. Build VHost
    with open(os.path.join(args.config, config.get('vhost_template')), 'r') as f:
        vhosttpl = f.read()
        vhost_data = vhosttpl.format(domain=args.domain, documentroot=sitepath, mail='webmaster@localhost')
        vh = open(os.path.join(config.get('apache.config_path'), config.get('apache.vhost_dir'), args.domain + '.conf'), 'w')
        print(vhost_data, file=vh)
        vh.close()
    f.closed

    # 4. Enable the site
    __enable_site(args, config)

    # 5. Reload Apache
    __reload_apache(args, config)

    # 6. Add entry to /etc/hosts
    hosts_file = '/etc/hosts'
    temp_hosts = os.path.join('/tmp', 'hosts__' + str(uuid.uuid1()))
    shutil.copyfile(hosts_file, temp_hosts)
    with open(hosts_file, 'a') as hosts:
        print('127.0.0.1\t%s' % args.domain, file=hosts)
    f.closed
    log(['You can restore the previous version of /etc/hosts executing:', '\tsudo mv %s %s' % (temp_hosts, hosts_file)])
    emptyline()
    log('Now you can access to %s from your browser.' % args.domain)

def action_callback_recreate(args, config):
    """
    1. Call destroy callback
    2. Call create callback with new args
    """
    pass


def __backup_hosts_file():
    temp_hosts = os.path.join('/tmp', 'hosts__' + str(uuid.uuid1()))
    shutil.copyfile(hosts_file, temp_hosts)
    return temp_hosts

def __log_info_backup_hosts(temp, path):
    log(['You can restore the previous version of %s executing:' % path, '\tsudo mv %s %s' % (temp, path)])

def __add_hosts_entry(args, config):
    temp_hosts = __backup_hosts_file()
    with open(hosts_file, 'a') as hosts:
        print('127.0.0.1\t%s' % args.domain, file=hosts)
    f.closed
    __log_info_backup_hosts(temp_hosts, hosts_file)

def __remove_hosts_entry(args, config):
    temp_hosts = __backup_hosts_file()
    cmd = ['sed', '-i', "'/%s/d'" % args.domain, '/etc/hosts']
    proc = subprocess.Popen(' '.join(cmd), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    debug(out)
    debug(err)
    debug(proc.returncode)
    __log_info_backup_hosts(temp_hosts, hosts_file)

def __disable_site(args, config):
    cmd = ['a2dissite', args.domain]
    proc = subprocess.Popen(' '.join(cmd), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    debug(out)
    debug(err)
    debug(proc.returncode)

def __enable_site(args, config):
    cmd = ['a2ensite', args.domain]
    proc = subprocess.Popen(' '.join(cmd), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    debug(out)
    debug(err)
    debug(proc.returncode)

def __reload_apache(args, config):
    cmd = ['service', 'apache2', 'reload']
    proc = subprocess.Popen(' '.join(cmd), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    debug(out)
    debug(err)
    debug(proc.returncode)

def __clean_filesystem(args, config):
    shutil.rmtree(args.root)
    os.remove(os.path.join(config.get('apache.config_path'), config.get('apache.vhost_dir'), args.domain + '.conf'))

def action_callback_destroy(args, config):
    """
    1. Disable the site
    2. Reload Apache
    3. Make an archive of the site
    4. Remove VHost
    5. Remove directories
    """
    # 1. Disable the site
    __disable_site(args, config)

    # 2. Reload Apache
    __reload_apache(args, config)

    # 3. Make an archive of the site
    backup_folder = os.path.join(args.config, 'backup')
    if not os.path.exists(backup_folder):
        os.mkdir(backup_folder, 0755)
        __fix_permission(backup_folder, 0755, login_uid, login_gid)

    archive_name = os.path.join(backup_folder, '-'.join([args.domain, time.strftime('%Y%m%dT%H%M%S'), str(uuid.uuid1())]))
    shutil.make_archive(archive_name, 'gztar', siteroot)
    __fix_permission(archive_name, 0644, login_uid, login_gid)

    # 4. Remove hosts entry
    __remove_hosts_entry(args, config)

    # 5. Remove directories
    __clean_filesystem(args, config)

def __check_site_status(args, config, out):
    pass

def __vhost_add_alias(args, config):

    temp_hosts = __backup_file()
    cmd = ['sed', '-i', "'/%s/d'" % args.domain, '/etc/hosts']
    proc = subprocess.Popen(' '.join(cmd), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    debug(out)
    debug(err)
    debug(proc.returncode)
    __log_info_backup_hosts(temp_hosts, hosts_file)

def action_callback_alias(args, config):
    """
    1. Check if the main domain exists
    2. Add the alias to VHost
    3. Reload Apache
    4. Add entry in /etc/hosts
    """
    # 1. Check if the main domain exists
    site_status = __check_site_status(args, config)
    if site_status is not SiteStatus.ENABLED:
        warning('The requested site %s is not enabled' % args.domain)
        exit()
    # 2. Add the alias
    __vhost_add_alias(args, config)

    # 3. Reload Apache
    __reload_apache(args, config)

    # 4. Add entry to /etc/hosts
    __add_hosts_entry(args, config)

def action_callback_info(args, config):
    info = sup.info.apache(args, config)
    info += sup.info.documentroot(args, config)
    #info += sup.info.database(args, config)
    #info += sup.info.archive(args, config)

    log(info)
    emptyline()

action_callbacks = {
        Actions.CREATE: action_callback_create,
        Actions.DESTROY: action_callback_destroy,
        Actions.ALIAS: action_callback_alias,
        Actions.INFO: action_callback_info
        }

def record_site(info):
    """
    Save the site confoguration into the config file.
    """
    pass

def remember_site(domain):
    """
    Load the site configuration from the config file.
    """
    pass

############ MAIN ############

check_configuration(args)
config = JSONConfig(os.path.join(args.config, 'config'))

log('Executing {t.bold}{t.green}%s {t.normal}on {t.bold}{t.yellow}%s' % (args.command, args.domain))
emptyline()

if args.command in action_callbacks:
    action_callbacks[args.command](args, config)
else:
    error('Command %s don\'t recognized.' % action)
