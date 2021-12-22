from os import environ

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nango",
    version=environ.get("VERSION_STRING", "dev"),
    author="Nick Farrell",
    author_email="nicholas.farrell@gmail.com",
    description="Provide model integrity between requests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nicois/nango",
    project_urls={
        "Bug Tracker": "https://github.com/nicois/nango/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "project"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)
