import os

def enum(**enums):
    """
    Return an enum like object.

    enum(ONE=1, TWO=2, THREE=3)
    """
    return type('Enum', (), enums)

def enum_auto(*sequential, **named):
    """
    Return an enum like object.

    enum('ONE', 'TWO', 'THREE')
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

def fix_permission(path, mode, uid, gid):
    os.chmod(path, mode)
    os.chown(path, uid, gid)
