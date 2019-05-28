.. image:: https://img.shields.io/pypi/status/collective.recipe.vscode.svg
    :target: https://pypi.org/project/collective.recipe.vscode/
    :alt: Package Status

.. image:: https://travis-ci.org/nazrulworld/collective.recipe.vscode.svg?branch=master
    :target: https://travis-ci.org/nazrulworld/collective.recipe.vscode
    :alt: Travis Build Status

.. image:: https://coveralls.io/repos/github/nazrulworld/collective.recipe.vscode/badge.svg?branch=master
    :target: https://coveralls.io/github/nazrulworld/collective.recipe.vscode?branch=master
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

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

.. contents::

Introduction
============

``collective.recipe.vscode`` is the buildout recipe for `Visual Studio Code`_ lover who wants python `autocomplete and intelliSense`_ features while developing python `Buildout`_ based project,
normally buildout eggs are not available in python path even if you provide virtualenv python path.
This tool will help not only adding eggs path as ``python extraPath`` but also you can manage per project basis vscode settings
for linter, autoformatting. 

A general question may arise that why we will use this tool, whether we can create `Visual Studio Code`_ project settings easily (we have better knowledge over `Visual Studio Code`_ configuration)?
Well i completely agree with you, but if you want to get benefited from  `Visual Studio Code`_ autocompletion feature (basically I am lover of autocompletion), you have to add all eggs links and it is hard to manage eggs links manually
if the size of project is big (think about any `Plone`_ powered project),
beside it is good practice allways use project specific linter path. For example my global ``flake8`` linter doesn't work
for my python3 project!

Installation
============

Install ``collective.recipe.vscode`` is simple enough, just need to create a section for ``vscode`` to your buildout.
Before using ``collective.recipe.vscode``, if you are going to use linter feature, make those are added in eggs section or globally installed. 

    Example Buildout::

        [buildout]
        parts += vscode

        [vscode]
        recipe = collective.recipe.vscode
        eggs = ${buildout:eggs}
        flake8-enabled = True
        flake8-path = ${buildout:directory}/bin/flake8
        black-enabled = True
        black-args = ----line-length 88

Available Options
-----------------

eggs
    Required: Yes

    Default: None

    Your project's list of eggs, those are going to be added as extra path for `autocomplete and intelliSense`_.

python-path
    Required: No

    Default: ``collective.recipe.vscode`` will find current python executable path.

    The python executable path for current project, if you are using virtual environment then should be that python path. FYI: ${home} and ${project} variable should work.

flake8-enabled

    Required: No

    Default: False

    Flag that indicates flake8 based linting. 

flake8-path
    Required: No

    Default: try to find flake8 executable path automatically.

flake8-args
    Required: No

    Default: ""
    

pylint-enabled

    Required: No
    Default: False

pylint-path
    Required: No

    Default: try to find pylint executable path automatically.

pylint-args
    Required: No

    Default:

pep8-enabled
    Required: No

    Default: False

pep8-path
    Required: No

    Default: try to find pep8 executable path automatically.

pep8-args
    Required: No

    Default: ""

jedi-enabled
    Required: No

    Default: False

jedi-path
    Required: No

    Default: ""

omelette-location
    Required: No

    Default: ${buildout:directory}/parts/omelette - the default omelette location.

autocomplete-use-omelette
    Required: No

    Default: False

black-enabled
    Required: No

    Default: False

black-path
    Required: No

    Default: try to find black executable path automatically.

    You could provide buildout specific black executable. It is very flexible way to avoid using global pylint.
    Example of relative path usecase:
    i.) `${buildout:directory}/bin/black`
    ii.) `$project_path/bin/black`
    iii.) `./bin/black`
    iv.) `~/path/bin/black`

black-args
    Required: No

    Default: ''

isort-enabled
    Required: No

    Default: False

    Flag that indicates isort is enabled. 

isort-path
    Required: No

    Default: try to find isort executable path automatically.

isort-args
    Required: No

    Default: ''

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

generate-envfile
    Required: No

    Default: false

    Generate .env file to add eggs to PYTHONPATH

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
.. _`autocomplete and intelliSense`: https://code.visualstudio.com/docs/languages/python#_autocomplete-and-intellisense
