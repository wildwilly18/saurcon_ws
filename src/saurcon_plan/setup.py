from setuptools import setup

package_name = 'saurcon_plan'
setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    entry_points={'console_scripts': [
        'cone_follower = saurcon_plan.cone_follower_node:main',
        'cone_mapper = saurcon_plan.cone_mapper_node:main',
    ]},
    zip_safe=True,
    maintainer='wilson',
    description='SAURCON planning: cone detection and memory, track geometry, classical cone follower',
    license='Apache-2.0',
)
