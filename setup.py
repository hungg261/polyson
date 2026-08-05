import os
import re
from setuptools import setup, find_packages

def get_version():
    init_path = os.path.join(os.path.dirname(__file__), "polyson", "__init__.py")
    with open(init_path, "r", encoding="utf-8") as f:
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', f.read())
        if match:
            return match.group(1)
    raise RuntimeError("Cannot find version string.")

setup(
    name="polyson",
    version=get_version(),
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "polyson": ["templates/sample/**/*", "templates/sample/*", "defaults/**/*", "defaults/*"],
    },
    entry_points={
        "console_scripts": [
            "polyson=polyson.cli:main",
            "son=polyson.cli:main",
        ],
    },
)
