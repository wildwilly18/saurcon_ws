from glob import glob
from setuptools import setup

package_name = 'saurcon_rl'
setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/config', glob('config/*')),
    ],
    install_requires=['setuptools'],
    entry_points={'console_scripts': ['cone_mapper = saurcon_rl.cone_mapper_node:main']},
    zip_safe=True,
    maintainer='wilson',
    description='RL racing policy for SAURCON',
    license='Apache-2.0',
)
