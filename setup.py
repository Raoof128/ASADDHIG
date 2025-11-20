"""
Setup script for Sovereign AI Gateway.
"""
from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sovereign-ai-gateway",
    version="1.0.0",
    author="Sovereign AI Gateway Team",
    author_email="team@example.com",
    description="Australian Data Sovereignty Enforcement Gateway for AI Inference",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/sovereign_ai_gateway",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "httpx>=0.25.1",
            "black>=23.12.0",
            "flake8>=6.1.0",
            "isort>=5.13.0",
            "mypy>=1.7.0",
            "pylint>=3.0.0",
            "pre-commit>=3.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sovereign-gateway=gateway.gateway:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

