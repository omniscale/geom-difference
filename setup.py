import platform
from setuptools import setup
import pkg_resources

setup(
    name='geom_difference',
    version='0.1.0',
    description='Calculate geometric differences of two GeoJSON/Shapefiles.',
    long_description='',
    url='https://github.com/omniscale/geom-difference',
    author='Oliver Tonnhofer',
    author_email='olt@omniscale.de',
    license='Apache Software License 2.0',
    py_modules=['geom_difference'],
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'geom-difference = geom_difference:main',
        ],
    },
    install_requires=[
        'Shapely',
        'Fiona',
        'pyproj',
        'rtree',
    ],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: GIS",
    ],
)
