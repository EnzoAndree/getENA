from setuptools import setup
with open("README.md", "r") as fh:
    long_description = fh.read()

# This call to setup() does all the work
setup(
    name="getENA",
    version="1.2.2",
    description="Read the latest Real Python tutorials",
    url="https://github.com/EnzoAndree/getENA",
    author="Enzo Guerrero-Araya",
    author_email="biologoenzo@gmail.com",
    license="GNU General Public License v3.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['getENA'],
    install_requires=["tqdm", "pandas"],
    scripts = ['getENA/getENA.py'],
)
