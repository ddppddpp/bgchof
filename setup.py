try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='bgchof',
    version='0.5.0',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=[
        'tests',
    ],
)
