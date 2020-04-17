from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', 'r') as f:
    readme = f.read()


setup(
    name='GitHubProjectManager',
    version='0.1',
    url='https://github.com/ronykoz/GitHubProjectManager',
    license='MIT',
    author='Rony Kozakish',
    author_email='',
    description='GitHub automatic project manager tool',
    install_requires=requirements,
    packages=find_packages(),
    include_package_data=True,
    keywords=[
        "GitHub",
        "Project",
        "Manager",
        "GitHubProjectManager",
        "project",
        "manage",
        "manager"
    ],
    long_description=readme,
    long_description_content_type='text/markdown',
    python_requires=">=3.7",
    entry_points={
        'console_scripts': ['GitHubProjectManager = src.cli:main']
    },
    classifiers=[
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ]
)
