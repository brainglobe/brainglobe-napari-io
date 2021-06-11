from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

requirements = [
    "napari",
    "napari-plugin-engine >= 0.1.4",
    "napari-ndtiffs",
    "tifffile>=2020.8.13",
    "imlib",
    "bg_space",
    "bg-atlasapi",
]

setup(
    name="brainglobe-napari-io",
    version="0.1.0",
    author="Adam Tyson",
    author_email="adam.tyson@ucl.ac.uk",
    license="GPL-3.0",
    description="Read and write files from the BrainGlobe neuroanatomy suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black",
            "pytest-cov",
            "pytest",
            "gitpython",
            "coverage>=5.0.3",
            "bump2version",
            "pre-commit",
            "flake8",
        ]
    },
    url="https://cellfinder.info",
    project_urls={
        "Source Code": "https://github.com/brainglobe/brainglobe-napari-io",
        "Bug Tracker": "https://github.com/brainglobe/brainglobe-napari-io/issues",
        "Documentation": "https://docs.brainglobe.info",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Framework :: napari",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
    ],
    entry_points={
        "napari.plugin": [
            "brainglobe-io = brainglobe_napari_io.plugins",
            "brainreg-standard = brainglobe_napari_io.brainreg.reader_dir_standard_space",
        ]
    },
)
