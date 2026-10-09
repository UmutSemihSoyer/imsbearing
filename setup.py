from setuptools import setup, find_packages

setup(
    name="imsbearing",
    version="1.0.0",
    description="Enterprise Predictive Maintenance & RUL Estimation Library for Industrial Bearings",
    author="Antigravity Deepmind Team",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.22.0",
        "pandas>=1.4.0",
        "scipy>=1.8.0",
        "scikit-learn>=1.0.0",
        "torch>=2.0.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.20.0"
    ],
    entry_points={
        "console_scripts": [
            "imsbearing=imsbearing.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
