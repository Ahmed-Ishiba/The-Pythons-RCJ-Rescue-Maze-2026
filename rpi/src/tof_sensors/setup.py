from setuptools import find_packages, setup

package_name = 'tof_sensors'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ishiba',
    maintainer_email='ahmedishiba9@gmail.com',
    description='ros node to read data from tof sensor',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'tof_node = tof_sensors.read_sensors:main',
        ],
    },
)
