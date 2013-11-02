Extending tutorial
==================


Monitoring a constant
---------------------
To monitor anything with zabby you must write a function and associate
it with a key.

Create a file named 30_constants.py with the following content ::

    def one():
        return 1

    items = {
        'one': one,
    }

And place it in items directory of your zabby configuration
directory(default in debian packages is /etc/zabby/items).

Start or reload zabby, you should see something like this in the log ::

    2013-11-02 20:44:03 DEBUG [zabby.config_manager] Loading items from /etc/zabby/items/30_constants.py

Now you can query zabby for your constant ::

    $ zabby_get one
    1

You've created an extension file for zabby, you've defined a function
that always returns 1 and you have associated it with a key 'one'. Now
every time zabby receives a request with key 'one' it will call this
function and answer with the result of calling this function.


Monitoring content of a file
----------------------------

Say you want to monitor when was the last time that puppet client ran
successfully on a server. You can make puppet do something like this [1]_,
after every successful run ::

    /bin/date +%s > /tmp/puppet_last_run~; mv /tmp/puppet_last_run~ /tmp/puppet_last_run

The only thing needed now is to read the value from a file.

Create a file named 30_puppet.py with the following content ::

    from zabby.core.utils import lines_from_file

    def puppet_last_run():
        '''
        Returns the epoch describing the last time puppet has succesfully ran.

        /tmp/puppet_last_run is filled by puppet client with output from `date +%s`
        '''
        lines = lines_from_file('/tmp/puppet_last_run')
        last_run = lines[0]
        return last_run

    items = {
        'puppet.last_run': puppet_last_run,
    }

Zabby contains some useful function that can be used in extensions.
lines_from_file reads all lines from a file and presents them as a
list.

Run a python interpreter supplying it with created file and call the
function you have just defined ::

    $ sudo -u zabby python -i 30_puppet.py
    >>> puppet_last_run()
    Traceback (most recent call last):
    ...
    IOError: [Errno 2] No such file or directory: '/tmp/puppet_last_run'

If that function went into production you would receive
ZBX_NOTSUPPORTED if /tmp/puppet_last_run was missing on any of your
servers. But absence of this file probably means that puppet never
ran, and we would like to detect such situations.

Edit 30_puppet.py so that puppet_last_run looks like this ::

    def puppet_last_run():
        try:
            lines = lines_from_file('/tmp/puppet_last_run')
            last_run = lines[0]
        except IOError:
            last_run = 0
        return last_run

This way, if file is missing, it is assumed that puppet never ran and
0 is returned to indicate just that.

Run python interpreter again ::

    $ sudo -u zabby python -i 30_puppet.py
    >>> puppet_last_run()
    0
    $ date +%s > /tmp/puppet_last_run
    $ sudo -u zabby python -i 30_puppet.py
    >>> puppet_last_run()
    '1383412855'

Now, if you create a trigger like 'puppet_last_run < (now() - 1h)' it
will generate an event even if /tmp/puppet_last_run is missing.


Monitoring result of executing commands in a shell
--------------------------------------------------
Sometimes it is not practical to write a function in pure python,
especially if you already have a working combination of executable
files.

Say you need to monitor a number of zombie processes. Create a file
named 30_zombie_processes.py with the following content ::

    from zabby.core.utils import sh

    items = {
        "zombie_processes.count": sh("ps -A -o state,pid | grep Z | wc -l"),
    }

sh returns a function that, when called, executes given command in a
shell and returns everything this command has written to standard
output.

Run python interpreter ::

    >>> items['zombie_processes.count']
    <function call_command at 0x7fcb0bdfad70>
    >>> items['ifree.zombie_process.count']()
    '0'

The function returned by sh is now associated with a key.

.. [1] mv is an atomic operation on POSIX systems, while opening,
       writing to a file, flushing and closing it is not an atomic
       operation. Using /bin/date +%s > /tmp/puppet_last_run
       may cause occasional reads of an empty file
