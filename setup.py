from setuptools import setup, find_packages

setup(
    name="student-result-manager",
    version="0.1.0",
    packages=find_packages(),
    py_modules=["student_result_manager", "banners"],
    install_requires=[
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "numpy>=1.20.0",
        "openpyxl>=3.0.0",
        "thefuzz>=0.18.0",
        "python-Levenshtein>=0.12.2",
    ],
    entry_points={
        "console_scripts": [
            "student-result-manager=student_result_manager:main",
        ],
    },
    author="Utkarsh Tiwari",
    description="A CLI tool for managing student results from Excel sheets.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
