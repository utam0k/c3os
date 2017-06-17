from setuptools import setup, find_packages


def load_requires_from_file(filepath):
    return [pkg_name.rstrip('\r\n') for pkg_name in open(filepath).readlines()]


def install_requires():
    return load_requires_from_file('requirements.txt')

exclude_packages = ['c3os/tests']

setup(name='c3os',
      version='1.0.0',
      description='c3os project',
      packages=find_packages(exclude=exclude_packages),
      install_requires=install_requires(),
      test_suite = 'tests',
      entry_points="""
        [console_scripts]
        c3os = c3os.c3os:main
        """,
      )
