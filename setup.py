from setuptools import setup

setup(
    name='py-github',
    version='1.0.0',
    packages=['py-github'],
    url='https://github.com/masgeek/py-github.git',
    license='MIT',
    author='Sammy Barasa',
    author_email='barsamms@gmail.com',
    description='Python github api utilities',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3',
    install_requires=[
        "PyGithub", "python-dotenv[cli]"
    ],
)
