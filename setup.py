import setuptools
from mindsdb_server.version import mindsdb_version
with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as req_file:
    requirements = req_file.read().splitlines()
print(mindsdb_version)
setuptools.setup(
    name="mindsdb_server",
    version=mindsdb_version,
    author="MindsDB Inc",
    author_email="jorge@mindsdb.com",
    description="MindsDB server, provides server capabilities to mindsdb native python library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mindsdb/mindsdb_server",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    python_requires=">=3.4"
)