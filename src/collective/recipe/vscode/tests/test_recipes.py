# _*_ coding: utf-8 _*_
from zc.buildout import rmtree
from zc.buildout import UserError
from zc.buildout.testing import Buildout
from zc.buildout.testing import mkdir
from zc.buildout.testing import read
from zc.buildout.testing import write

import json
import os
import sys
import tempfile
import unittest


JSON_TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__))), "template.json"
)
TEST_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    str_ = basestring
except NameError:
    str_ = str


class TestRecipe(unittest.TestCase):
    """ """

    def setUp(self):

        self.here = os.getcwd()

        self.location = tempfile.mkdtemp(prefix="collective.recipe.vscode")
        mkdir(self.location, "develop-eggs")
        os.chdir(self.location)

        self.buildout = Buildout()
        # Set eggs
        self.buildout["buildout"]["directory"] = self.location

        self.recipe_options = dict(
            recipe="collective.recipe.vscode", eggs="zc.recipe.egg\nzc.buildout"
        )

    def test_install(self):
        """"""
        from ..recipes import Recipe
        from ..recipes import mappings

        buildout = self.buildout
        recipe_options = self.recipe_options.copy()
        recipe_options.update(
            {
                "black-enabled": "1",
                "black-args": "--line-length 88",
                "black-path": "$project_path/bin/black",
                "flake8-enabled": "True",
                "flake8-args": "--max-line-length 88",
                "flake8-path": "${buildout:directory}/bin/flake8",
            }
        )
        buildout["vscode"] = recipe_options
        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        recipe.install()

        generated_settings = json.loads(
            read(os.path.join(self.location, ".vscode", "settings.json"))
        )
        # should be two, zc,recipe.egg, python site-package path
        self.assertEqual(
            2, len(generated_settings[mappings["autocomplete-extrapaths"]])
        )
        self.assertEqual(
            generated_settings[mappings["flake8-path"]],
            self.location + '/bin/flake8'
            )
        
        # Isort executable should get automatically
        self.assertEqual(
            generated_settings[mappings["isort-path"]],
            self.location + '/bin/isort'
            )

        # Test with custom location with package
        buildout["vscode"].update(
            {
                "packages": "/fake/path",
                "location": os.path.join(tempfile.gettempdir(), "hshdshgdrts"),
            }
        )

        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        recipe.install()

        generated_settings = json.loads(
            read(
                os.path.join(
                    buildout["vscode"]["location"],
                    recipe_options["project-name"] + ".sublime-project",
                )
            )
        )

        # Now should four links
        self.assertEqual(4, len(generated_settings["settings"]["python_package_paths"]))

        # Make sure settings file is created at custom location
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    buildout["vscode"]["location"],
                    buildout["vscode"]["project-name"] + ".sublime-project",
                )
            )
        )

        # restore
        rmtree.rmtree(buildout["vscode"]["location"])
        del buildout["vscode"]["location"]
        del buildout["vscode"]["packages"]

        # Test ignores
        buildout["buildout"].update({"develop": "."})
        buildout["vscode"].update({"ignores": "zc.buildout", "ignore-develop": "True"})
        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        recipe.install()

        generated_settings = json.loads(
            read(
                os.path.join(
                    self.location, recipe_options["project-name"] + ".sublime-project"
                )
            )
        )

        # should be two, zc.buildout is ignored
        self.assertEqual(2, len(generated_settings["settings"]["python_package_paths"]))

        # Failed Test: existing project file with invalid json
        write(
            self.location,
            recipe_options["project-name"] + ".sublime-project",
            """I am invalid""",
        )
        try:
            recipe.update()
            raise AssertionError(
                "Code should not come here, as invalid json inside existing project"
                "file! ValueError raised by UserError"
            )
        except UserError:
            pass

        # Failed Test: exception rasied by zc.recipe.Egg
        recipe.options.update(
            {
                # Invalid Egg
                "eggs": "\\"
            }
        )
        try:
            recipe.install()
            raise AssertionError(
                "Code should not come here, as should raised execption because of invalied eggs"
            )
        except UserError:
            pass

    def __test__set_defaults(self):
        """ """
        from ..recipes import Recipe

        buildout = self.buildout
        recipe_options = self.recipe_options.copy()

        del recipe_options["project-name"]

        buildout["vscode"] = recipe_options
        recipe = Recipe(buildout, "vscode", buildout["vscode"])

        recipe._set_defaults()
        # Test: default project name should be buildout directory name
        self.assertEqual(recipe.options["project-name"], self.location.split("/")[-1])

        # Test: if any ``sublime-project`` suffix file is available inside buildout directory
        # that should be picked as default project file name
        _project_file = "human_project"
        write(self.location, _project_file + ".sublime-project", "[]")
        # clear previously assaigned default
        del buildout["vscode"]["project-name"]

        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        recipe._set_defaults()

        self.assertEqual(recipe.options["project-name"], _project_file)

    def __test__prepare_settings(self):
        """ """
        from ..recipes import Recipe

        buildout = self.buildout
        recipe_options = self.recipe_options.copy()

        buildout["vscode"] = recipe_options
        recipe = Recipe(buildout, "vscode", buildout["vscode"])

        test_eggs_locations = ["/tmp/eggs/egg1.egg", "/tmp/eggs/egg2.egg"]

        develop_eggs_locations = []

        st3_settings = recipe._prepare_settings(
            test_eggs_locations, develop_eggs_locations
        )

        # By Default Sublimelinter is not enabled
        # No linter setting should be available
        s_linters = [
            l for l in st3_settings["settings"].keys() if l.startswith("SublimeLinter")
        ]
        self.assertEqual(len(s_linters), 0)

        # Anaconda is not enabled as well
        self.assertNotIn("build_systems", st3_settings)
        self.assertNotIn("extra_paths", st3_settings["settings"])

        recipe_options["jedi-enabled"] = "True"
        recipe_options["sublimelinter-enabled"] = "True"
        recipe_options["sublimelinter-pylint-enabled"] = "True"
        recipe_options["sublimelinter-flake8-enabled"] = "True"
        recipe_options["sublimelinter-flake8-executable"] = "/fake/path/flake8"
        recipe_options["anaconda-enabled"] = "True"
        recipe_options["anaconda-pylint-enabled"] = "True"
        recipe_options["anaconda-pep8-ignores"] = "N802\nW291"

        buildout["vscode"].update(recipe_options)

        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        st3_settings = recipe._prepare_settings(
            test_eggs_locations, develop_eggs_locations
        )

        s_linters = [
            l for l in st3_settings["settings"].keys() if l.startswith("SublimeLinter")
        ]
        # two extra option with SublimeLinter.linters.{linter}.python
        self.assertEqual(len(s_linters), 6)

        self.assertEqual(
            test_eggs_locations, st3_settings["settings"]["python_package_paths"]
        )
        self.assertFalse(
            st3_settings["settings"]["SublimeLinter.linters.pylint.disable"]
        )

        # Test Anaconda Settings are avialable
        self.assertIn("build_systems", st3_settings)
        self.assertTrue(st3_settings["settings"]["anaconda_linting"])
        self.assertTrue(st3_settings["settings"]["use_pylint"])
        self.assertEqual(len(st3_settings["settings"]["pep8_ignore"]), 2)
        self.assertTrue(st3_settings["settings"]["validate_imports"])

        # Test Parent `sublimelinter-enabled` is respected
        # We all children options of sublimelinter are enabled.
        del buildout["vscode"]["sublimelinter-enabled"]

        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        st3_settings = recipe._prepare_settings(
            test_eggs_locations, develop_eggs_locations
        )
        self.assertNotIn("SublimeLinter", st3_settings)

    def __test__write_project_file(self):
        """ """
        from ..recipes import Recipe
        from ..recipes import default_st3_folders_settings

        buildout = self.buildout
        recipe_options = self.recipe_options.copy()
        del recipe_options["overwrite"]
        recipe_options.update(
            {"sublimelinter-enabled": "True", "sublimelinter-flake8-enabled": "True"}
        )

        _project_file = "human_project.sublime-project"

        write(
            self.location,
            _project_file,
            """{
                /*
                 This is comment.
                */
                "tests": {
                    "hello": 1
                },
                "settings": {
                    "SublimeLinter.linters.flake8.disable": true,
                    "SublimeLinter.linters.flake8.args": ["--max-complexity=10"]
                }

            }""",
        )

        buildout["vscode"] = recipe_options

        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        recipe._set_defaults()

        test_eggs_locations = ["/tmp/eggs/egg1.egg", "/tmp/eggs/egg2.egg"]

        develop_eggs_locations = []

        st3_settings = recipe._prepare_settings(
            test_eggs_locations, develop_eggs_locations
        )
        recipe._write_project_file(
            os.path.join(self.location, _project_file), st3_settings, False
        )
        # By default no overwrite configuration, means existing configuration should be
        # available
        generated_settings = json.loads(
            read(os.path.join(self.location, _project_file))
        )

        # Test:: merged works with new and existing

        # Make sure value changed from buildout
        self.assertFalse(
            generated_settings["settings"]["SublimeLinter.linters.flake8.disable"]
        )
        # Make sure other value kept intact, because that option is not handled by this recipe
        self.assertEqual(
            generated_settings["settings"]["SublimeLinter.linters.flake8.args"],
            ["--max-complexity=10"],
        )
        # Test:: default folders option is added, because existing file don't have this
        self.assertEqual(generated_settings["folders"], default_st3_folders_settings)

        # Test: existing configuration is kept intact
        self.assertEqual(generated_settings["tests"]["hello"], 1)

        buildout["vscode"].update(
            {
                "sublimelinter-enabled": "True",
                "sublimelinter-flake8-enabled": "False",
                "sublimelinter-pylint-enabled": "True",
                "jedi-enabled": "True",
            }
        )

        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        st3_settings = recipe._prepare_settings(
            test_eggs_locations, develop_eggs_locations
        )

        recipe._write_project_file(
            os.path.join(self.location, _project_file), st3_settings, False
        )

        generated_settings = json.loads(
            read(os.path.join(self.location, _project_file))
        )

        self.assertEqual(
            test_eggs_locations, generated_settings["settings"]["python_package_paths"]
        )
        # Test paths are added for `pylint`
        self.assertEqual(
            2, len(generated_settings["settings"]["SublimeLinter.linters.pylint.paths"])
        )

        # Test: overwrite works!
        recipe._write_project_file(
            os.path.join(self.location, _project_file), st3_settings, True
        )
        generated_settings = json.loads(
            read(os.path.join(self.location, _project_file))
        )
        self.assertNotIn("tests", generated_settings)
        # Test:: default folders setting
        # As completly overwrite file, so there is no folders option, so should have default
        self.assertEqual(generated_settings["folders"], default_st3_folders_settings)

        # Test: Anaconda Settings is working

        buildout["vscode"].update(
            {"anaconda-enabled": "True", "anaconda-pep8-ignores": "N802 W291"}
        )

        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        st3_settings = recipe._prepare_settings(
            test_eggs_locations, develop_eggs_locations
        )

        recipe._write_project_file(
            os.path.join(self.location, _project_file), st3_settings, True
        )

        generated_settings = json.loads(
            read(os.path.join(self.location, _project_file))
        )
        self.assertIn("build_systems", generated_settings)
        self.assertEqual(
            generated_settings["build_systems"][0]["name"],
            "PRS:: Anaconda Python Builder",
        )
        # By default pylint disabled
        self.assertFalse(generated_settings["settings"]["use_pylint"])
        # Should have two eggs paths in `extra_paths`
        self.assertEqual(len(generated_settings["settings"]["extra_paths"]), 2)

    def tearDown(self):
        os.chdir(self.here)
        rmtree.rmtree(self.location)


class TestRecipeUninstall(unittest.TestCase):
    """ """

    def setUp(self):

        self.here = os.getcwd()

        self.location = tempfile.mkdtemp(prefix="plone.recipe.vscode")
        os.chdir(self.location)

        self.buildout = Buildout()
        # Set eggs
        self.buildout["buildout"]["directory"] = self.location

        self.recipe_options = dict(recipe="plone.recipe.vscode", overwrite="False")

    def __test_uninstall(self):
        """ """
        from ..recipes import Recipe
        from ..recipes import uninstall

        recipe_options = self.recipe_options.copy()
        self.buildout["vscode"] = recipe_options

        recipe = Recipe(self.buildout, "vscode", self.buildout["vscode"])
        recipe._set_defaults()

        # Test: in case of overwrite false, project file should not be removed
        filename = recipe.options["project-name"] + ".sublime-project"
        write(self.location, filename, '{"hello": "T20"}')
        uninstall(recipe.name, recipe.options)

        # should be exists
        self.assertTrue(os.path.exists(filename))

        # update to overwrite True
        recipe.options.update({"overwrite": "True"})
        uninstall(recipe.name, recipe.options)

        # now should be removed
        self.assertFalse(os.path.exists(filename))

    def tearDown(self):
        os.chdir(self.here)
        rmtree.rmtree(self.location)
