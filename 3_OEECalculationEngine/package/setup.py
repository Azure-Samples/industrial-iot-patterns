import setuptools
 
with open("PACKAGEDETAILS.md", "r") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="manufacturingmetrics",
    version="0.1.0",
    author="Jomit Vaghela",
    author_email="",
    description="Package to calculate manufacturing performance metrics and KPIs like OEE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    zip_safe=False
)