from setuptools import find_packages, setup

setup(
    name="stocks-monitor",
    version="0.0.1",
    packages=find_packages(),
    author="Giles Shaw",
    author_email="giles.shaw@gmail.com",
    description="A simple stock monitor for the command line.",
    entry_points={
        "console_scripts": ["stocks-monitor=stocks_monitor.cli:cli"]
    },
    install_requires=["numpy", "pandas", "requests", "toml", "urwid"],
    python_requires=">=3.6",
)
