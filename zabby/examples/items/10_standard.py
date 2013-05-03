from zabby import __version__

from zabby.items import vfs, net, proc, vm, system, kernel

items = {
    'agent.ping': lambda: 1,
    'agent.version': lambda: __version__,

    'vfs.fs.size': vfs.fs.size,
    'vfs.fs.inode': vfs.fs.inode,

    'net.if.in': net.interface.incoming,
    'net.if.out': net.interface.outgoing,

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

    'kernel.maxproc': kernel.maxproc,
}
