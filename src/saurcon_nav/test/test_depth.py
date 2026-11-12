import importlib.util
from pathlib import Path
import unittest
import numpy as np
spec=importlib.util.spec_from_file_location('oak_depth',Path(__file__).parents[1]/'scripts/oak_depth.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class DepthTest(unittest.TestCase):
    def test_range_and_texture(self):
        z=np.array([[np.nan,np.inf,-1,.1,.5,1,2,4.1]],dtype=np.float32)
        image=np.zeros_like(z)
        result=m.degrade_depth(z,image,np.random.default_rng(1),disparity_std=0,texture_threshold=0)
        np.testing.assert_array_equal(result,[[0,0,0,0,500,1000,2000,0]])
        self.assertEqual(m.degrade_depth(z,image,np.random.default_rng(1)).sum(),0)
    def test_quadratic_noise(self):
        image=np.zeros((200,200),dtype=np.uint8)
        std=[]
        for distance in (1,2):
            z=np.full(image.shape,distance,dtype=np.float32)
            out=m.degrade_depth(z,image,np.random.default_rng(1),texture_threshold=0)
            std.append(out.astype(float).std())
        self.assertAlmostEqual(std[1]/std[0],4,delta=.1)
if __name__=='__main__':unittest.main()
