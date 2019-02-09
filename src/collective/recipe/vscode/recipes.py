# _*_ coding: utf-8 _*_
""" """
from zc.buildout import UserError

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

if PY2:
    json_dump_params["encoding"] = "utf-8"
    json_load_params["encoding"] = "utf-8"


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


with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings_mappings.json"),
    "r",
) as f:
    mappings = json.load(f, **json_load_params)


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
            with open(os.path.join(self.settings_dir, "settings.json")) as fp:
                existing_settings = json.load(fp)

        except ValueError as e:
            raise UserError(str(e))
        except IOError:
            existing_settings = dict()

        vscode_settings = self._prepare_settings(
            list(eggs_locations), list(develop_eggs_locations), existing_settings
        )

        self._write_project_file(vscode_settings, existing_settings)

    update = install

    def normalize_options(self):
        """This method is simply doing tranformation of cfg string to python datatype.
        For example: yes(cfg) = True(python), 2(cfg) = 2(python)"""

        # Check for required and optional options
        options = self.options.copy()

        if "flake8-enabled" in options:
            options["flake8-enabled"] = options["flake8-enabled"].lower() in (
                "yes",
                "true",
                "on",
                "1",
                "sure",
            )

        if "pylint-enabled" in options:
            options["pylint-enabled"] = options["jedi-enabled"].lower() in (
                "yes",
                "true",
                "on",
                "1",
                "sure",
            )

        if "jedi-enabled" in options:
            options["jedi-enabled"] = options["jedi-enabled"].lower() in (
                "yes",
                "true",
                "on",
                "1",
                "sure",
            )

        if "black-enabled" in options:
            options["black-enabled"] = options["black-enabled"].lower() in (
                "yes",
                "true",
                "on",
                "1",
                "sure",
            )

        if "isort-enabled" in options:
            options["isort-enabled"] = options["isort-enabled"].lower() in (
                "yes",
                "true",
                "on",
                "1",
                "sure",
            )
        if "mypy-enabled" in options:
            options["mypy-enabled"] = options["mypy-enabled"].lower() in (
                "yes",
                "true",
                "on",
                "1",
                "sure",
            )

        options["autocomplete-use-omelete"] = self.options[
            "autocomplete-use-omelete"
        ].lower() in ("yes", "true", "on", "1", "sure")

        # Parse linter arguments
        if "pylint-args" in options:
            args = self._normalize_linter_args(options["pylint-args"])
            if args:
                options["pylint-args"] = args
            else:
                del options["pylint-args"]

        if "flake8-args" in options:
            args = self._normalize_linter_args(options["flake8-args"])
            if args:
                options["flake8-args"] = args
            else:
                del options["flake8-args"]

        if "black-args" in options:
            args = self._normalize_linter_args(options["black-args"])
            if args:
                options["black-args"] = args
            else:
                del options["black-args"]

        if "isort-args" in options:
            args = self._normalize_linter_args(options["isort-args"])
            if args:
                options["isort-args"] = args
            else:
                del options["isort-args"]

        if "mypy-args" in options:
            args = self._normalize_linter_args(options["mypy-args"])
            if args:
                options["mypy-args"] = args
            else:
                del options["mypy-args"]

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
        if "jedi-enabled" in options:
            settings[mappings["jedi-enabled"]] = options["jedi-enabled"]

        if "jedi-path" in options:
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
        if "black-enabled" in options and options["black-enabled"]:
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

        if linter_enabled in options:
            try:
                settings[mappings[linter_enabled]] = options[linter_enabled]
            except KeyError:
                if not allow_key_error:
                    raise
        else:
            return

        if not allow_key_error and not options.get(linter_enabled):
            return
        # we care only if flake8 is active
        linter_executable = options.get(linter_path, None)
        if linter_executable is None:
            linter_executable = find_executable_path(name)

        if linter_executable:
            settings[mappings[linter_path]] = self._resolve_executable_path(
                linter_executable
            )

        if linter_args in options:
            settings[mappings[linter_args]] = options[linter_args]

    def _write_project_file(self, settings, existing_settings):
        """Project File Writer:
        This method is actual doing writting project file to file system."""
        with open(os.path.join(self.settings_dir, "settings.json"), "w") as fp:
            try:
                final_settings = existing_settings.copy()
                final_settings.update(settings)
                json.dump(final_settings, fp)

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
    """Nothing much need to do with uninstall, because this recipe is doing so much filesystem writting.
    Depends overwrite option, generated project file is removed."""

    logger = logging.getLogger(name)
    logger.info("uninstalling ...")
    # xxx: nothing for now, but may be removed what ever in options?
