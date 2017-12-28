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

if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent
    print("Project path: {0}".format(base_path))
    
    def get_binary_archi(filepath):
        """ get binary architecture of a binary file by alternative method to win32file (not working here) 
        
        from https://stackoverflow.com/questions/1345632/determine-if-an-executable-or-library-is-32-or-64-bits-on-windows 
        """
        if not isinstance(filepath,Path):
            filepath = Path(filepath)
        f = filepath.open('rb')
        s = f.read(2)
        if s!="MZ":
            f.close()
            raise Exception("%s is not a binary file"%filepath.resolve())
        else:
            import struct
            f.seek(60)
            s=f.read(4)
            header_offset=struct.unpack("<L", s)[0]
            f.seek(header_offset+4)
            s=f.read(2)
            f.close()
            machine=struct.unpack("<H", s)[0]
            IMAGE_FILE_MACHINE_I386=332
            IMAGE_FILE_MACHINE_IA64=512
            IMAGE_FILE_MACHINE_AMD64=34404
            archis = {IMAGE_FILE_MACHINE_I386:'x86',IMAGE_FILE_MACHINE_IA64:'IA64',IMAGE_FILE_MACHINE_AMD64:'x64'}
            return archis.get(machine,"Unknown architecture")

    def extract_pyver_from_dir(pydirpath):
        """ extract python version from binary found in a directory on windows """
        if not isinstance(pydirpath,Path):
            pydirpath = Path(pydirpath)
        if os.name == 'nt': # only works for windows, looking for dlls
            dlls = sorted(pydirpath.glob('**/python*.dll'))
            import re
            dlls = [dll for dll in dlls if re.match('python[0-9][0-9]\.',dll.name) is not None]
            if len(dlls)==1:
                archi = get_binary_archi(dlls[0])
                import win32api
                info = win32api.GetFileVersionInfo(str(dlls[0]), "\\")
                ms = info['FileVersionMS']
                (M,m) = win32api.HIWORD(ms), win32api.LOWORD(ms)
                return (M,m), archi
            # case pypy: we check pypy dll for archi and lib-python directory for version
            dlls = sorted(pydirpath.glob('**/libpypy*.dll'))
            if len(dlls)==1:
                archi = get_binary_archi(dlls[0])
                lps = sorted(pydirpath.joinpath('lib-python').glob('*'))
                assert len(lps) == 1
                (M,m) = lps[0].name.split('.') # split major/minor
                return (int(M),int(m)), archi
                

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
        ver, archi = extract_pyver_from_dir(envp)
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
        
    from lxml import etree
    root = etree.parse(str(pyproj)) # parse pyproj file
    nsmap = root.getroot().nsmap # get namespace
    pnode = root.getroot() # get main node
    
    # add includes and source files
    for el, fs in [('Content',incs),('Compile',srcs),('Folder',dirs)]:
        if root.find('.//ItemGroup/%s'%el,nsmap) is not None:
            par=root.find('.//ItemGroup/%s'%el,nsmap).getparent()
            for i in par: # remove existing items
                par.remove(i)
        else:
            par = etree.SubElement(pnode,'ItemGroup') 
        for f in fs:
            etree.SubElement(par,el,Include=str(f))
    
    # adds Python environments
    # remove existing ones
    if root.find('.//ItemGroup/Interpreter',nsmap) is not None:
        par=root.find('.//ItemGroup/Interpreter',nsmap).getparent()
        for i in par: # remove existing items
            par.remove(i)
    else:
        par = etree.SubElement(pnode,'ItemGroup') 
    # adds environments
    for alias, toxenv in tox_environments.items():
        toxdir = toxenv['path']
        i = etree.SubElement(par,'Interpreter',Include=str(toxdir),nsmap=nsmap)
        etree.SubElement(i,"Id").text = "Tox %s" % (alias)
        etree.SubElement(i,"Description").text = "%s %s (%s)" % (alias,toxenv['python'],toxenv['archi'])
        pyexe = sorted(toxdir.glob('**/python.exe'))
        assert len(pyexe)==1,pyexe
        etree.SubElement(i,"InterpreterPath").text = str(pyexe[0].relative_to(toxdir))
        pywexe = sorted(toxdir.glob('**/pythonw.exe'))
        if len(pywexe)==0:
            pywexe = pyexe # use normal interpreter (case for pypy)
        assert len(pywexe)==1,pywexe
        etree.SubElement(i,"WindowsInterpreterPath").text = str(pywexe[0].relative_to(toxdir))
        etree.SubElement(i,"Version").text = "%d.%d"%(toxenv['pyver'])
        etree.SubElement(i,"Architecture").text = "%s"%(toxenv['archi'])
        pyenvvars = etree.SubElement(i,"PathEnvironmentVariable")
        pyenvvars.text = "PYTHONPATH"
        # TODO, to add environment variables
        for v in toxenv['env_vars']:
            raise Exception('not implemented yet')
        
    root.write(str(pyproj),pretty_print=True, xml_declaration=True, encoding='UTF-8')    