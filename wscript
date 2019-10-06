# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-

APPNAME = 'ndn-mongo-fileserver'

from waflib import Utils, Context
import os, subprocess

def options(opt):
    opt.load(['compiler_cxx', 'gnu_dirs'])
    opt.load(['default-compiler-flags',
              'coverage', 'sanitizers', 'boost',
              'sphinx_build'],
             tooldir=['.waf-tools'])

def configure(conf):
    conf.load(['compiler_cxx', 'gnu_dirs',
               'default-compiler-flags', 'boost', 'sphinx_build'])

    if 'PKG_CONFIG_PATH' not in os.environ:
        os.environ['PKG_CONFIG_PATH'] = Utils.subst_vars('${LIBDIR}/pkgconfig', conf.env)
    conf.check_cfg(package='libndn-cxx', args=['--cflags', '--libs'], uselib_store='NDN_CXX')

    conf.check_cfg(package='libmongocxx', args=['--cflags', '--libs'],
                   uselib_store='MONGOCXX', mt=True)

    boost_libs = ['system', 'program_options', 'filesystem']

    conf.check_boost(lib=boost_libs, mt=True)

    conf.check_compiler_flags()
    # Loading "late" to prevent tests from being compiled with profiling flags
    conf.load('coverage')
    conf.load('sanitizers')

def build(bld):
    bld.objects(target='core-objects',
                source=bld.path.ant_glob('core/*.cpp'),
                use='NDN_CXX BOOST',
                includes='.',
                export_includes='.')

    if Utils.unversioned_sys_platform() == 'linux':
        systemd_units = bld.path.ant_glob('systemd/*.in')
        bld(features='subst',
            name='systemd-units',
            source=systemd_units,
            target=[u.change_ext('') for u in systemd_units])

    bld.recurse('src')

