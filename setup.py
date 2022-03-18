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
    version="0.1.5-rc0",
    author="Adam Tyson",
    author_email="code@adamltyson.com",
    license="BSD-3-Clause",
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
    url="https://brainglobe.info",
    project_urls={
        "Source Code": "https://github.com/brainglobe/brainglobe-napari-io",
        "Bug Tracker": "https://github.com/brainglobe/brainglobe-napari-io/issues",
        "Documentation": "https://docs.brainglobe.info",
        "User Support": "https://forum.image.sc/tag/brainglobe",
        "Twitter": "https://twitter.com/brain_globe",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: napari",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "napari.manifest": [
            "brainglobe-napari-io = brainglobe_napari_io:napari.yaml",
        ],
    },
    package_data={"brainglobe_napari_io": ["napari.yaml"]},
)
