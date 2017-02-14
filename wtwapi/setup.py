from setuptools import setup

setup(
    name='what_to_wear_api',
    version='0.0.1',
    description='An attempt to build a testable RESTful API.',
    packages=['wtwapi'],
    include_package_data=True,
    install_requires=[
        'flask',
        ],
    setup_requires=[
        'pytest-runner',
        ],
    tests_require=[
        'pytest',
        ],
    )
