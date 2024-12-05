class UnbakeableGraphError(Exception):
    """ Raised when you try to bake a graph that has mesh-dependent nodes, like `position`. """