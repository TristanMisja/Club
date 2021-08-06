import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.rst").read_text()

REQUIREMENTS = open('requirements.txt','r').read().split('\n')

setup(
    name="club",
    version="1.0.0",
    description="Command Line Utility Belt",
    long_description=README,
    long_description_content_type="text/x-rst",
    url="https://github.com/TristanMisja/Club",
    download_url="https://github.com/TristanMisja/Club",
    author="Tristan S. Misja",
    author_email="TristanMisja09@gmail.com",
    maintainer="Tristan S. Misja",
    maintainer_email="TristanMisja09@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Terminals",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English"
    ],
    keywords="cmd commandline terminal utility belt command line argument unix utilities posix bsd linux",
    packages=['club'], # find_packages(),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    requires=REQUIREMENTS,
    provides=["club"],
    zip_safe=False,
    entry_points={},
    project_urls={
        "Bug Tracker": "https://github.com/TristanMisja/Club/issues",
#         "Documentation": "",
        "Source Code": "https://github.com/TristanMisja/Club"
    }
)
