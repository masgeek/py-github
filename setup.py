import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='py-github',
    version='1.0.0',
    packages=setuptools.find_packages(),
    url='https://github.com/masgeek/py-github.git',
    license='MIT',
    author='Sammy Barasa',
    author_email='barsamms@gmail.com',
    description='Python github api utilities',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3',
    install_requires=[
        "python-env"
    ],
)
