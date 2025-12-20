from setuptools import setup, find_packages

setup(
    name="ezycspm",
    version="0.1.0",
    description="EzyCPSM - Lightweight AWS Cloud Security Posture Management tool",
    author="Rudra Pratap Singh",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.24.0",
        "botocore>=1.27.0",
        "python-dotenv>=0.20.0",
        "SQLAlchemy>=1.4.0",
        "colorlog>=6.7.0",
        "tqdm>=4.64.0",
    ],
    entry_points={
        "console_scripts": [
            "ezycspm=easy_cspm.cli:main",
        ],
    },
    include_package_data=True,
)
