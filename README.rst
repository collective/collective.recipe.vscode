.. image:: https://img.shields.io/pypi/status/collective.recipe.vscode.svg
    :target: https://pypi.org/project/collective.recipe.vscode/
    :alt: Package Status

.. image:: https://img.shields.io/travis/collective/collective.recipe.vscode/master.svg
    :target: http://travis-ci.org/nazrulworld/collective.recipe.vscode
    :alt: Travis Build Status

.. image:: https://img.shields.io/coveralls/collective/collective.recipe.vscode/master.svg
    :target: https://coveralls.io/r/collective/collective.recipe.vscode
    :alt: Test Coverage

.. image:: https://img.shields.io/pypi/pyversions/collective.recipe.vscode.svg
    :target: https://pypi.org/project/collective.recipe.vscode/
    :alt: Python Versions

.. image:: https://img.shields.io/pypi/v/collective.recipe.vscode.svg
    :target: https://pypi.org/project/collective.recipe.vscode/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/collective.recipe.vscode.svg
    :target: https://pypi.org/project/collective.recipe.vscode/
    :alt: License


.. contents::

Introduction
============

``collective.recipe.vscode`` is the buildout recipe for `Visual Studio Code`_ lover who wants python IDE like features while developing python `Buildout`_ based project. This tool will help them to create per project basis vscode settings with appropriate paths location assignment. Currently ``collective.recipe.vscode`` comes with supporting autocompletation.
A general question may arise that why we will use this tool, whether we can create `Visual Studio Code`_ project settings easily (we have better knowledge over `Visual Studio Code`_ configuration)?
Well i completely agree with you, but if you want to get benefited from `Anaconda`_ or `Jedi`_'s python autocompletion feature (basically I am lover of autocompletion), you have to add all eggs links for `Anaconda`_ or `Jedi`_'s paths settings and it is hard to manage eggs links manually if the size of project is big (think about any `Plone`_ powered project), beside `Sublimelinter-Pylint`_ also need list of paths to be added to sys.path  to find modules.

Installation
============

Install ``collective.recipe.vscode`` is simple enough, just need to create a section for ``vscode`` to your buildout. Before using ``collective.recipe.vscode`` make sure  `Jedi`_, `Sublimelinter`_, `Sublimelinter-Flake8`_ and/or `Sublimelinter-Pylint`_ plugins are already installed at your `Visual Studio Code`_. You could follow full [`instruction here
<https://nazrulworld.wordpress.com/2017/05/06/make-sublime-text-as-the-best-ide-for-full-stack-python-development>`_] if not your `Visual Studio Code`_ setup yet. Flake8 linter need `flake8 executable <https://pypi.python.org/pypi/flake8>`_ available globally (unless you are going to use local flake8), also it is recommended you install some awsome flake8 plugins (flake8-isort, flake8-coding, pep8-naming, flake8-blind-except, flake8-quotes and more could find in pypi)

    Example Buildout::

        [buildout]
        parts += vscode

        [vscode]
        recipe = collective.recipe.vscode
        eggs = ${buildout:eggs}
        jedi-enabled = True
        sublimelinter-enabled = True
        sublimelinter-pylint-enabled = True

Available Options
-----------------

eggs
    Required: Yes

    Default: None

    Your project's list of eggs, those are going to be added in path location for `Jedi`_ and/or `Sublimelinter-Pylint`_ or `Anaconda`_.

    This situation may happen, you did create settings file manually with other configuration (those are not managed by ``collective.recipe.vscode``) and you want keep those settings intact.

python-path
    Required: No

    Default: ``collective.recipe.vscode`` will find current python executable path.

    The python executable path for current project, if you are using virtual environment then should be that python path. FYI: ${home} and ${project} variable should work.

flake8-enabled
    Required: No

    Default: if you have a existing `Visual Studio Code`_ project file(settings file) in project/buildout's root directory, ``collective.recipe.vscode`` will choose it as ``project-name``, other than project/buildout directory name will become as ``project-name``

flake8-path
    Required: No

    Default: if you have a existing `Visual Studio Code`_ project file(settings file) in project/buildout's root directory, ``collective.recipe.vscode`` will choose it as ``project-name``, other than project/buildout directory name will become as ``project-name``

flake8-args
    Required: No

    Default: if you have a existing `Visual Studio Code`_ project file(settings file) in project/buildout's root directory, ``collective.recipe.vscode`` will choose it as ``project-name``, other than project/buildout directory name will become as ``project-name``
    It is possible to `provide arguments (options) <http://flake8.pycqa.org/en/latest/user/options.html#full-listing-of-options-and-their-descriptions>`_ for ``flake8`` executable project specific.
    You have to follow a simple format to provide `multiple arguments aka <http://www.sublimelinter.com/en/stable/linter_settings.html#args>`_ flake8 options thanks to buildout for making our life easy. Format ``{option name}={option value(optional if the arg boolen type)}`` ``max-line-length=90``, it is remarkable that ``--`` prefix is not required, you can provide multiple arguments separated by ``space`` and/or ``newline``

    1. sublimelinter-flake8-args = max-line-length=90  --show-source

    2. sublimelinter-flake8-args = max-line-length=90  --show-source
                                output-file=path_to_file

pylint-enabled
    Required: No

    Default: if you have a existing `Visual Studio Code`_ project file(settings file) in project/buildout's root directory, ``collective.recipe.vscode`` will choose it as ``project-name``, other than project/buildout directory name will become as ``project-name``

pylint-path
    Required: No

    Default: if you have a existing `Visual Studio Code`_ project file(settings file) in project/buildout's root directory, ``collective.recipe.vscode`` will choose it as ``project-name``, other than project/buildout directory name will become as ``project-name``

pylint-args
    Required: No

    Default: if you have a existing `Visual Studio Code`_ project file(settings file) in project/buildout's root directory, ``collective.recipe.vscode`` will choose it as ``project-name``, other than project/buildout directory name will become as ``project-name``


pep8-enabled
    Required: No

    Default: if you have a existing `Visual Studio Code`_ project file(settings file) in project/buildout's root directory, ``collective.recipe.vscode`` will choose it as ``project-name``, other than project/buildout directory name will become as ``project-name``

pep8-path
    Required: No

    Default: if you have a existing `Visual Studio Code`_ project file(settings file) in project/buildout's root directory, ``collective.recipe.vscode`` will choose it as ``project-name``, other than project/buildout directory name will become as ``project-name``

pep8-args
    Required: No

    Default: if you have a existing `Visual Studio Code`_ project file(settings file) in project/buildout's root directory, ``collective.recipe.vscode`` will choose it as ``project-name``, other than project/buildout directory name will become as ``project-name``

jedi-enabled
    Required: No

    Default: False

    This option is related to enable/disable Sublime `Jedi`_

jedi-path
    Required: No

    Default: False

    Use the omelette as basis for jedi autocompletion and go-to-definition. See `collective.recipe.omelette <https://pypi.python.org/pypi/collective.recipe.omelette>`_

omelette-location
    Required: No

    Default: ${buildout:directory}/parts/omelette - the default omelette location.

    For use with jedi-use-omelette, but unless the omelette is installed at a custom location, the default should be fine.

autocomplete-use-omelete
    Required: No

    Default: False

    Whether `Sublimelinter`_'s features you want to use or not.

black-enabled
    Required: No

    Default: False

     If you want to use `Sublimelinter-Pylint`_ or not; ``sublimelinter-enabled`` option will be respected, means if parent option is set as disabled but you enable this option will not work.

black-path
    Required: No

    Default: ''

    You could provide buildout specific pylint executable. It is very flexible way to avoid using global pylint.
    Example of relative path usecase:
    i.) `${buildout:directory}/bin/pylint`
    ii.) `$project_path/bin/pylint`
    iii.) `./bin/pylint`
    iv.) `~/path/bin/pylint`


black-args
    Required: No

    Default: ''

    @see bellow at ``sublimelinter-flake8-args`` section for full detail.


ignore-develop
    Required: No

    Default: False

    If you don't want development eggs, should go for autocompletion.

ignores
    Required: No

    Default: ""

    If you want specific eggs should not go for autocompletion.

packages
    Required: No

    Default: ""

    Location of some python scripts or non standard modules (don't have setup file), you want to be in system path.

Links
=====

Code repository:

    https://github.com/nazrulworld/collective.recipe.vscode

Continuous Integration:

    https://travis-ci.org/nazrulworld/collective.recipe.vscode

Issue Tracker:

    https://github.com/nazrulworld/collective.recipe.vscode/issues



.. _`Visual Studio Code`: https://code.visualstudio.com/
.. _`Buildout`: http://www.buildout.org/en/latest/
.. _`Plone`: https://plone.org/
.. _`Flake8`: https://pypi.python.org/pypi/flake8
.. _`Python`: https://www.python.org/
.. _`Anaconda`: https://nazrul.me/2017/06/10/make-anaconda-powered-vscode-as-powerful-python-ide-for-full-stack-development/
