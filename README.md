<div align="center">

<img src="https://github.com/tomchaplin/grpphati/raw/main/docs/assets/logo.png" alt="Grpphati logo" width="300" role="img">

<h1>GrPPHATI</h1>

is a <b>Gr</b>ounded <b>P</b>ipeline <b>PHAT</b> <b>I</b>mplementation.

</div>

## Overview

The grounded pipeline, introduced in [[1]](#1), is a method for building stable, topological descriptors of weighted digraphs.
GrPPHATI is a Python library for implementing descriptors derived from this pipeline.
In particular, GrPPHATI provides default, optimised implementations of grounded persistent path homology (GrPPH) and grounded persistent directed flag complex homology (GrPdFlH).
GrPPHATI builds the boundary matrix in Python, converts it into a sparse format and then employs the persistent homology algorithm toolkit (PHAT) [[2]](#2) to perform the persistence calculation in C++.

> **Note**
> Due to its focus on GrPPH, this library only computes homology in degree 1.

## Installation

Due to [issues](https://github.com/xoltar/phat/issues/4) with the PyPI packaging of `phat`, GrPPHATI is currently not available as a PyPI package.
Instead, please install as a direct reference to the repository:

```
$ pip install git+https://github.com/tomchaplin/grpphati.git
```

> **Warning**
> Some package managers (in particular `poetry`) will fail to build the `phat` dependency, since it uses the `setup.py install` build method.
> At the time of writing, installing as a direct reference with `hatch` is known to work.
> As a fallback, enter the shell of your virtual environment, and install via `pip`.

## Basic Usage

The quickest way to get started is to use the default implementation of GrPPH or GrPdFlH.
All descriptors implemented in `grpphati` expect a `networkx.DiGraph` as input with the edge-weights stored in the `weight` attribute.

```python
# test.py
from grpphati.pipelines.grounded import GrPPH, GrPdFlH
import networkx as nx

G = nx.DiGraph()
G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)], weight = 3)
grpph_bar = GrPPH(G)
grpdflh_bar = GrPdFlH(G)

print(grpph_bar)
print(grpdflh_bar)
```
```
$ python test.py
[[0, 3]]
[[0, 6]]
```

### Optimisations

By default, all pipelines parallelise the computation over weakly connected components.

In addition, `GrPPH` iteratively removes appendage edges before starting the computation.
The pipeline `GrPdFlH` does not use this optimisation as it may result in a different barcode (e.g. [[Example A.13, 1]](#1)).

Thanks to [[Theorem 4.21, 1]](#1), it is possible to parallelise the computation of GrPPH over wedge components.
The pipeline `GrPPH_par_wedge` implements this optimisation.
If you expect that your input has a wedge decomposition, it is highly recommended to use this pipeline since it (a) parallelises the computation and (b) significantly reduces the number of allowed 2-paths.
For example, the following script computes the GrPPH of the wedge of two complete digraphs, each on 50 nodes.
The output is from a laptop with a Ryzen 5 3500U @2.1GHz.

```python
# test2.py
import networkx as nx
import time
from grpphati.pipelines.grounded import (
    GrPPH,
    GrPPH_par_wedge,
)


def timed(f):
    tic = time.time()
    output = f()
    toc = time.time()
    elapsed = toc - tic
    return (output, elapsed)


N = 50
G6_1 = nx.relabel_nodes(
    nx.complete_graph(50, create_using=nx.DiGraph), lambda x: (x, 1) if x > 0 else x
)
G6_2 = nx.relabel_nodes(
    nx.complete_graph(50, create_using=nx.DiGraph), lambda x: (x, 2) if x > 0 else x
)
G6 = nx.compose(G6_1, G6_2)
print(f"{G6.number_of_nodes()} nodes in wedge graph")

(out, elap) = timed(lambda: GrPPH(G6))
print("Serial:")
print(f"Size of barcode = {len(out)}")
print(f"Time elapsed = {elap}s")

print("Parallel over wedges:")
(out, elap) = timed(lambda: GrPPH_par_wedge(G6))
print(f"Size of barcode = {len(out)}")
print(f"Time elapsed = {elap}s")
```

```
$ python test2.py
99 nodes in wedge graph
Serial:
Size of barcode = 4802
Time elapsed = 10.496055603027344s
Parallel over wedges:
Size of barcode = 4802
Time elapsed = 2.702505111694336s
```

### Standard pipelines

For ease of comparison, we also provide implementations of the standard pipelines in `grpphati.pipelines.standard`.
The pipeline `PPH` combines path homology with the shortest-path filtration (`PPH_par_wedge` parallelises over wedges).
The pipeline `PdFlH` combines directed flag complex homology with the shortest-path filtration.

## Advanced Usage

GrPPHATI is in fact a library for implementing instances of the grounded pipeline.
The main interface for is the function `make_grounded_pipeline` in the `grpphati.pipelines.grounded` module.
The required arguments a filtration map and a homology class, which are explained further in the following sections.
Additionally, you can specify the persistence algorithm via a `phat.reductions` and provide an optimisation strategy.
The function returns a 'pipeline' which accepts a `nx.DiGraph` and returns the barcode.

The function `make_standard_pipeline` in `grpphati.pipelines.standard` has the same interface and returns the standard pipeline.

### Filtrations

A filtration map should except a `nx.DiGraph` and return a `grpphati.filtrations.Filtration`.
To specify a custom filtration, simply implement a subclass of `Filtration`, implementing all abstract methods.
The main methods describing the filtration are `node_iter` and `edge_iter` which return an iterator of `(node/edge, entrance_time)` tuples.
See the implementation of `ShortestPathFiltration` for an illustrative example.

Note, if `filtration` represents the filtration $t\mapsto F^t G$ then
`filtration.ground(G)` should return a `Filtration` representing the filtration $t\mapsto G \cup F^t G$.
A default implementation of this method is provided.
If $V(F^t G) \subseteq V(G)$ for all $t$ then `ProperGroundedFiltration` provides a more efficient iterator over nodes.

### Homology

To specify your homology theory, implement a subclass of `grpphati.homologies.Homology`.
The key methods to implement are the `get_<k>_cells(self, filtration)`.
For a given $k$, the method should return an iterator of columns in the boundary matrix.
For most digraph homology theories, you should only need to implement `get_two_cells`.

In order to implement your homology theory, you may need to implement new column types.
These column types should be subclasses of `grpphati.column.Column`.
A column object should encapsulate its `entrance_time`, as this will be needed for sorting the columns of the boundary matrix.
However, you should implement `__eq__` and `__hash__` so that columns representing the same basis are equal, regardless of entrance time.
This allows `convert_to_sparse` to lookup the index of each column when sparsifying the boundary matrix.

### Optimisations

An optimisation should accept a pipeline (as constructed via `make_grounded_pipeline`) and return a new pipeline, implementing the optimisation.
For illustrative examples, see the contents of `grpphati.optimisations`.

## TODO

- [ ] Implement non-regular path homology
- [ ] Improve performance of sparse matrix construction?
- [ ] Write tests
- [ ] Choose benchmark datasets
- [ ] Benchmark different reductions
- [ ] Switch to and benchmark `bit_tree_pivot_column` representation
- [ ] Benchmark optimisations
- [ ] Add type hints
- [ ] Add docstrings
- [ ] Test `_sparsify`; is it worthwhile to split the dictionaries on dimension?
- [ ] Figure out problem with leaked objects
- [ ] Separate out entrance times?

## References

<a id="1">[1]</a>
Chaplin, T., Harrington, H.A. and Tillmann, U., 2022.
Grounded persistent path homology: a stable, topological descriptor for weighted digraphs.
arXiv preprint [arXiv:2210.11274](https://arxiv.org/abs/2210.11274).

<a id="2">[2]</a>
Bauer, U., Kerber, M., Reininghaus, J. and Wagner, H., 2017.
Phat–persistent homology algorithms toolbox. Journal of symbolic computation, 78, pp.76-90.
github: [xoltar/phat](https://github.com/xoltar/phat)
