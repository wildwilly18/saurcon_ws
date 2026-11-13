import importlib.util
from pathlib import Path
import tempfile
import unittest
from launch import LaunchContext

spec=importlib.util.spec_from_file_location('rtabmap_launch',Path(__file__).parents[1]/'launch/rtabmap_sim.launch.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class DatabaseGuardTest(unittest.TestCase):
    def test_localization_cannot_delete(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'map.db';path.write_bytes(b'preserve-map')
            context=LaunchContext();context.launch_configurations.update(visual_odometry='false',mode='localization',database_path=str(path),reset_database='true')
            with self.assertRaises(ValueError):m.setup(context)
            self.assertEqual(path.read_bytes(),b'preserve-map')
    def test_localization_requires_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            context=LaunchContext();context.launch_configurations.update(visual_odometry='false',mode='localization',database_path=str(Path(tmp)/'absent.db'),reset_database='false')
            with self.assertRaises(ValueError):m.setup(context)
    def test_initial_pose_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'map.db';path.write_bytes(b'preserve-map')
            base=dict(visual_odometry='false',database_path=str(path),reset_database='false')
            for bad in (dict(mode='mapping',initial_pose='0 0 0 0 0 0'), dict(mode='localization',initial_pose='0 0 3.14')):
                context=LaunchContext();context.launch_configurations.update(base,**bad)
                with self.assertRaises(ValueError):m.setup(context)
            context=LaunchContext();context.launch_configurations.update(base,mode='localization',initial_pose='0.254 0 0 0 0 3.14159')
            nodes=m.setup(context)
            self.assertEqual([n.node_executable for n in nodes],['rtabmap','map_cleaner.py'])

if __name__=='__main__':unittest.main()
