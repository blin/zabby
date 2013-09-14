========
Pyzabbix
========
This is alternative implementation of zabbix_ agent in python.

Main goal of porting to python is to provide administrators with an easy way to understand how items work.
Instead of digging through C source code(that you have to download first) you can read well documented(and tested!)
python code on your machine and execute it.

Use case
--------
Imagine that you need to understand why "vfs.fs.inode" does not work on some of your servers with NFS partitions.

.. code-block:: sh

    % grep -l 'vfs.fs.size' /etc/zabby/items/*
    /etc/zabby/items/standard.py

In standard.py you will find an import statement pointing you to zabby/items/vfs/fs.py .
There you can find function definition which clearly defines dependency on operating system capabilities.

.. code-block:: sh

    % grep 'depends on' zabby/items/vfs/fs.py
    ...
        :depends on: [host_os.fs_inodes]
    ...

Than you can look at zabby/hostos/${YOUR_OS}.py and even import it and call the function in question.

.. code-block:: python

    >>> from zabby.hostos import detect_host_os
    >>> host_os = detect_host_os()
    >>> # from zabby.hostos.linux import Linux
    ... # host_os = Linux()
    ... 
    >>> host_os.fs_inodes('/mnt/nfs')
    (0, 0)
    >>> help(host_os.fs_inodes)

    fs_inodes(self, filesystem) method of zabby.hostos.linux.Linux instance
        Uses statvfs system call to obtain information about filesystem

Turns out, the problem is somewhere on a kernel level
(in my case, i had an outdated kernel that didn't support inode counting on NFS).

Differences from zabbix agent
-----------------------------
You can not specify later item arguments if you specify former.

system.cpu.util[,idle] will be treated as system.cpu.util(cpu='', state='idle', mode='avg1') and you probably don't have ''th cpu.

You should pass 'all processes' and 'all users' to proc.num explicitly, proc[,root] should be proc[all processes,root]

Oldest supported linux kernel version is 2.6.26

Testing
-------
All tests are done using nose_ . Tests are currently separated as os dependent and os independent. 
Run os independent tests:

.. code-block:: sh

    nosetests -a '!os'

Run os dependent tests(os dependent tests for linux will not run on BSD, so you can't just run -a 'os'):

.. code-block:: sh

    nosetests -A "os == '${YOUR_OS}'"
    # nosetests -A "os == 'linux'"

To run os independent tests on all supported python version use tox_ .
tox.ini is provided and includes all python environments supported by zabby(py26 through py33).
You should try to test at least one py2 env and at least one py3 env.

After running tox you can run zabby in a virtualenv:

.. code-block:: sh

    source .tox/py26/bin/activate
    zabby -c zabby/examples/config.py

.. _zabbix: http://www.zabbix.com/
.. _nose: https://nose.readthedocs.org/
.. _tox: http://tox.readthedocs.org
