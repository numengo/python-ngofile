#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
bootstrap to recreate .pyproj visual studio python project from
existing directory and installed environments by TOX
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
import sys
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import join
from pathlib import Path
import matrix
from xml import etree
from xml.etree import ElementTree as ET
import re
import py.path 
 
if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent
    print("Project path: {0}".format(base_path))
 
    def extract_pyver_from_dir(pydirpath):
        """ extract python version from binary found in a directory on windows """
        if not isinstance(pydirpath,Path):
            pydirpath = Path(pydirpath)
        print('pydirpath: %s'%str(pydirpath))
        if os.name == 'nt': # only works for windows, looking for dlls
            dlls  = sorted(pydirpath.glob('python*.exe'))
            dlls += sorted(pydirpath.glob('bin\\python*.exe'))
            dlls += sorted(pydirpath.glob('Scripts\\python*.exe'))
        assert len(dlls) > 0, "no executable python*.exe found in directory %s"%(pydirpath)
        pyexepath = dlls[0].resolve()
        print(str(pyexepath))
        pyexepath = py.path.local(str(pyexepath))
        out = pyexepath.sysexec("-c",
                                       "import sys; "
                                       "print(sys.executable);"
                                       "print(list(sys.version_info)); "
                                       "import platform;"
                                       "print(platform.architecture()[0]);"
                                       "print(sys.version);"
                                       )
        lines = out.splitlines()
        executable = lines.pop(0)
        ver = eval(lines.pop(0))
        version_info = '%i.%i.%i'%(ver[0],ver[1],ver[2])
        archi = lines.pop(0)
        version = "\n".join(lines)
        return dict(
            executable=executable,
            version_info=version_info,
            version=version,
            archi=archi)
              

    tox_environments = {}
    for (alias, conf) in matrix.from_file(str(base_path.joinpath("setup.cfg"))).items():
        python = conf["python_versions"]
        deps = conf["dependencies"]
        tox_environments[alias] = {
            "python": "python" + python if "py" not in python else python,
            "deps": deps.split(),
        }
        if "coverage_flags" in conf:
            cover = {"false": False, "true": True}[conf["coverage_flags"].lower()]
            tox_environments[alias].update(cover=cover)
        if "environment_variables" in conf:
            env_vars = conf["environment_variables"]
            tox_environments[alias].update(env_vars=env_vars.split())
        print('found python environment', (alias, tox_environments[alias]['python']))
        envp = Path('.tox/%s'%alias)
        dirpath = Path(__file__).resolve().parent.joinpath(envp)
        version_info = extract_pyver_from_dir(dirpath)
        #print(version_info)
        ver = version_info['version_info']
        archi = version_info['archi']
        tox_environments[alias].update({'pyver':ver,'archi':archi,'path':envp})
        


    def list_files(path,patterns='*',excludes=[]):
        """ list files in a path following a list of patterns and a list of excludes """
        if not isinstance(path,Path):
            path = Path(path)
        from fnmatch import fnmatch
        if not isinstance(patterns,list):
            patterns = [patterns]
        ret = []
        for f in path.glob('*'):
            if any([fnmatch(f.name,e) for e in excludes]):
                continue
            fp = path.joinpath(f.name)
            if fp.is_dir():
                ret += list_files(fp,patterns,excludes)
            elif any([fnmatch(f.name,p) for p in patterns]):
                ret.append(fp)
        return ret
    
    inc_patterns = ['*.txt', '*.ini', '*.cfg', '*json', '*.html', '*.css', '*.js', '*.rst']
    excludes     = ['.*', 'envs', 'dist', 'build','__pycache__', '*.egg-info']
    srcs = list_files(base_path,"*.py",excludes)
    incs = list_files(base_path,inc_patterns,excludes)
    dirs = list(set([str(p.parent.resolve()) for p in srcs+incs]))
    dirs = [Path(d) for d in dirs]

    pyprojs = sorted(base_path.glob('*.pyproj'))
    assert len(pyprojs) == 1, "only works with one file .pyproj in the directory"
    pyproj = pyprojs[0]
        
    root = ET.parse(str(pyproj)) # parse pyproj file
            
    def namespace(element):
        m = re.match('\{.*\}', element.tag)
        return m.group(0) if m else ''
    nsmap = namespace(root.getroot())[1:-1]
    ET.register_namespace('',nsmap)   
    print('nsmap: %s'%nsmap)
    pnode = root.getroot() # get main node
    
    # add includes and source files
    for el, fs in [('Content',incs),('Compile',srcs),('Folder',dirs)]:
        if root.find('.//ItemGroup/%s'%el,nsmap) is not None:
            par=root.find('.//ItemGroup/%s'%el,nsmap).getparent()
            for i in par: # remove existing items
                par.remove(i)
        else:
            par = ET.SubElement(pnode,'ItemGroup') 
        for f in fs:
            ET.SubElement(par,el,Include=str(f))
    
    # adds Python environments
    # remove existing ones
    if root.find('.//ItemGroup/Interpreter',nsmap) is not None:
        par=root.find('.//ItemGroup/Interpreter',nsmap).getparent()
        for i in par: # remove existing items
            par.remove(i)
    else:
        par = ET.SubElement(pnode,'ItemGroup') 
    # adds environments
    for alias, toxenv in tox_environments.items():
        toxdir = toxenv['path']
        i = ET.SubElement(par,'Interpreter',Include=str(toxdir),nsmap=nsmap)
        ET.SubElement(i,"Id").text = "Tox %s" % (alias)
        ET.SubElement(i,"Description").text = "%s %s (%s)" % (alias,toxenv['python'],toxenv['archi'])
        pyexe = sorted(toxdir.glob('**/python.exe'))
        assert len(pyexe)==1,pyexe
        ET.SubElement(i,"InterpreterPath").text = str(pyexe[0].relative_to(toxdir))
        pywexe = sorted(toxdir.glob('**/pythonw.exe'))
        if len(pywexe)==0:
            pywexe = pyexe # use normal interpreter (case for pypy)
        assert len(pywexe)==1,pywexe
        ET.SubElement(i,"WindowsInterpreterPath").text = str(pywexe[0].relative_to(toxdir))
        ET.SubElement(i,"Version").text = "%s"%(toxenv['pyver'])
        ET.SubElement(i,"Architecture").text = "%s"%(toxenv['archi'])
        pyenvvars = ET.SubElement(i,"PathEnvironmentVariable")
        pyenvvars.text = "PYTHONPATH"
        # TODO, to add environment variables
        for v in toxenv['env_vars']:
            raise Exception('not implemented yet')
    root.write(str(pyproj), xml_declaration=True, encoding='UTF-8')    