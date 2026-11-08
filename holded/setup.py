"""Instala el comando tesela-erp desde el directorio holded/.

Uso recomendado: ejecutar desde la raíz del repositorio con el setup.py raíz.
Este archivo permite también: cd holded && pip install -e .
"""

from setuptools import setup

setup(
    name="tesela-erp",
    version="0.1.0",
    packages=["holded"],
    package_dir={"holded": "."},
    install_requires=[
        "requests>=2.31.0",
        "supabase>=2.0.0",
        "python-dotenv>=1.0.0",
        "tzdata>=2024.1",
    ],
    entry_points={
        "console_scripts": [
            "tesela-erp=holded.cli:main",
        ],
    },
    python_requires=">=3.9",
)
