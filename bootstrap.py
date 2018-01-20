#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
import sys
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import join


if __name__ == "__main__":
    base_path = dirname(abspath(__file__))
    print("Project path: {0}".format(base_path))
    env_path = join(base_path, ".tox", "bootstrap")
    if sys.platform == "win32":
        bin_path = join(env_path, "Scripts")
    else:
        bin_path = join(env_path, "bin")
    if not exists(env_path):
        import subprocess

        print("Making bootstrap env in: {0} ...".format(env_path))
        try:
            subprocess.check_call(["virtualenv", env_path])
        except subprocess.CalledProcessError:
            subprocess.check_call([sys.executable, "-m", "virtualenv", env_path])
        print("Installing `jinja2` and `matrix` into bootstrap environment...")
        subprocess.check_call([join(bin_path, "pip"), "install", "jinja2" "py" , "matrix"])
    activate = join(bin_path, "activate_this.py")
    # noinspection PyCompatibility
    exec(compile(open(activate, "rb").read(), activate, "exec"), dict(__file__=activate))

    import jinja2

    import matrix

    jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader(join(base_path, ".templates")),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True
    )
    

    toxEnvironments = {}
    for (alias, conf) in matrix.from_file(join(base_path, "setup.cfg")).items():
        python = conf["python_versions"]
        deps = conf["dependencies"]
        toxEnvironments[alias] = {
            "python": "python" + python if "py" not in python else python,
            "deps": deps.split(),
        }
        if "coverage_flags" in conf:
            cover = {"false": False, "true": True}[conf["coverage_flags"].lower()]
            toxEnvironments[alias].update(cover=cover)
        if "environment_variables" in conf:
            envVars = conf["environment_variables"]
            toxEnvironments[alias].update(envVars=envVars.split())

    for name in os.listdir(join(".templates")):
        if not name.startswith("template"):
            with open(join(base_path, name), "w") as fh:
                fh.write(jinja.get_template(name).render(toxEnvironments=toxEnvironments))
            print("Wrote {}".format(name))
    print("DONE.")
