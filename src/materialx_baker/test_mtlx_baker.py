import unittest
import pytest

import MaterialX as mx

from .mtlx_baker import MTLXBaker
from .exceptions import UnbakeableGraphError
from pathlib import Path

class TestMtlxBakerInit(unittest.TestCase):
    def test_valid_mtlx(self) -> None:
        # GIVEN a path to a valid .mtlx file.
        mtlx_path = Path(__file__).parent.joinpath("test_data/blood_red.mtlx")

        # WHEN you create an instance of MTLXBaker.
        # THEN baker is successfully create.
        baker = MTLXBaker(mtlx_path)

    def test_invalid_mtlx(self) -> None:
        # GIVEN a path to a valid .mtlx file.
        mtlx_path = Path(__file__).parent.joinpath("test_data/invalid.mtlx")

        # WHEN you create an instance of MTLXBaker.
        # THEN MaterialX.PyMaterialXFormat.ExceptionParseError is raised.
        with pytest.raises(mx.PyMaterialXFormat.ExceptionParseError):
            baker = MTLXBaker(mtlx_path)


class TestMtlxBakerBakeSingleNodeGraph(unittest.TestCase):
    def setUp(self) -> MTLXBaker:
        mtlx_path = Path(__file__).parent.joinpath("test_data/marbel.mtlx")
        self.baker = MTLXBaker(mtlx_path)
        self.graphs = {graph.getName(): graph for graph in self.baker.doc.getNodeGraphs()}

    def test_bakeable_graph(self) -> None:
        # GIVEN a graph containing only non-mesh dependent nodes (bakeable).
        graph = self.graphs["NG_marble_mesh_independent"]

        # WHEN we bake this graph.
        textures = self.baker.bake_single_node_graph(graph)

        # THEN we get a dictionary of textures with a single key.
        assert len(textures) == 1

    def test_unbakeable_graph(self) -> None:
        # GIVEN a graph containing at least one mesh dependent node (unbakeable).
        graph = self.graphs["NG_marble_mesh_dependent"]

        # WHEN we try to bake this graph.
        # THEN UnbakeableGraph error is raised.
        with pytest.raises(UnbakeableGraphError):
            self.baker.bake_single_node_graph(graph)
