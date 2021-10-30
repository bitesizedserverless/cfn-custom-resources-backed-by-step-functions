"""Project setup."""

import setuptools

with open(file="README.md", encoding="utf-8") as fp:
    long_description = fp.read()

setuptools.setup(
    name="CFN Custom Resources backed by Step Functions",
    version="0.0.1",
    description="Bite-Sized Serverless: CFN Custom Resources backed by Step Functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bite-Sized Serverless",
    package_dir={"": "cfn_custom_resources_backed_by_step_functions"},
    packages=setuptools.find_packages(
        where="cfn_custom_resources_backed_by_step_functions"
    ),
    install_requires=[
        "aws-cdk.core==1.130.0",
        "aws-cdk.aws-lambda==1.130.0",
        "aws-cdk.aws-stepfunctions==1.130.0",
        "aws-cdk.aws-stepfunctions-tasks==1.130.0",
        "black==21.6b0",
        "pylint==2.10.2",
        "python-dotenv==0.17.0",
        "stringcase==1.2.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
