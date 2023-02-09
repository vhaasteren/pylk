.. image:: https://github.com/nanograv/PINT/blob/master/docs/logo/PINT_LOGO_128trans.png
   :alt: PINT Logo
   :align: right

Pylk
====

.. image:: https://github.com/nanograv/pint/workflows/CI%20Tests/badge.svg
   :target: https://github.com/nanograv/pint/actions
   :alt: Actions Status

.. image:: https://codecov.io/gh/nanograv/PINT/branch/master/graph/badge.svg?token=xIOFqcKKrP
   :target: https://codecov.io/gh/nanograv/PINT
   :alt: Coverage
   
.. image:: https://readthedocs.org/projects/nanograv-pint/badge/?version=latest
   :target: https://nanograv-pint.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/badge/arXiv-2012.00074-red
   :target: https://arxiv.org/abs/2012.00074
   :alt: PINT Paper on arXiv

.. image:: https://img.shields.io/badge/ascl-1902.007-blue.svg?colorB=262255
   :target: https://www.ascl.net/1902.007
   :alt: PINT on ASCL

.. image:: https://img.shields.io/pypi/l/pint-pulsar
    :target: https://github.com/nanograv/PINT/blob/master/LICENSE.md
    :alt: License:BSD

.. image:: https://img.shields.io/badge/code_of_conduct-Contributor_Covenant-blue.svg
    :target: https://github.com/nanograv/PINT/blob/master/CODE_OF_CONDUCT.md
    :alt: Code of Conduct

Pylk: the pint GUI
------------------

Pylk is a Qt based GUI for PINT, the python pulsar timing package
based on python and modern libraries.

It is still in active development, and it resembles the pintk GUI.
However, it holds the promise to make more advanced methods of
interaction with PINT available to the user.


IMPORTANT Notes!
----------------

PINT/Pylk requires `longdouble` arithmetic within `numpy`, which is currently not supported natively on M1 Macs (e.g., with the `ARM64 conda build <https://conda-forge.org/blog/posts/2020-10-29-macos-arm64/>`_).  So it may be better to install the standard `osx-64` build and rely on Rosetta.

Installing
----------

Install using ``python setup.py develop``

Using
-----

See the online PINT documentation_.  Specifically:

* `tutorials <https://nanograv-pint.readthedocs.io/en/latest/tutorials.html>`_
* `API reference <https://nanograv-pint.readthedocs.io/en/latest/reference.html>`_
* `How to's for common tasks <https://github.com/nanograv/PINT/wiki/How-To>`_

Are you a NANOGrav member?  Then join the #pint channel in the NANOGrav slack.
  
If you have tasks that aren't covered in the material above, you can
email rutger@vhaastaeren.com or one of the people below:

* Rutger van Haasteren (rutger@vhaasteren)

