"""
The pseudo-format supported is (PEP 386):
N.N[.N]+[{a|b|c|rc}N[.N]+][.postN][.devN]
"""
MAJOR = 0
MINOR = 1
EXTRA = 2

__version__ = f'{MAJOR}.{MINOR}.{EXTRA}'
