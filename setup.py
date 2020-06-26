# _*_ coding: utf-8 _*_
from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = "\n\n".join(
    [
        read("README.rst"),
        read("src", "collective", "recipe", "vscode", "recipes.rst"),
        read("CONTRIBUTORS.rst"),
        read("CHANGES.rst"),
    ]
)

install_requires = ["setuptools", "zc.buildout", "zc.recipe.egg"]
tests_require = ["zope.testing", "zc.buildout[test]", "zc.recipe.egg"]

entry_point = "collective.recipe.vscode:Recipe"
uninstall_entry_point = "collective.recipe.vscode:uninstall"
entry_points = {
    "zc.buildout": ["default = {0}".format(entry_point)],
    "zc.buildout.uninstall": ["default = {0}".format(uninstall_entry_point)],
}

setup(
    name="collective.recipe.vscode",
    version="0.1.5",
    description="Visual Studio Code configuration for buildout-based Python projects",
    long_description=long_description,
    # Get more from https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="python buildout plone vscode jedi sublimelinter buildout-recipe anaconda",
    author="Md Nazrul Islam",
    author_email="email2nazrul@gmail.com",
    url="https://github.com/nazrulworld/collective.recipe.vscode",
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["collective", "collective.recipe"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={"test": tests_require},
    entry_points=entry_points,
)
