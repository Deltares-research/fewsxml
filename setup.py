from setuptools import setup, find_packages

setup(
    name="fewsxml",
    version="0.1.3",
    packages=find_packages(),
    install_requires=["numpy"],
    include_package_data=True,
    package_data={
        "fewsxml": ["config.xml"],
    },
    author="Farid Alavi",
    author_email="farid.alavi@deltares.nl",
    description="A library for reading and writing XML files to interact with Delft-FEWS.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/FaridAlavi/fewsxml",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
