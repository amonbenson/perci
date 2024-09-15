"""
A simple reactive state management library.
"""

from setuptools import setup, find_packages

setup(
    name="perci",
    version="0.1.0",
    description="A simple reactive state management library.",
    author="Amon Benson",
    author_email="amonkbenson@gmail.com",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    install_requires=[],
    python_requires=">=3.9",
)
