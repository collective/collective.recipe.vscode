Example Usage
=============

Install  vscode recipe with stndard settings::

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop =
    ...     %(test_dir)s/develop/vscodetest_pkg1
    ... eggs =
    ...     vscodetest_pkg1
    ...     zc.recipe.egg
    ...     zc.buildout
    ... parts = vscode
    ...
    ... [vscode]
    ... recipe = collective.recipe.vscode
    ... packages = %(test_dir)s/Products
    ... ignore-develop = False
    ... eggs = ${buildout:eggs}
    ... flake8-enabled = True
    ... flake8-path = ${buildout:directory}/bin/flake8
    ... black-enabled = True
    ... black-path = $project_path/bin/black
    ... black-args = --line-length 88 
    ...              --skip-string-normalization
    ... """ % globals())
    >>> output_lower = system(buildout + ' -c buildout.cfg').lower()
    >>> "installing vscode." in output_lower
    True
    >>> 'tests/develop/vscodetest_pkg1' in output_lower
    True
    >>> ls(sample_buildout)
    -  .installed.cfg
    d  .vscode
    d  bin
    -  buildout.cfg
    d  develop-eggs
    d  eggs
    d  parts
    <BLANKLINE>
    >>> import json
    >>> import os
    >>> from collective.recipe.vscode.recipes import mappings
    >>> settings_dir = os.path.join(sample_buildout, ".vscode")
    >>> vsc_settings = json.loads(read(settings_dir, 'settings.json'))
    >>> len(vsc_settings[mappings['autocomplete-extrapaths']]) == 4
    True
    >>> mappings['flake8-enabled'] in vsc_settings
    True
    >>> vsc_settings[mappings['formatting-provider']] == "black"
    True

VS Code settings with all default options::

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... develop =
    ...     %(test_dir)s/develop/vscodetest_pkg1
    ... eggs =
    ...     vscodetest_pkg1
    ...     zc.recipe.egg
    ... parts = vscode
    ...
    ... [vscode]
    ... recipe = collective.recipe.vscode
    ... eggs = ${buildout:eggs}
    ... """ % globals())
    >>> output = system(buildout + ' -c buildout.cfg').lower()
    >>> vsc_settings = json.loads(read(settings_dir, 'settings.json'))
    >>> mappings['flake8-path'] not in vsc_settings
    True
    >>> len(vsc_settings[mappings['autocomplete-extrapaths']]) == 3
    True