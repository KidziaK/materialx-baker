import numpy as np
import pyexr

from .mtlx_baker import MTLXBaker
from pathlib import Path
from typing import Dict, List

def bake_to_numpy(mtlx_path: Path) -> Dict[str, Dict[str, np.ndarray]]:
    """
    Given an .mtlx path returns baked textures as numpy array. The result will be wrapped in a dictionary
    with map names as keys and corresponding numpy arrays as values.
    """
    baker = MTLXBaker(mtlx_path)
    return baker.bake()

def bake_to_file(mtlx_path: Path, output_path: Path) -> List[Path]:
    baker = MTLXBaker(mtlx_path)
    file_names = []

    for graph, textures in baker.bake().items():
        out_file = output_path.joinpath(f"{mtlx_path.stem}_{graph}.exr")
        pyexr.write(out_file, textures)
        file_names.append(out_file)

    return file_names