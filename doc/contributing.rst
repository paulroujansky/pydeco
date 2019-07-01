.. _contributing_ref:

=======================
Contribution guidelines
=======================

Tests
-----

Before committing, from within the main directory, run:

.. code-block:: bash

    pytest

This will run `pytest <https://docs.pytest.org/en/latest/>`_, and run all the
existing unit tests to make sure you haven't broken any of the existing
codebase.

Style
-----

Before committing, from within the main directory, run:

.. code-block:: bash

    make pep

This will run ``pydocstyle``, ``flake``, and ``docspell`` to scan for all kinds
of errors in your code (syntax, style, and docstrings).