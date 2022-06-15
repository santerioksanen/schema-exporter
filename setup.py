from setuptools import setup

setup(
    name='marshmallow-export',
    version='0.1.0',
    description='Export Marshmallow schemas to Rust and Typescript',
    author='Santeri Oksanen',
    url='https://github.com/santerioksanen/marshmallow-export',
    packages=['marshmallow_export'],
    install_requires=['marshmallow', 'marshmallow_enum'],
)
