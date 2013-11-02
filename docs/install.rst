Installation
============

From source
-----------

You can clone the public repo: ::

    $ git clone https://github.com/blin/zabby.git

Or download tarball_.

Once you have the source, you can install it into your site-packages with ::

    $ python setup.py install

After installing zabby run it with ::

    $ zabby -c /usr/local/lib/python2.6/dist-packages/zabby/examples/config.py

Config path will differ, based on your python version

.. _tarball: https://github.com/blin/zabby/tarball/master

From debian package
-------------------

Install build dependencies ::

    $ aptitude install devscripts build-essential

Build ::

    $ debuild

Install ::

    $ dpkg -i ../zabby*.deb

Zabby will be started automatically by post-install script.

Testing your installation
-------------------------

After installing and running zabby query it with ::

    $ zabby_get agent.ping
