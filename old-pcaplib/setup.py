
from setuptools import setup

setup(
    name='pcaplib',
    version='0.1',
    description='Library to decode packets from a PCAP packet capture file.',
    packages=['pcaplib'],
    entry_points={
        'console_scripts': ['fdump = pcaplib.fdump:main']
    }
)
