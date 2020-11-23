import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()
# end with

setuptools.setup(
    name='moodools',  # Replace with your own username
    version='0.0.2',
    author='Marco Tosato',
    author_email='marco.tosato@didotech.com',
    description='Utilities for Odoo development',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/LibrERP/Pylibs/moodools/',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Framework :: Odoo',
    ],
    install_requires=['graphviz', ],
    python_requires='>=3.5',
)
