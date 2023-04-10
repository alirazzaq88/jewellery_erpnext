from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in jewellery_erpnext/__init__.py
from jewellery_erpnext import __version__ as version

setup(
	name="jewellery_erpnext",
	version=version,
	description="jewellery custom app",
	author="Nirali",
	author_email="nirali@ascratech.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
