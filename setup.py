from setuptools import find_packages, setup

setup(
    name="va-shared",
    version="0.1.23",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pydantic>=1.10.17",
        "firebase-admin>=6.0.0",
        "aiohttp>=3.8.0",
        "ulid-py>=1.1.0",
    ],
    python_requires=">=3.10",
    author="Solace Smart",
    description="Shared utilities for Ensi AI Voice Assistant",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Solace-smart/ensi-ai-voice-assistant-shared",
)
