from setuptools import setup, find_packages

setup(
    name="polyson",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "polyson": ["templates/sample/**/*", "templates/sample/*", "defaults/**/*", "defaults/*"],
    },
    entry_points={
        "console_scripts": [
            "polyson=polyson.__init__:main",
            "son=polyson.__init__:main",
        ],
    },
)
