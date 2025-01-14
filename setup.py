from setuptools import setup, find_packages

setup(
    name="call-center-calculator",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "streamlit>=1.32.0",
        "plotly>=5.18.0",
        "pandas>=2.2.0",
        "numpy>=1.24.0",
        "pytest>=8.0.0",
        "matplotlib>=3.8.2",
    ],
    entry_points={
        "console_scripts": [
            "call-center-calculator=src.app:main",
        ],
    },
    python_requires=">=3.8",
)
