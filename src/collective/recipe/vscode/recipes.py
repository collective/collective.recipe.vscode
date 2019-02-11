# _*_ coding: utf-8 _*_
""" """
from zc.buildout import UserError

import io
import json
import logging
import os
import re
import subprocess
import sys
import zc.recipe.egg


PY2 = sys.version_info[0] == 2

json_comment = re.compile(r"/\*.*?\*/", re.DOTALL | re.MULTILINE)
json_dump_params = {"sort_keys": True, "indent": 4, "separators": (",", ":")}
json_load_params = {}


def ensure_unicode(string):
    """" """
    if isinstance(string, bytes):
        return string.decode("utf-8", "strict")

    if PY2 and isinstance(string, basestring):  # noqa: F821
        if not isinstance(string, unicode):  # noqa: F821
            return string.decode("utf-8", "strict")


def find_executable_path(name):
    """ """
    try:
        path_ = subprocess.check_output(["which", name])
        return ensure_unicode(path_.strip())

    except subprocess.CalledProcessError:
        pass


with io.open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings_mappings.json"),
    "r",
    encoding="utf-8",
) as f:
    mappings = json.loads(f.read())


class Recipe:

    """zc.buildout recipe for sublimetext project settings:
    """

    def __init__(self, buildout, name, options):
        """ """
        self.buildout, self.name, self.options = buildout, name, options
        self.logger = logging.getLogger(self.name)

        self.egg = zc.recipe.egg.Egg(buildout, self.options["recipe"], options)

        self._set_defaults()

        self.settings_dir = os.path.join(options["project-root"], ".vscode")
        if not os.path.exists(self.settings_dir):
            os.makedirs(self.settings_dir)

        develop_eggs = []

        if self.options["ignore-develop"].lower() in ("yes", "true", "on", "1", "sure"):

            develop_eggs = os.listdir(buildout["buildout"]["develop-eggs-directory"])
            develop_eggs = [dev_egg[:-9] for dev_egg in develop_eggs]

        ignores = options.get("ignores", "").split()
        self.ignored_eggs = develop_eggs + ignores

        self.packages = [
            l.strip() for l in self.options["packages"].splitlines() if l and l.strip()
        ]

    def install(self):
        """Let's build vscode settings file:
        This is the method will be called by buildout it-self and this recipe
        will generate or/update vscode setting file (.vscode/settings.json) based
        on provided options.
        """
        eggs_locations = set()
        develop_eggs_locations = set()
        develop_eggs = os.listdir(self.buildout["buildout"]["develop-eggs-directory"])
        develop_eggs = [dev_egg[:-9] for dev_egg in develop_eggs]

        try:
            requirements, ws = self.egg.working_set()

            for dist in ws.by_key.values():

                project_name = dist.project_name
                if project_name not in self.ignored_eggs:
                    eggs_locations.add(dist.location)
                if project_name in develop_eggs:
                    develop_eggs_locations.add(dist.location)

            for package in self.packages:
                eggs_locations.add(package)

        except Exception as exc:
            raise UserError(str(exc))

        try:
            with io.open(
                os.path.join(self.settings_dir, "settings.json"), "r", encoding="utf-8"
            ) as fp:
                json_text = fp.read()
                existing_settings = json.loads(json_text)

        except ValueError as e:
            raise UserError(str(e))
        except IOError:
            existing_settings = dict()

        vscode_settings = self._prepare_settings(
            list(eggs_locations), list(develop_eggs_locations), existing_settings
        )

        self._write_project_file(vscode_settings, existing_settings)

        return os.path.join(self.settings_dir, "settings.json")

    update = install

    def normalize_options(self):
        """This method is simply doing tranformation of cfg string to python datatype.
        For example: yes(cfg) = True(python), 2(cfg) = 2(python)"""

        # Check for required and optional options
        options = self.options.copy()
        # flake8 check
        self._normalize_boolean("flake8-enabled", options)

        # pylint check
        self._normalize_boolean("pylint-enabled", options)

        # jedi check
        self._normalize_boolean("jedi-enabled", options)

        # black check
        self._normalize_boolean("black-enabled", options)

        # isort check
        self._normalize_boolean("isort-enabled", options)

        # mypy check
        self._normalize_boolean("mypy-enabled", options)

        # pep8 check: Issue#1
        self._normalize_boolean("pep8-enabled", options)

        # autocomplete
        options["autocomplete-use-omelete"] = self.options[
            "autocomplete-use-omelete"
        ].lower() in ("yes", "y", "true", "t", "on", "1", "sure")

        # Parse linter arguments
        if "pylint-args" in options:
            options["pylint-args"] = self._normalize_linter_args(options["pylint-args"])

        if "flake8-args" in options:
            options["flake8-args"] = self._normalize_linter_args(options["flake8-args"])

        if "black-args" in options:
            options["black-args"] = self._normalize_linter_args(options["black-args"])

        if "isort-args" in options:
            options["isort-args"] = self._normalize_linter_args(options["isort-args"])

        if "mypy-args" in options:
            options["mypy-args"] = self._normalize_linter_args(options["mypy-args"])

        if "pep8-args" in options:
            options["pep8-args"] = self._normalize_linter_args(options["pep8-args"])

        return options

    def _normalize_linter_args(self, args_lines):
        """ """
        args = list()
        for arg_line in args_lines.splitlines():
            if not arg_line or (arg_line and not arg_line.strip()):
                continue
            for arg in arg_line.split(" "):
                if not arg or (arg and not arg.strip()):
                    continue
                args.append(arg)

        return args

    def _normalize_boolean(self, option_name, options):
        """ """
        if option_name in options:
            options[option_name] = options[option_name].lower() in (
                "y",
                "yes",
                "true",
                "t",
                "on",
                "1",
                "sure",
            )

    def _set_defaults(self):
        """This is setting default values of all possible options"""

        self.options.setdefault("project-root", self.buildout["buildout"]["directory"])
        self.options.setdefault("python-path", str(sys.executable))
        if getattr(sys, "real_prefix", None):
            # Python running under virtualenv
            self.options.setdefault(
                "python-virtualenv",
                os.path.dirname(os.path.dirname(self.options["python-path"])),
            )

        self.options.setdefault(
            "omelette-location",
            os.path.join(self.buildout["buildout"]["parts-directory"], "omelette"),
        )

        self.options.setdefault("flake8-enabled", "False")
        self.options.setdefault("flake8-path", "")
        self.options.setdefault("flake8-args", "")
        self.options.setdefault("pylint-enabled", "False")
        self.options.setdefault("pylint-path", "")
        self.options.setdefault("pylint-args", "")
        self.options.setdefault("isort-enabled", "False")
        self.options.setdefault("isort-path", "")
        self.options.setdefault("isort-args", "")
        self.options.setdefault("mypy-enabled", "False")
        self.options.setdefault("mypy-path", "")
        self.options.setdefault("mypy-args", "")
        self.options.setdefault("pep8-enabled", "False")
        self.options.setdefault("pep8-path", "")
        self.options.setdefault("pep8-args", "")
        self.options.setdefault("jedi-enabled", "False")
        self.options.setdefault("jedi-path", "")
        self.options.setdefault("black-enabled", "False")
        self.options.setdefault("black-path", "")
        self.options.setdefault("black-args", "")
        self.options.setdefault("formatting-provider", "")
        self.options.setdefault("autocomplete-use-omelete", "False")
        self.options.setdefault("ignore-develop", "False")
        self.options.setdefault("ignores", "")
        self.options.setdefault("packages", "")

    def _prepare_settings(
        self, eggs_locations, develop_eggs_locations, existing_settings
    ):
        """ """
        options = self.normalize_options()
        settings = dict()
        # Base settings
        settings[mappings["python-path"]] = self._resolve_executable_path(
            options["python-path"]
        )

        settings[mappings["autocomplete-extrapaths"]] = eggs_locations

        if options["autocomplete-use-omelete"]:
            # Add the omelette and the development eggs to the jedi list.
            # This has the advantage of opening files at the omelette location,
            # keeping open files inside the project. Making it possible to
            # navigate to the location in the project, syncing the toolbar, and
            # inspecting the full module not just the individual file.
            settings[mappings["autocomplete-extrapaths"]] = [
                options["omelette-location"]
            ] + develop_eggs_locations

        # Look on Jedi
        if options["jedi-enabled"]:
            settings[mappings["jedi-enabled"]] = options["jedi-enabled"]

        if options["jedi-path"]:
            settings[mappings["jedi-path"]] = self._resolve_executable_path(
                options["jedi-path"]
            )

        # Setup flake8
        self._prepare_linter_settings(settings, "flake8", options)

        # Setup pylint
        self._prepare_linter_settings(settings, "pylint", options)

        # Setup pep8
        self._prepare_linter_settings(settings, "pep8", options)

        # Setup isort
        self._prepare_linter_settings(settings, "isort", options, allow_key_error=True)

        # Setup black
        if options["black-enabled"]:
            settings[mappings["formatting-provider"]] = "black"
            self._prepare_linter_settings(
                settings, "black", options, allow_key_error=True
            )
        else:
            if existing_settings.get(mappings["formatting-provider"], None) == "black":
                del existing_settings[mappings["formatting-provider"]]

        # Setup mypy
        self._prepare_linter_settings(settings, "mypy", options)

        return settings

    def _prepare_linter_settings(self, settings, name, options, allow_key_error=False):
        """All sublinter related settings are done by this method."""
        linter_enabled = "{name}-enabled".format(name=name)
        linter_path = "{name}-path".format(name=name)
        linter_args = "{name}-args".format(name=name)

        if not options[linter_enabled]:
            return

        try:
            settings[mappings[linter_enabled]] = options[linter_enabled]
        except KeyError:
            if not allow_key_error:
                raise

        # we care only if linter is active
        linter_executable = options.get(linter_path, "")
        if linter_executable in (None, ""):
            linter_executable = find_executable_path(name)

        if linter_executable:
            settings[mappings[linter_path]] = self._resolve_executable_path(
                linter_executable
            )

        if options[linter_args]:
            settings[mappings[linter_args]] = options[linter_args]

    def _write_project_file(self, settings, existing_settings):
        """Project File Writer:
        This method is actual doing writting project file to file system."""
        with io.open(
            os.path.join(self.settings_dir, "settings.json"), "w", encoding="utf-8"
        ) as fp:
            try:
                final_settings = existing_settings.copy()
                final_settings.update(settings)
                json_text = json.dumps(final_settings, indent=4)
                fp.write(ensure_unicode(json_text))

            except ValueError as exc:
                # catching any json error
                raise UserError(str(exc))

    def _resolve_executable_path(self, path_):
        """ """
        # Noramalized Path on demand
        if path_.startswith("~"):
            path_ = os.path.expanduser(path_)

        elif path_.startswith("./"):
            path_ = path_.replace(".", self.buildout["buildout"]["directory"])

        elif path_.startswith("${buildout:directory}"):
            path_ = path_.replace(
                "${buildout:directory}", self.buildout["buildout"]["directory"]
            )

        elif path_.startswith("$project_path/"):
            path_ = path_.replace(
                "$project_path", self.buildout["buildout"]["directory"]
            )

        return path_


def uninstall(name, options):
    """Nothing much need to do with uninstall, because this recipe is doing so
    much filesystem writting.
    Depends overwrite option, generated project file is removed."""

    logger = logging.getLogger(name)
    logger.info("uninstalling ...")
    # xxx: nothing for now, but may be removed what ever in options?
