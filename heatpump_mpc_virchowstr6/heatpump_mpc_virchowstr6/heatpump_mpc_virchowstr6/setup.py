"""
Setup script for Heat Pump MPC Control System
"""
from setuptools import setup, find_packages

setup(
    name="heatpump_mpc_virchowstr6",
    version="1.0.0",
    description="MPC control system for iDM AERO ALM 4-12 heat pump at Virchowstr. 6",
    author="Building Automation System",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "casadi>=3.5.5",
        "pyyaml>=5.4.0"
    ],
    python_requires=">=3.8",
)
