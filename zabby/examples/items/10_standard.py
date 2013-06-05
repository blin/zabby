from zabby import __version__

from zabby.items import vfs, net, proc, vm, system, kernel

items = {
    'agent.ping': lambda: 1,
    'agent.version': lambda: __version__,

    'vfs.fs.size': vfs.fs.size,
    'vfs.fs.inode': vfs.fs.inode,

    'net.if.in': net.interface.incoming,
    'net.if.out': net.interface.outgoing,

    'net.tcp.service': net.tcp.service,

    'proc.num': proc.num,

    'vm.memory.size': vm.memory.size,

    'vfs.dev.read': vfs.dev.read,
    'vfs.dev.write': vfs.dev.write,

    'system.cpu.util': system.cpu.util,
    'system.cpu.load': system.cpu.load,

    'system.hostname': system.hostname,
    'system.uname': system.uname,
    'system.uptime': system.uptime,

    'system.swap.size': system.swap.size,
    'system.swap.in': system.swap.into_memory,
    'system.swap.out': system.swap.out_of_memory,

    'kernel.maxproc': kernel.maxproc,

    'vfs.file.md5sum': vfs.file.md5sum,
}
