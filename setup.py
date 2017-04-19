from setuptools import setup

OPTIONS = {
    'iconfile': 'icon.icns'
    }
DATA_FILES = ['guetzli-osx']
setup(
    app=["Guetzli-R.py"],
    options={'py2app': OPTIONS},
    data_files=DATA_FILES,
    setup_requires=["py2app"],
)
