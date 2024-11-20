from setuptools import setup, find_packages
setup(
    name="cpu_resource_monitor",
    version="1.0.0",
    description="Monitor CPU load",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SeasonChains/cpu_utilization",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "psutil", "pyintsaller", "logging"
    ],
    entry_points={"console_scripts": ["cpu_resource_monitor=resource_monitor.__main__:cpu_load"]},
)