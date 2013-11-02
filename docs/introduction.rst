Introduction
============

Goals
-------------

- Be easy to understand
- Be easy to modify
- Be easy to extend and maintain extensions

Maturity
--------
Zabby is used on all production Linux servers at i-Free_ since august
2013, this includes debian lenny(we are building required python 2.6
packages), squeeze and wheezy.

There are plans to use zabby to monitor windows servers.

.. _i-Free: http://www.i-free.com/

How zabby works
---------------
Zabby's only function is to answer requests of the following
form(zabbix format) ::

    key[argument1,argument2]

Answers are calculated by looking up [1]_ functions by key and calling them
with provided arguments, like so(python call) ::

    functions[key](argument1, argument2)

Result of this call will be sent as a response.

If anything unexpected happens(there is no function associated with
key, wrong arguments are provided for function, function throws
exception) ZBX_NOTSUPPORTED will be sent as a response.

.. [1] Key/function associations are obtained from `python files`_. If
       there are several functions with the same key, zabby will use
       function that was loaded last.


.. _`python files`: https://github.com/blin/zabby/blob/master/zabby/examples/items/10_standard.py
