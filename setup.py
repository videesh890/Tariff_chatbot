from setuptools import setup, find_packages

setup(
    name='tariff_management_chatbot',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'fastapi',
        'uvicorn',
        'langchain',
        'crewai',
        'pandas',
        'sqlalchemy',
        'python-dotenv'
    ],
    entry_points={
        'console_scripts': [
            'tariff-chatbot=tariff_management_chatbot.main:main'
        ]
    },
)
