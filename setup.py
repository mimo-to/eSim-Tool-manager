from setuptools import setup, find_packages

setup(
    name="esim-tool-manager",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["rich>=13.0.0"],
    entry_points={
        "console_scripts": ["esim-tm=src.cli:main"]
    },
    python_requires=">=3.9"
)
