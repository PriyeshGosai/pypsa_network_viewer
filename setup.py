"""
Setup script for pypsa_network_viewer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pypsa-network-viewer",
    version="0.2.0",
    author="Priyesh Gosai",
    description="Interactive HTML viewer for PyPSA networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pypsa>=0.20.0",
        "plotly>=5.0.0",
    ],
    keywords="pypsa, network, visualization, interactive, html",
    project_urls={
        "Bug Reports": "https://github.com/PriyeshGosai/pypsa_network_viewer/issues",
        "Source": "https://github.com/PriyeshGosai/pypsa_network_viewer",
    },
)