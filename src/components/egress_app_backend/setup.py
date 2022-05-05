import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="egress_backend",
    version="0.0.1",

    description="CDK Backend for Egress App",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "egress_backend"},
    packages=setuptools.find_packages(where="egress_backend"),

    install_requires=[
        "aws-cdk.core==1.154.0",
        "aws-cdk.pipelines==1.154.0",
        "aws-cdk.aws-lambda==1.154.0",
        "aws-cdk.aws-s3==1.154.0",
        "aws-cdk.aws-s3-notifications==1.154.0",
        "aws-cdk.aws-amplify==1.154.0",
        "aws-cdk.aws-cognito==1.154.0",
        "aws-cdk.aws-sns==1.154.0",
        "aws-cdk.aws-sns-subscriptions==1.154.0",
        "aws-cdk.aws-stepfunctions==1.154.0",
        "aws-cdk.aws-stepfunctions-tasks==1.154.0",
        "aws-cdk.aws-dynamodb==1.154.0",
        "aws-cdk.aws-kms==1.154.0",
        "aws-cdk.aws-codestarnotifications==1.154.0",
        "aws-cdk.aws-appsync==1.154.0",
        "aws-cdk.aws-ssm==1.154.0",
        "aws-cdk.aws-iam==1.154.0",
        "aws-cdk.aws-cloudfront==1.154.0",
        "aws-cdk.aws-cloudfront-origins==1.154.0",
        "aws-cdk.aws-ec2==1.154.0",
        "aws-cdk.aws-efs==1.154.0",
        "aws-cdk.aws-ses==1.154.0",
        "cdk-nag==1.5.7"
    ],

    tests_require=[
        "pytest",
        "tox",
        "moto[s3,sns,dynamodb]",
        "aws-cdk.assertions==1.154.0"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

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
