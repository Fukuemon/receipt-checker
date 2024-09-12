from setuptools import setup, find_packages

setup(
    name="receipt_check",
    version='0.1.0',
    description="This is a receipt check package.",
    packages=find_packages(where="libs"),
    package_dir={"": "libs"},
    author="Fukuemon",
)