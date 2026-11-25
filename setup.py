from setuptools import setup, find_packages

setup(
    name="panelforge",
    version="0.1.0",
    author="Yahya Ali Khan",
    packages=find_packages(),
    install_requires=[
        "pillow>=10.0.0",
        "fastapi>=0.110.0",
        "uvicorn>=0.28.0",
        "reportlab>=4.0.0",
        "pytest>=8.0.0",
        "python-multipart>=0.0.9"
    ],
    entry_points={
        "console_scripts": [
            "panelforge=panelforge.cli:main"
        ]
    }
)
