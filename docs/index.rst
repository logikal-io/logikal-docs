.. toctree::
    :caption: Documentation
    :hidden:

    self
    development
    license

.. toctree::
    :caption: External Links
    :hidden:

    Release Notes <https://github.com/logikal-io/logikal-docs/releases>
    Issue Tracker <https://github.com/logikal-io/logikal-docs/issues>
    Source Code <https://github.com/logikal-io/logikal-docs>

Getting Started
===============
The logikal-docs package provides the ``docs`` command-line tool which simplifies Python
documentation building and management.

You can install logikal-docs from `pypi <https://pypi.org/project/logikal-docs/>`_:

.. code-block:: shell

    pip install logikal-docs

Once installed, you may build your documentation by executing ``docs -b`` in the root of your
Python project, after which you can open your current documentation in the browser by executing
``docs``. You can always access a short usage help by executing ``docs --help`` or ``docs -h``.

Configuration
-------------
The documentation is built with `Sphinx <https://www.sphinx-doc.org/en/master/>`_ using the `Read
the Docs Sphinx theme <https://sphinx-rtd-theme.readthedocs.io/en/stable/>`_. Note that we
pre-configure Sphinx building and output and we also read out and forward the necessary project
information from your ``pyproject.toml`` file, therefore you typically only need to add and
configure your own extensions in your ``docs/conf.py`` file (which is now optional). Additionally,
we use an improved theme style file with well-defined fonts and a more fluid responsive user
experience, among other minor patches.

We use the available git tags starting with ``v[0-9]`` to identify the current version and to
populate the automatically generated version selection panel.

Jupyter
-------
You can install logikal-docs with `Jupyter <https://jupyter.org/>`_ support:

.. code-block:: shell

    pip install logikal-docs[jupyter]

This allows you to run and render the result of arbitrary Python statements (via the `Jupyter
Sphinx extension <https://jupyter-sphinx.readthedocs.io/en/latest/>`_):

.. jupyter-execute::

    from pandas import DataFrame

    DataFrame({
        'Movie': ['The Lord of the Rings', 'Back to the Future', 'Blade Runner'],
        'Budget [M USD]': [93, 19, 30],
        'Box Office [M USD]': [898, 389, 42],
    })
