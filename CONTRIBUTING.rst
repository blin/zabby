Contributing
============

Testing
-------
All tests are done using nose_ . Tests are currently separated as os
dependent and os independent. Run os independent tests:

.. code-block:: sh

    nosetests -a '!os'

Run os dependent tests(os dependent tests for linux will not run on
BSD, so you can't just run -a 'os'):


.. code-block:: sh

    nosetests -A "os == '${YOUR_OS}'"
    # nosetests -A "os == 'linux'"

To run os independent tests on all supported python version use tox_ .
tox.ini is provided and includes all python environments supported by
zabby(py26 through py33). You should try to test at least one py2 env
and at least one py3 env.


After running tox you can run zabby in a virtualenv:

.. code-block:: sh

    source .tox/py26/bin/activate
    zabby -c zabby/examples/config.py

.. _nose: https://nose.readthedocs.org/
.. _tox: http://tox.readthedocs.org
