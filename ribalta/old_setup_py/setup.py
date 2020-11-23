import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()
# end with

setuptools.setup(
    name='ribalta',
    version='0.0.2',
    author='Marco Tosato',
    author_email='marco.tosato@didotech.com',
    description='Create RiBa CBI file out of Odoo objects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/LibrERP/Pylibs/ribalta/',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Framework :: Odoo',
    ],
    install_requires=['mako', ],
    python_requires='>=3.5',
)
