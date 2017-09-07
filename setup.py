#!/usr/bin/env python
import os
import sys
import shutil
import subprocess
from distutils.core import setup, Command
from distutils.dir_util import remove_tree

MODULE_NAME = "binwalk"
SCRIPT_NAME = MODULE_NAME
MODULE_VERSION = "2.1.2b"
VERSION_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "src", "binwalk", "core", "version.py")

# Python3 has a built-in DEVNULL; for Python2, we have to open
# os.devnull to redirect subprocess stderr output to the ether.
try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

# If this version of binwalk was checked out from the git repository,
# include the git commit hash as part of the version number reported
# by binwalk.
try:
    label = subprocess.check_output(["git", "describe"], stderr=DEVNULL)
    MODULE_VERSION += "-" + label.split('-')[-1].strip()
except subprocess.CalledProcessError:
    pass

# Python2/3 compliance
try:
    raw_input
except NameError:
    raw_input = input


def which(command):
    # /usr/local/bin is usually the default install path, though it may not be in $PATH
    usr_local_bin = os.path.sep.join(
        [os.path.sep, 'usr', 'local', 'bin', command])

    try:
        location = subprocess.Popen(
            ["which", command],
            shell=False, stdout=subprocess.PIPE).communicate()[0].strip()
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        pass

    if not location and os.path.exists(usr_local_bin):
        location = usr_local_bin

    return location


def find_binwalk_module_paths():
    paths = []

    try:
        import binwalk
        paths = binwalk.__path__
    except KeyboardInterrupt as e:
        raise e
    except Exception:
        pass

    return paths


def remove_binwalk_module(pydir=None, pybin=None):
    if pydir:
        module_paths = [pydir]
    else:
        module_paths = find_binwalk_module_paths()

    for path in module_paths:
        try:
            remove_tree(path)
        except OSError:
            pass

    if not pybin:
        pybin = which(MODULE_NAME)

    if pybin:
        try:
            sys.stdout.write("removing '%s'\n" % pybin)
            os.remove(pybin)
        except KeyboardInterrupt:
            pass
        except Exception:
            pass


class IDAUnInstallCommand(Command):
    description = "Uninstalls the binwalk IDA plugin module"
    user_options = [
        ('idadir=', None, 'Specify the path to your IDA install directory.'),
    ]

    def initialize_options(self):
        self.idadir = None
        self.mydir = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "src")

    def finalize_options(self):
        pass

    def run(self):
        if self.idadir is None:
            sys.stderr.write(
                "Please specify the path to your IDA install directory with the '--idadir' option!\n")
            return

        binida_dst_path = os.path.join(self.idadir, 'plugins', 'binida.py')
        binwalk_dst_path = os.path.join(self.idadir, 'python', 'binwalk')

        if os.path.exists(binida_dst_path):
            sys.stdout.write("removing %s\n" % binida_dst_path)
            os.remove(binida_dst_path)
        if os.path.exists(binwalk_dst_path):
            sys.stdout.write("removing %s\n" % binwalk_dst_path)
            shutil.rmtree(binwalk_dst_path)


class IDAInstallCommand(Command):
    description = "Installs the binwalk IDA plugin module"
    user_options = [
        ('idadir=', None, 'Specify the path to your IDA install directory.'),
    ]

    def initialize_options(self):
        self.idadir = None
        self.mydir = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "src")

    def finalize_options(self):
        pass

    def run(self):
        if self.idadir is None:
            sys.stderr.write(
                "Please specify the path to your IDA install directory with the '--idadir' option!\n")
            return

        binida_src_path = os.path.join(self.mydir, 'scripts', 'binida.py')
        binida_dst_path = os.path.join(self.idadir, 'plugins')

        if not os.path.exists(binida_src_path):
            sys.stderr.write(
                "ERROR: could not locate IDA plugin file '%s'!\n" %
                binida_src_path)
            return
        if not os.path.exists(binida_dst_path):
            sys.stderr.write(
                "ERROR: could not locate the IDA plugins directory '%s'! Check your --idadir option.\n" %
                binida_dst_path)
            return

        binwalk_src_path = os.path.join(self.mydir, 'binwalk')
        binwalk_dst_path = os.path.join(self.idadir, 'python')

        if not os.path.exists(binwalk_src_path):
            sys.stderr.write(
                "ERROR: could not locate binwalk source directory '%s'!\n" %
                binwalk_src_path)
            return
        if not os.path.exists(binwalk_dst_path):
            sys.stderr.write(
                "ERROR: could not locate the IDA python directory '%s'! Check your --idadir option.\n" %
                binwalk_dst_path)
            return

        binida_dst_path = os.path.join(binida_dst_path, 'binida.py')
        binwalk_dst_path = os.path.join(binwalk_dst_path, 'binwalk')

        if os.path.exists(binida_dst_path):
            os.remove(binida_dst_path)
        if os.path.exists(binwalk_dst_path):
            shutil.rmtree(binwalk_dst_path)

        sys.stdout.write("copying %s -> %s\n" %
                         (binida_src_path, binida_dst_path))
        shutil.copyfile(binida_src_path, binida_dst_path)

        sys.stdout.write("copying %s -> %s\n" %
                         (binwalk_src_path, binwalk_dst_path))
        shutil.copytree(binwalk_src_path, binwalk_dst_path)


class UninstallCommand(Command):
    description = "Uninstalls the Python module"
    user_options = [
        ('pydir=', None, 'Specify the path to the binwalk python module to be removed.'),
        ('pybin=', None, 'Specify the path to the binwalk executable to be removed.'),
    ]

    def initialize_options(self):
        self.pydir = None
        self.pybin = None

    def finalize_options(self):
        pass

    def run(self):
        remove_binwalk_module(self.pydir, self.pybin)


class CleanCommand(Command):
    description = "Clean Python build directories"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sys.stdout.write("removing %s%s" %(VERSION_FILE, os.linesep))
        os.remove(VERSION_FILE)

        try:
            remove_tree("build")
        except KeyboardInterrupt as e:
            raise e
        except Exception:
            pass

        try:
            remove_tree("dist")
        except KeyboardInterrupt as e:
            raise e
        except Exception:
            pass


class TestCommand(Command):
    description = "Run unit-tests"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import nose
        nose.main(argv=['--exe','--with-coverage'])

# The data files to install along with the module
install_data_files = []
for data_dir in ["magic", "config", "plugins", "modules", "core"]:
    install_data_files.append("%s%s*" % (data_dir, os.path.sep))

# Create a version.py file which defines the current binwalk version.
# This file is excluded from git in the .gitignore file.
sys.stdout.write("creating %s%s" % (VERSION_FILE, os.linesep))
with open(VERSION_FILE, "w") as fp:
    fp.write("# This file has been auto-generated by setup.py" + os.linesep)
    fp.write('__version__ = "%s"' % MODULE_VERSION)

# Install the module, script, and support files
setup(
    name=MODULE_NAME,
    version=MODULE_VERSION,
    description="Firmware analysis tool",
    author="Craig Heffner",
    url="https://github.com/devttys0/%s" % MODULE_NAME,
    requires=[],
    package_dir={"": "src"},
    packages=[MODULE_NAME],
    package_data={MODULE_NAME: install_data_files},
    scripts=[
        os.path.join(
            "src",
            "scripts",
            SCRIPT_NAME)],
    cmdclass={
        'clean': CleanCommand,
        'uninstall': UninstallCommand,
        'idainstall': IDAInstallCommand,
        'idauninstall': IDAUnInstallCommand,
        'test': TestCommand})
