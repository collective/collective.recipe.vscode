plone.recipe.sublimetext test suite
===================================

Install sublimetext recipe with autocomplete path for eggs, some packages::
    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop =
    ...     %(test_dir)s/develop/sublimtexttest_pkg1
    ... eggs =
    ...     sublimtexttest_pkg1
    ...     zc.recipe.egg
    ...     zc.buildout
    ... parts = sublimetext
    ...
    ... [sublimetext]
    ... recipe = plone.recipe.sublimetext
    ... packages = %(test_dir)s/Products
    ... project-name = plone-recipe-sublime
    ... ignore-develop = False
    ... eggs = ${buildout:eggs}
    ... overwrite = False
    ... jedi-enabled = True
    ... sublimelinter-enabled = True
    ... sublimelinter-pylint-enabled = True
    ... sublimelinter-flake8-enabled = True
    ... """ % globals())
    >>> output_lower = system(buildout + ' -c buildout.cfg').lower()
    >>> 'installing sublimetext.' in output_lower
    True
    >>> 'tests/develop/sublimtexttest_pkg1' in output_lower
    True
    >>> ls(sample_buildout)
    -  .installed.cfg
    d  bin
    -  buildout.cfg
    d  develop-eggs
    d  eggs
    d  parts
    -  plone-recipe-sublime.sublime-project
    <BLANKLINE>
    >>> import json
    >>> ST3_settings = json.loads(read(sample_buildout, 'plone-recipe-sublime.sublime-project'))
    >>> len(ST3_settings['settings']['python_package_paths']) == 5
    True
    >>> 'SublimeLinter.linters.pylint.disable' in ST3_settings['settings'].keys()
    True
    >>> ST3_settings['settings']['SublimeLinter.linters.pylint.disable']
    False

SublimeText congiguration with all default options::
    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop =
    ...     %(test_dir)s/develop/sublimtexttest_pkg1
    ... eggs =
    ...     sublimtexttest_pkg1
    ...     zc.recipe.egg
    ... parts = sublimetext
    ...
    ... [sublimetext]
    ... recipe = plone.recipe.sublimetext
    ... eggs = ${buildout:eggs}
    ... """ % globals())
    >>> output = system(buildout + ' -c buildout.cfg').lower()
    >>> ST3_settings = json.loads(read(sample_buildout, 'plone-recipe-sublime.sublime-project'))
    >>> s_linters = [l for l in ST3_settings['settings'].keys() if l.startswith('SublimeLinter')]
    >>> len(s_linters) == 0
    True
    >>> 'python_package_paths' not in ST3_settings['settings'].keys()
    True
    >>> ST3_settings['folders'][0]['path'] == '.'
    True

SublimeText congiguration test with custom location, custom flake8 exacutable and with existings settings.
Test merged works, existing settings kept intact::

    >>> import os
    >>> import tempfile
    >>> custom_location = tempfile.mkdtemp('prs')
    >>> GLOBAL = {'custom_location': custom_location}
    >>> GLOBAL.update(globals())
    >>> write(custom_location, 'plone-recipe-sublime.sublime-project',
    ... """
    ... {
    ...     "folders": [{"path": "%(custom_location)s"}],
    ...     "settings": {
    ...         "SublimeLinter.linters.flake8.disable": true,
    ...         "SublimeLinter.linters.flake8.args": ["--max-complexity=10"]
    ...      }
    ... }
    ... """ % {'custom_location': custom_location})
    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop =
    ...     %(test_dir)s/develop/sublimtexttest_pkg1
    ... eggs =
    ...     sublimtexttest_pkg1
    ...     zc.recipe.egg
    ... parts = sublimetext
    ...
    ... [sublimetext]
    ... recipe = plone.recipe.sublimetext
    ... eggs = ${buildout:eggs}
    ... project-name = plone-recipe-sublime
    ... location = %(custom_location)s
    ... sublimelinter-enabled = True
    ... sublimelinter-flake8-enabled = True
    ... sublimelinter-flake8-executable = ${buildout:directory}/bin/flake8
    ... sublimelinter-pylint-enabled = True
    ... sublimelinter-pylint-executable = ${buildout:directory}/bin/pylint
    ... """ % GLOBAL)
    >>> output = system(buildout + ' -c buildout.cfg').lower()
    >>> ST3_settings = json.loads(read(custom_location, 'plone-recipe-sublime.sublime-project'))
    >>> import os
    >>> ST3_settings['settings']['SublimeLinter.linters.flake8.executable'] == os.path.join(sample_buildout, 'bin', 'flake8')
    True
    >>> ST3_settings['settings']['SublimeLinter.linters.pylint.executable'] == os.path.join(sample_buildout, 'bin', 'pylint')
    True
    >>> ST3_settings['settings']['SublimeLinter.linters.flake8.disable']
    False
    >>> ST3_settings['settings']['SublimeLinter.linters.flake8.args'] == ['--max-complexity=10']
    True
    >>> ST3_settings['folders'][0]['path'] == custom_location
    True
    >>>
    >>> import shutil
    >>> shutil.rmtree(custom_location)

Anaconda Settings Tests with default options::

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop =
    ...     %(test_dir)s/develop/sublimtexttest_pkg1
    ... eggs =
    ...     sublimtexttest_pkg1
    ...     zc.recipe.egg
    ...     zc.buildout
    ... parts = sublimetext
    ...
    ... [sublimetext]
    ... recipe = plone.recipe.sublimetext
    ... packages = %(test_dir)s/Products
    ... project-name = plone-recipe-sublime
    ... eggs = ${buildout:eggs}
    ... anaconda-enabled = True
    ... anaconda-pep8-ignores =
    ...     N802
    ...     W291
    ... """ % globals())
    >>> output_lower = system(buildout + ' -c buildout.cfg').lower()
    >>> ST3_settings = json.loads(read(sample_buildout, 'plone-recipe-sublime.sublime-project'))
    >>> len(ST3_settings['settings']['extra_paths']) == 5
    True
    >>> 'build_systems' in ST3_settings.keys()
    True
    >>> len(ST3_settings['settings']['pep8_ignore']) == 2
    True
    >>> ST3_settings['settings']['anaconda_linting']
    True
    >>> 'SublimeLinter' not in ST3_settings.keys()
    True
    >>> 'python_package_paths' not in ST3_settings['settings'].keys()
    True


Sublimelinter Linter Settings Tests with args::

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop =
    ...     %(test_dir)s/develop/sublimtexttest_pkg1
    ... eggs =
    ...     sublimtexttest_pkg1
    ...     zc.recipe.egg
    ...     zc.buildout
    ... parts = sublimetext
    ...
    ... [sublimetext]
    ... recipe = plone.recipe.sublimetext
    ... packages = %(test_dir)s/Products
    ... project-name = plone-recipe-sublime
    ... eggs = ${buildout:eggs}
    ... sublimelinter-enabled = 1
    ... sublimelinter-pylint-enabled = True
    ... sublimelinter-pylint-args =  disable=all
    ... sublimelinter-flake8-enabled = 1
    ... sublimelinter-flake8-args =  max-complexity=10  max-line-length=119
    ...     exclude=docs,*.egg.,omelette
    ... """ % globals())

    >>> output_lower = system(buildout + ' -c buildout.cfg').lower()
    >>> ST3_settings = json.loads(read(sample_buildout, 'plone-recipe-sublime.sublime-project'))
    >>> len(ST3_settings['settings']['SublimeLinter.linters.flake8.args']) == 3
    True
    >>> ST3_settings['settings']['SublimeLinter.linters.flake8.args'] == \
    ...  ['--max-complexity=10', '--max-line-length=119', '--exclude=docs,*.egg.,omelette']
    True
    >>> len(ST3_settings['settings']['SublimeLinter.linters.pylint.args']) == 1
    True