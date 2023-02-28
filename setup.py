from setuptools import setup
from os import path

pwd = path.abspath(path.dirname(__file__))
with open(path.join(pwd, 'README.md'), 'r') as f:
    description = f.read()

setup(
    name='workdrive-sync',
    version='0.0.1',
    description='Python Wrapper for Zoho Workdrive API.',
    author='IT Support',
    author_email='it-support@zilogic.com',
    url='https://repo.zilogic.com/it-admin/workdrive-sync',
    long_description=description,
    long_description_content_type="text/markdown",
    packages=['workdrive_sync'],
    py_modules=['workdrive_sync.workdrive_upload'],
    entry_points={
        'console_scripts': ['workdrive-upload = workdrive_sync.workdrive_upload:main'],
    },
    install_requires=['requests']
)