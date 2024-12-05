import numpy as np
import pyexr

from .mtlx_baker import MTLXBaker
from pathlib import Path
from typing import Dict

def bake_to_numpy(mtlx_path: Path) -> Dict[str, Dict[str, np.ndarray]]:
    """
    Given an .mtlx path returns baked textures as numpy array. The result will be wrapped in a dictionary
    with map names as keys and corresponding numpy arrays as values.
    """
    baker = MTLXBaker(mtlx_path)
    return baker.bake()

def bake_to_file(mtlx_path: Path, output_path: Path):
    baker = MTLXBaker(mtlx_path)

    for graph, textures in baker.bake().items():
        pyexr.write(output_path.joinpath(f"{mtlx_path.stem}_{graph}.exr"), textures)
