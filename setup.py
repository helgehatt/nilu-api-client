from setuptools import setup, PEP420PackageFinder

setup(
    name="nilu-api-client",
    version="1.0.0",
    author="helgehatt",
    description="NILU API client",
    url="https://github.com/helgehatt/nilu-api-client",
    packages=PEP420PackageFinder.find(),
    package_data={"": ["**/files/*"]},
    install_requires=["pandas", "requests"],
)
