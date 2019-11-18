.. _contributing:

============
Contributing
============

``itty3`` gladly accepts contributions that:

* are respectful to everyone
* inclusive by default (we're all human)
* report/fix Real World™ problems

If this list offends you or you feel you can't follow these guidelines,
you're welcome to use other frameworks or to not contribute.

Ways To Contribute
==================

In easy-to-harder order:

* File an issue/bug report
* Add/update documentation
* Add test coverage
* Add feature code

File An Issue/Bug Report
========================

If you encounter a bug or a shortcoming in ``itty3``, one of the easiest
ways to help is to create a `GitHub Issue`_.

Simply click the link and fill out the template.

The more detail you can provide, the easier it will be to reproduce your
issue & get it resolved.

Thanks for the help!

Add/Update Documentation
========================

Documentation is crucial in understanding & using software libraries.
And ``itty3``'s documentation is no exception.

That said, mistakes & omissions happen. Helping fix the documentation is
an easy way to help everyone!

To submit a documentation addition/update:

* Fork the repository on GitHub
* Clone your fork to your local machine (or edit in the GitHub UI)
* Create a new branch with ``git``
* Change the documentation in question (located in the ``docs/`` folder)
* Add your changes via ``git``
* Commit the changes to your branch
* Push the branch back to GitHub
* Open a `Pull Request`_ for your branch
* Fill out the template & submit!

*With apologies to Edgar Allen Poe,...*
Quoth the raven: ``Documentation forevermore!``

Add Test Coverage
=================

All software has bugs. Tests prove that the code works as intended.

To submit a test addition/update:

* Fork the repository on GitHub
* Clone your fork to your local machine (or edit in the GitHub UI)
* Create a new branch with ``git``
* Create a ``virtualenv``/``pipenv`` for the repository & activate it
* Run ``$ pip install pytest``
* Run ``$ pytest tests`` & ensure they're passing.
* Make your changes/additions to test files.
* Run ``$ pytest tests`` again & ensure your changes pass.
* Add your changes via ``git``
* Commit the changes to your branch
* Push the branch back to GitHub
* Open a `Pull Request`_ for your branch
* Fill out the template & submit!

I ``:heart:`` more tests, always.

Add Feature Code
================

Most everyone loves new features. As long as new features fall within
the :ref:`philosophy` of ``itty3``, they're welcomed & appreciated!

To submit a new feature:

* Fork the repository on GitHub
* Clone your fork to your local machine (or edit in the GitHub UI)
* Create a new branch with ``git``
* Create a ``virtualenv``/``pipenv`` for the repository & activate it
* Run ``$ pip install pytest``
* Run ``$ pytest tests`` & ensure they're passing.
* Add your feature work.
* Ensure the new feature has a docstring if it's public API.
* Ensure the new feature matches existing code style (``black`` is nice here).
* Add documentation to the main guides as appropriate.
* Run ``$ pytest tests`` again & ensure your changes pass.
* Add your changes via ``git``
* Commit the changes to your branch
* Push the branch back to GitHub
* Open a `Pull Request`_ for your branch
* Fill out the template & submit!

You da bes!

.. _`GitHub Issue`: https://github.com/toastdriven/itty3/issues/new
.. _`Pull Request`: https://github.com/toastdriven/itty3/compare
