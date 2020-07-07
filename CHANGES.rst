Changelog
=========

0.1.6 (unreleased)
------------------

- Auto find all eggs for all recipes so eggs argument no longer required. [djay]
- Document how to automatically include the vscode recipe in all your buildouts [djay]


0.1.5 (2020-06-26)
------------------

- Issue#10 `don't ignore html files <https://github.com/nazrulworld/collective.recipe.vscode/issues/10>`_ [MrTango]


0.1.4 (2019-05-28)
------------------

- Issue#3 `Fixed  typo <https://github.com/nazrulworld/collective.recipe.vscode/issues/3>`_ [parruc]
- Issue#4 `Documented isort <https://github.com/nazrulworld/collective.recipe.vscode/issues/4>`_ [parruc]
- Issue#5 `Automatic .env file generation <https://github.com/nazrulworld/collective.recipe.vscode/issues/5>`_ [parruc]



0.1.3 (2019-03-12)
------------------

Bug fixes

- Issue#2 `Linter disabling simply not working <https://github.com/nazrulworld/collective.recipe.vscode/issues/2>`_


0.1.2 (2019-02-14)
------------------

New features

- default ``files.associations`` and ``files.exclude`` for python file now will be automatically included
  if those are not in existing ``settings.json``

Bug fixes

- Normally buildout removed generated file/directory first if exists, that's why previously ``settings.json`` file
  removed and ultimately existing settings were lost! [nazrulworld]


0.1.1 (2019-02-11)
------------------

Bug fixes

- Issue#1 `pep8 enabling configuration added even not mentioned in buildout <https://github.com/nazrulworld/collective.recipe.vscode/issues/1>`_

- Open existing settings file (mode was missing while opening file)


0.1.0 (2019-02-10)
------------------

- Initial release.
  [nazrulworld]
