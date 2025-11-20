from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sa-investment-analyzer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Institutional-grade investment analytics for SA investors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sa-investment-analyzer",
    packages=find_packages(exclude=["tests", "notebooks"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "sa-invest=scripts.cli:main",
        ],
    },
)