from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
with open(here / "requirements.txt", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='pseudoku',
    version='0.1.0',
    description='A CLI tool for generating sudoku puzzles.',
    author='Anique Lodewijkx',
    author_email='anique.lodewijkx@gmail.com',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pseudoku = pseudoku.sudoku:main',
        ],
    },
)