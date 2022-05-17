import setuptools

with open("README.md") as fp:
    long_description = fp.read()
setuptools.setup(
    name="workspace-backup",
    version="0.0.1",
    description="Infrastructure for TRE workspace backups.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AWS Professional Services",
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    install_requires=[
        "aws-cdk-lib==2.21.0",
        "constructs==10.0.12",
        "cdk-nag==2.12.32",
        "pytest==6.2.5",
        "black==21.12b0",
        "flake8==4.0.1",
        "pip==21.3.1",
        "pre-commit==2.16.0",
        "isort==5.10.1",
        "safety==1.10.3",
        "bandit==1.7.1",
        "coverage==6.2",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
