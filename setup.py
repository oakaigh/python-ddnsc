import config.consts

import setuptools

setuptools.setup(
    name = 'python-ddnsc',
    version = '0.0.0',
    description = 'Python DDNS client.',
    long_description = None,
    author = None,
    author_email = None,
    maintainer = None,
    maintainer_email = None,
    url = None,
    license = None,
    python_requires = '>=3.2',
    install_requires = [
        'cloudflare>=2.8.15',
        'pyroute2>=0.6.4',
        'dnspython>=2.1.0'
    ],
    packages = setuptools.find_packages(),
    entry_points = {
        'console_scripts': [
            f'{config.consts.EXECUTABLE} = {config.consts.ENTRY_POINT}',
        ],
    }
)
