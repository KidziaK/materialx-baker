# materialx-baker

## Description
A small library for baking textures from .mtlx files. Given an .mtlx it produces a series of .exr files, one for each node graph inside the file.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Limitations](#limitations)
- [License](#license)

## Features
- Baking textures to numpy arrays for in memory usage.
- Baking textures to .exr files.

## Prerequisites
- python3.11+
- (optional) uv - https://docs.astral.sh/uv/ (for building from source)

## Installation
Use pre-build wheel on PYPI.
`pip install materialx_baker`

Or clone the repository and use uv.
### On linux
```
git clone https://github.com/KidziaK/materialx-baker
cd materialx-baker
uv pip install .
```

## Usage
The main API is very simple and consists of 2 functions: `bake_to_numpy(mtlx_path)` and `bake_to_file(mtlx_path, output_path)`.
As the names suggest, the first one will output the dictionary of N-dictionaries (where N is the number of node graphs inside the .mtlx).
Each inner dictionary is a key-value pair, where `key` is the name of the output for the given graph and `value` is the 
numpy array holding a texture.

```python
from materialx_baker import bake_to_numpy
from pathlib import Path

mtlx_path = Path("path_to_mtlx.mtlx")

textures = bake_to_numpy(mtlx_path)

for graph, tex in textures.items():
    ...
```


The second function `bake_to_file()` produces N .exr files with the appropriate textures.

```python
from materialx_baker import bake_to_file
from pathlib import Path

mtlx_path = Path("path_to_mtlx.mtlx")
output_path = Path("output_dir/")

bake_to_file(mtlx_path, output_path)  # <mtlx_name>_<graph_name>.mtlx
```

If you need custom logic for parsing, validating or controlling docs and graphs, you can import and use MTLXBaker class, 
however it is not recommended.

## Testing
```bash
# Using pytest
pytest src/
```

## Limitations
* Only works for geometry independent graphs. Geometry nodes like `position` will cause an error.
* Lacks support for certain nodes. These will be added in later versions.
* Output only support .exr. I'm not planning on adding other formats in the future.
* This is not a production ready project and requires some polishing. Use at your own risk.

## License
The MIT License (MIT) - see `LICENSE.txt`
