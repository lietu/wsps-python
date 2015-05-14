from distutils.core import setup
from pip.req import parse_requirements

requirements = [
    str(entry.req)
    for entry in parse_requirements("requirements.txt")
]

setup(
    name='wsps',
    packages=['wsps'],
    version='1.0.0',
    description='Python client library for WSPS server',
    author='Janne Enberg',
    author_email='janne.enberg@lietu.net',
    url='https://github.com/lietu/wsps-python',
    download_url='https://github.com/lietu/wsps-python/tarball/0.1',
    keywords=['wsps', 'client', 'pubsub', 'websocket'],
    classifiers=[],
    install_requires=requirements
)
