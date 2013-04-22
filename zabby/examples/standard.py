from zabby import __version__

from zabby.items import vfs, net

items = {
    'agent.ping': lambda: 1,
    'agent.version': lambda: __version__,

    'vfs.fs.size': vfs.fs.size,
    'vfs.fs.inode': vfs.fs.inode,

    'net.if.in': net.interface.incoming,
}
