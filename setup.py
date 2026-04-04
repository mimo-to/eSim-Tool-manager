from setuptools import setup, find_packages

setup(
    name="esim-tool-manager",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "rich>=13.0.0",
        "textual>=0.47.0",
        'tomli>=2.0.0; python_version < "3.11"'
    ],
    package_data={
        "src": ["tools.toml"]
    },
    include_package_data=True,
    entry_points={
        "console_scripts": ["esim-tm=src.cli:main"]
    },
    python_requires=">=3.9"
)
