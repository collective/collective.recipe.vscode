# _*_ coding: utf-8 _*_
from zc.buildout import rmtree
from zc.buildout import UserError
from zc.buildout.testing import Buildout
from zc.buildout.testing import mkdir
from zc.buildout.testing import read
from zc.buildout.testing import write

import json
import os
import tempfile
import unittest


JSON_TEMPLATE = os.path.join(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__))), "template.json"
)
TEST_DIR = os.path.abspath(os.path.dirname(__file__))


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
                "isort-enabled": "True",
                "isort-path": "${buildout:directory}/bin/isort",
                "generate-envfile": "True",
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
            generated_settings[mappings["flake8-path"]], self.location + "/bin/flake8"
        )

        # Isort executable should get automatically
        self.assertEqual(
            generated_settings[mappings["isort-path"]],
            self.location + "/bin/isort"
        )

        # Test existence and configuration of env file
        envfile_path = os.path.join(self.location, ".vscode", ".env")
        self.assertEqual(generated_settings["python.envFile"], envfile_path)
        self.assertTrue(os.path.isfile(envfile_path))

        # Test with custom location with package
        buildout["vscode"].update({
            "packages": "/fake/path",
            "project-root": os.path.join(tempfile.gettempdir(), "hshdshgdrts"),
        })

        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        recipe.install()

        generated_settings = json.loads(
            read(
                os.path.join(
                    buildout["vscode"]["project-root"], ".vscode", "settings.json"
                )
            )
        )

        # Now should three (two+one) links
        self.assertEqual(
            3, len(generated_settings[mappings["autocomplete-extrapaths"]])
        )

        # restore
        rmtree.rmtree(buildout["vscode"]["project-root"])
        del buildout["vscode"]["project-root"]
        del buildout["vscode"]["packages"]

        # Test ignores
        buildout["buildout"].update({"develop": "."})
        buildout["vscode"].update({"ignores": "zc.buildout", "ignore-develop": "True"})
        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        recipe.install()

        generated_settings = json.loads(
            read(os.path.join(self.location, ".vscode", "settings.json"))
        )

        # should be two, zc.buildout is ignored
        self.assertEqual(
            2, len(generated_settings[mappings["autocomplete-extrapaths"]])
        )

        # Failed Test: existing project file with invalid json
        write(
            os.path.join(self.location, ".vscode"), "settings.json", """I am invalid"""
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
                "Code should not come here, as should raised execption "
                "because of invalid eggs"
            )
        except UserError:
            pass

    def test__prepare_settings(self):
        """ """
        from ..recipes import mappings
        from ..recipes import Recipe

        buildout = self.buildout
        recipe_options = self.recipe_options.copy()

        buildout["vscode"] = recipe_options
        recipe = Recipe(buildout, "vscode", buildout["vscode"])

        test_eggs_locations = ["/tmp/eggs/egg1.egg", "/tmp/eggs/egg2.egg"]

        develop_eggs_locations = []

        vsc_settings = recipe._prepare_settings(
            test_eggs_locations, develop_eggs_locations, {}
        )
        self.assertNotIn(mappings["isort-path"], vsc_settings)
        self.assertNotIn(mappings["black-path"], vsc_settings)
        self.assertNotIn(mappings["flake8-path"], vsc_settings)
        self.assertNotIn(mappings["pylint-path"], vsc_settings)

        recipe_options["jedi-enabled"] = "True"
        recipe_options["pylint-enabled"] = "True"
        recipe_options["flake8-enabled"] = "True"
        recipe_options["flake8-path"] = "/fake/path/flake8"
        recipe_options["black-enabled"] = "True"
        recipe_options["black-path"] = "/tmp/bin/black"
        recipe_options["black-args"] = "--line-length\n88"

        buildout["vscode"].update(recipe_options)

        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        vsc_settings = recipe._prepare_settings(
            test_eggs_locations, develop_eggs_locations, {}
        )

        # Test Anaconda Settings are avialable
        self.assertIn(mappings["flake8-path"], vsc_settings)
        # make sure formatter provider is black
        self.assertEqual(vsc_settings[mappings["formatting-provider"]], "black")
        self.assertEqual(vsc_settings[mappings["black-path"]], "/tmp/bin/black")
        self.assertEqual(vsc_settings[mappings["black-args"]], ["--line-length", "88"])

        # Let's test path, args are not ignored
        buildout["vscode"]["black-enabled"] = "False"

        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        vsc_settings2 = recipe._prepare_settings(
            test_eggs_locations, develop_eggs_locations, {}
        )
        self.assertNotIn(mappings["formatting-provider"], vsc_settings2)
        self.assertIn(mappings["black-path"], vsc_settings2)
        self.assertIn(mappings["black-args"], vsc_settings2)

        # test with existing settings
        buildout["vscode"]["black-path"] = ""
        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        vsc_settings3 = recipe._prepare_settings(
            test_eggs_locations, develop_eggs_locations, vsc_settings
        )

        # only formatting-provider should removed, others should be kept
        self.assertNotIn(mappings["formatting-provider"], vsc_settings)
        self.assertIn(mappings["black-path"], vsc_settings)
        self.assertNotIn(mappings["black-path"], vsc_settings3)

    def test__write_project_file(self):
        """ """
        from ..recipes import mappings
        from ..recipes import Recipe

        buildout = self.buildout
        recipe_options = self.recipe_options.copy()
        buildout["vscode"] = recipe_options

        test_eggs_locations = ["/tmp/eggs/egg1.egg", "/tmp/eggs/egg2.egg"]
        develop_eggs_locations = []

        recipe_options["jedi-enabled"] = "True"
        recipe_options["pylint-enabled"] = "True"
        recipe_options["flake8-enabled"] = "True"
        recipe_options["flake8-path"] = "/fake/path/flake8"
        recipe_options["black-enabled"] = "True"
        recipe_options["black-path"] = "/tmp/bin/black"
        recipe_options["black-args"] = "--line-length\n88"

        buildout["vscode"].update(recipe_options)

        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        recipe._set_defaults()

        vsc_settings = recipe._prepare_settings(
            test_eggs_locations, develop_eggs_locations, {}
        )
        recipe._write_project_file(vsc_settings, {})
        # By default no overwrite configuration, means existing configuration should be
        # available
        generated_settings = json.loads(
            read(os.path.join(self.location, ".vscode", "settings.json"))
        )

        # Make sure other value kept intact, because that option is not handled by
        # this recipe.
        self.assertEqual(
            generated_settings[mappings["flake8-path"]], "/fake/path/flake8"
        )
        # Test:: default folders option is added, because existing file don't have this
        self.assertEqual(
            generated_settings[mappings["black-args"]], ["--line-length", "88"]
        )

        buildout["vscode"].update(
            {"black-enabled": "False", "flake8-path": "/new/path/flake8"}
        )

        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        vsc_settings2 = recipe._prepare_settings(
            test_eggs_locations, develop_eggs_locations, vsc_settings
        )

        recipe._write_project_file(vsc_settings2, vsc_settings)

        generated_settings = json.loads(
            read(os.path.join(self.location, ".vscode", "settings.json"))
        )
        # there should not any formatting provider
        self.assertNotIn(mappings["formatting-provider"], generated_settings)
        # Black path still exists
        self.assertIn(mappings["black-path"], generated_settings)
        # Test: overwrite works!
        self.assertEqual(
            generated_settings[mappings["flake8-path"]], "/new/path/flake8"
        )

    def test_pyfile_defaults_settings(self):
        """ """
        from ..recipes import python_file_defaults
        from ..recipes import Recipe

        recipe_options = self.recipe_options.copy()
        self.buildout["vscode"] = recipe_options

        recipe = Recipe(self.buildout, "vscode", self.buildout["vscode"])
        recipe._set_defaults()
        recipe.install()

        generated_settings = json.loads(
            read(os.path.join(self.location, ".vscode", "settings.json"))
        )
        for key in python_file_defaults:
            self.assertIn(key, generated_settings)

        with open(os.path.join(self.location, ".vscode", "settings.json"), "w") as fp:
            json.dump({"files.associations": {}, "files.exclude": []}, fp)

        recipe = Recipe(self.buildout, "vscode", self.buildout["vscode"])
        recipe._set_defaults()
        recipe.install()

        generated_settings = json.loads(
            read(os.path.join(self.location, ".vscode", "settings.json"))
        )
        for key in python_file_defaults:
            self.assertNotEqual(python_file_defaults[key], generated_settings[key])

    def test_issue2(self):
        """Issue:2 Linter disabling simply not working"""
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
                "isort-enabled": "True",
                "pylint-enabled": "False",
            }
        )
        buildout["vscode"] = recipe_options
        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        recipe.install()

        generated_settings = json.loads(
            read(os.path.join(self.location, ".vscode", "settings.json"))
        )
        # should have an entry of pylint
        self.assertIn(mappings["pylint-enabled"], generated_settings)
        self.assertFalse(generated_settings[mappings["pylint-enabled"]])

        buildout["vscode"]["pylint-enabled"] = "True"
        recipe = Recipe(buildout, "vscode", buildout["vscode"])
        recipe.install()

        generated_settings = json.loads(
            read(os.path.join(self.location, ".vscode", "settings.json"))
        )
        # should enable now
        self.assertTrue(generated_settings[mappings["pylint-enabled"]])

        del recipe_options["black-enabled"]
        del recipe_options["black-path"]
        del recipe_options["flake8-enabled"]
        recipe_options["isort-enabled"] = "False"

        buildout["vscode2"] = recipe_options

        recipe = Recipe(buildout, "vscode2", buildout["vscode2"])
        recipe.install()

        generated_settings = json.loads(
            read(os.path.join(self.location, ".vscode", "settings.json"))
        )
        # flake8 enable flag should not exists

        self.assertNotIn(mappings["flake8-enabled"], generated_settings)
        # same for black
        self.assertNotIn(mappings["formatting-provider"], generated_settings)

        # still flake8 path should exists
        self.assertIn(mappings["flake8-path"], generated_settings)
        # But not blackpath
        self.assertNotIn(mappings["black-path"], generated_settings)

        # there should no auto isort executable
        self.assertNotIn(mappings["isort-path"], generated_settings)

    def tearDown(self):
        os.chdir(self.here)
        rmtree.rmtree(self.location)


class TestRecipeUninstall(unittest.TestCase):
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

    def test_uninstall(self):
        """ """
        from ..recipes import Recipe
        from ..recipes import uninstall

        recipe_options = self.recipe_options.copy()
        self.buildout["vscode"] = recipe_options

        recipe = Recipe(self.buildout, "vscode", self.buildout["vscode"])
        recipe._set_defaults()
        recipe.install()

        uninstall(recipe.name, recipe.options)

    def tearDown(self):
        os.chdir(self.here)
        rmtree.rmtree(self.location)
