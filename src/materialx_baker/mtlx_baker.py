import MaterialX as mx
import numpy as np

from warnings import warn
from tqdm import tqdm
from pathlib import Path
from typing import Dict, Tuple
from .exceptions import UnbakeableGraphError
from collections import deque
from perlin_numpy import generate_fractal_noise_3d
from functools import cache

# This line of code saved 4s (almost halved the execution time) with just 2 calls to generate_fractal_noise_3d()
# in the test suite (2 at the time of writing this comment). Makes sense since generate_fractal_noise_3d() is the only
# computation heavy function.
generate_fractal_noise_3d = cache(generate_fractal_noise_3d)

class MTLXBaker:
    def __init__(self, mtlx_path: Path, resolution: Tuple[int, int] = (1024, 1024)) -> None:
        self.doc = mx.createDocument()
        mx.readFromXmlFile(self.doc, str(mtlx_path))
        self.resolution = resolution

    def bake(self, verbose: bool = False) -> Dict[str, Dict[str, np.ndarray]]:
        node_graphs = self.doc.getNodeGraphs()
        baked_textures = {}

        iterator = tqdm(node_graphs) if verbose else node_graphs
        for graph in iterator:
            try:
                baked_textures[graph.getName()] = self.bake_single_node_graph(graph)
            except UnbakeableGraphError as e:
                warn(f"Baking {graph} graph failed with error: {e}.")

        return baked_textures

    @staticmethod
    def _get_value(node: mx.Node, input_nodes: Dict[str, np.ndarray]) -> np.ndarray:
        if node.getInterfaceName() != "":
            return input_nodes[node.getInterfaceName()]

        if node.getNodeName() != "":
            return input_nodes[node.getNodeName()]

        return np.array(node.getValue())

    def _perform_operation(self, node: mx.Node, input_nodes: Dict[str, np.ndarray]) -> np.ndarray:
        inputs = [self._get_value(child, input_nodes) for child in node.getChildren()]

        match node.getCategory():
            case "dotproduct":
                return np.dot(*inputs)
            case "multiply":
                return np.multiply(*inputs)
            case "fractal3d":
                match node.getType():
                    case "vector2":
                        dims = 2
                    case "vector3":
                        dims = 3
                    case "vector4":
                        dims = 4
                    case _:
                        dims = 1

                # TODO use input parameters and make sure that they are called according to MaterialX specification.
                amplitude = 1.0
                octaves = 3
                lacunarity = 2
                diminish = 0.5
                noise = generate_fractal_noise_3d(
                    (self.resolution[0], self.resolution[1], 4),
                    (self.resolution[0] // 32, self.resolution[1] // 32, 1),
                    octaves=octaves,
                    persistence=diminish,
                    lacunarity=lacunarity
                )[:, :, :dims].squeeze()

                noise -= noise.min()
                return amplitude * noise
            case "add":
                return np.add(*inputs)
            case "power":
                return np.power(*inputs)
            case "mix":
                assert len(inputs) == 3, "mix takes exactly 2 inputs."
                in1 = inputs[0]
                in2 = inputs[1]
                mix_factor = inputs[2]
                first_part = np.kron(mix_factor, in1).reshape(mix_factor.shape + in1.shape)
                second_part = np.kron(1 - mix_factor, in2).reshape(mix_factor.shape + in2.shape)
                return first_part + second_part
            case "sin":
                return np.sin(*inputs)
            case "output":
                return input_nodes[node.getNodeName()]
            case _:
                raise UnbakeableGraphError(f"Unsupported node category {node.getCategory()}.")

    def bake_single_node_graph(self, graph: mx.NodeGraph) -> Dict[str, np.ndarray]:
        input_nodes = {}
        output_nodes = []
        complex_nodes = deque()

        for node in graph.getChildren():
            match type(node):
                case mx.Input:
                    input_nodes[node.getName()] = np.array(node.getValue())
                case mx.Output:
                    output_nodes.append(node)
                case mx.Node:
                    complex_nodes.append(node)
                case _:
                    error_message = f"Unsupported node type: {type(node)}. Only mesh-independent nodes are supported"
                    raise UnbakeableGraphError(error_message)

        while len(complex_nodes) > 0:
            node = complex_nodes.pop()
            children = [child.getConnectedNode() for child in node.getChildren() if child.getConnectedNode()]

            if any(input.getName() not in input_nodes for input in children):
                complex_nodes.appendleft(node)
                continue

            input_nodes[node.getName()] = self._perform_operation(node, input_nodes)

        return {node.getName(): self._perform_operation(node, input_nodes) for node in output_nodes}
