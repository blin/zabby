Zabby
=====

This is alternative implementation of zabbix_ agent in python.


Documentation
-------------

You can find installation instructions and tutorials here_

.. _here: http://zabby.readthedocs.org/


Differences from zabbix agent
-----------------------------

- You can not specify later item arguments if you specify former.

- system.cpu.util[,idle] will be treated as system.cpu.util(cpu='',
  state='idle', mode='avg1') and you probably don't have ''th cpu.

- You should pass 'all processes' and 'all users' to proc.num
  explicitly, proc[,root] should be proc[all processes,root]


.. _zabbix: http://www.zabbix.com/
