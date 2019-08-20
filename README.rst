.. -*- mode: rst -*-

|PyPi|_ |Documentation|_ |Travis|_ |Circle|_ |Codecov|_ |Python36|_ |Downloads|_ |License MIT|_

.. |PyPi| image:: https://badge.fury.io/py/pydeco.svg
.. _PyPi: https://badge.fury.io/py/pydeco

.. |Documentation| image:: https://readthedocs.org/projects/pydeco/badge/?version=latest
.. _Documentation: https://pydeco.readthedocs.io/en/latest/?badge=latest

.. |Travis| image:: https://api.travis-ci.org/paulroujansky/pydeco.png?branch=master
.. _Travis: https://travis-ci.org/paulroujansky/pydeco/branches

.. |Circle| image:: https://circleci.com/gh/paulroujansky/pydeco.svg?style=svg
.. _Circle: https://circleci.com/gh/paulroujansky

.. |Codecov| image:: https://codecov.io/gh/paulroujansky/pydeco/branch/master/graph/badge.svg
.. _Codecov: https://codecov.io/gh/paulroujansky/pydeco

.. |Python36| image:: https://img.shields.io/badge/python-3.6-blue.svg
.. _Python36: https://badge.fury.io/py/pydeco

.. |Downloads| image:: https://pepy.tech/badge/pydeco
.. _Downloads: https://pepy.tech/project/pydeco

.. |License MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
.. _License MIT: https://opensource.org/licenses/MIT

PyDeco
======

This package enable to decorate any specified class methods with a passed decorator.
The resulting wrapped class is `picklable`_.

Documentation
^^^^^^^^^^^^^

`PyDeco documentation`_ is available online.

Installing PyDeco
^^^^^^^^^^^^^^^^^

To install the latest stable version of PyDeco, you can use pip in a terminal:

.. code-block:: bash

    pip install -U pydeco

Source code
^^^^^^^^^^^

You can check the latest sources with the command:

.. code-block:: bash

    git clone https://github.com/paulroujansky/pydeco.git

Contributing
^^^^^^^^^^^^

To learn more about making a contribution to PyDeco, please see the `Contributing guide`_.

License
^^^^^^^

This software is licensed under the `MIT license`_.

© 2019 Paul Roujansky.

.. External references:
.. _examples: https://github.com/paulroujansky/pydeco/tree/master/examples
.. _PyDeco documentation: https://pydeco.readthedocs.io/en/latest/
.. _MIT license: http://en.wikipedia.org/wiki/MIT_License
.. _Contributing guide: https://pydeco.readthedocs.io/en/latest/contributing.html
.. _picklable: https://docs.python.org/3/library/pickle.html