

def action_callback_create(args, config, options):
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

