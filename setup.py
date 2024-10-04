# setup.py

from setuptools import setup, find_packages

setup(
    name='DocScribe',
    version='1.0.0',
    description='A tool to generate AI-optimized code documentation.',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        'aiofiles',
        'astor',
        'black',
        'autoflake',
        'nltk',
        'tinycss2',
        'beautifulsoup4',
        'openai',
        'faiss-cpu',
        'sentence-transformers',
        # Add other dependencies as needed
    ],
    entry_points={
        'console_scripts': [
            'docscribe=main:main',
        ],
    },
    python_requires='>=3.7',
)
