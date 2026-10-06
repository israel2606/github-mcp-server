"""Instala el comando tesela-erp en el entorno Python."""

from setuptools import setup, find_packages

setup(
    name="tesela-erp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "supabase>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "tesela-erp=holded.cli:main",
        ],
    },
)
