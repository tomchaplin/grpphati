<div align="center">

<img src="https://github.com/tomchaplin/grpphati/raw/main/docs/assets/logo.png" alt="Grpphati logo" width="300" role="img">

<h1>GrPPHATI</h1>

is a <b>Gr</b>ounded <b>P</b>ipeline Lo<b>PHAT</b> <b>I</b>mplementation.

[Overview](https://www.tomchaplin.xyz/research/2022-10-25-grounded-persistent-path-homology/)
•
[arXiv](https://arxiv.org/abs/2210.11274)
•
[Google Colab](https://colab.research.google.com/drive/1WUuiShZcXGb8n8kxjIoRcybYEM5av31O?usp=sharing)
   
</div>

## Overview

The grounded pipeline, introduced in [[1]](#1), is a method for building stable, topological descriptors of weighted digraphs.
GrPPHATI is a Python library for implementing descriptors derived from this pipeline.
In particular, GrPPHATI provides default, optimised implementations of grounded persistent path homology (GrPPH) and grounded persistent directed flag complex homology (GrPdFlH).
GrPPHATI builds the boundary matrix in Python, converts it into a sparse format and then employs [LoPHAT](https://github.com/tomchaplin/lophat) to perform the persistence calculation in Rust.

> **Note**
> Due to its focus on GrPPH, this library only computes homology in degree 1.

## Installation

To get started straight away, save a copy of [this Google Colab notebook](https://colab.research.google.com/drive/1WUuiShZcXGb8n8kxjIoRcybYEM5av31O?usp=sharing) to your drive.

To install, simply run

```shell
pip install grpphati
```


## Basic Usage

The quickest way to get started is to use the default implementation of GrPPH or GrPdFlH.
All descriptors implemented in `grpphati` expect a `networkx.DiGraph` as input with the edge-weights stored in the `weight` attribute.

```python
# examples/readme_1.py
from grpphati.pipelines.grounded import GrPPH, GrPdFlH
import networkx as nx

G = nx.DiGraph()
G.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 3)], weight=3)
grpph_bar = GrPPH(G).barcode
grpdflh_bar = GrPdFlH(G).barcode

print(grpph_bar)
print(grpdflh_bar)
```
```
$ python example/readme_1.py
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
# examples/readme_2.py
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
G_1 = nx.relabel_nodes(
    nx.complete_graph(N, create_using=nx.DiGraph), lambda x: (x, 1) if x > 0 else x
)
G_2 = nx.relabel_nodes(
    nx.complete_graph(N, create_using=nx.DiGraph), lambda x: (x, 2) if x > 0 else x
)
G_wedge = nx.compose(G_1, G_2)
print(f"{G_wedge.number_of_nodes()} nodes in wedge graph")

(out, elap) = timed(lambda: GrPPH(G_wedge))
print("Serial:")
print(f"Size of barcode = {len(out.barcode)}")
print(f"Time elapsed = {elap}s")

print("Parallel over wedges:")
(out, elap) = timed(lambda: GrPPH_par_wedge(G_wedge))
print(f"Size of barcode = {len(out.barcode)}")
print(f"Time elapsed = {elap}s")
```

```
$ python examples/readme_2.py
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

### grpphati_rs

If you are computing GrPPH on large networks, consider using [`grpphati_rs`](https://github.com/tomchaplin/grpphati_rs), which computes the basis of the boundary matrix in parallel, in Rust.

## Advanced Usage

GrPPHATI is in fact a library for implementing instances of the grounded pipeline.
The main interface for is the function `make_grounded_pipeline` in the `grpphati.pipelines.grounded` module.
The required arguments a filtration map and a homology class, which are explained further in the following sections.
Additionally, you can specify the PH backend and provide an optimisation strategy.
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

### Backends

By default, GrPPHATI uses LoPHAT to do the core persistence computation.
An alternative backend, relying on Eirene.jl [[3]](#3) is also provided.
Here is a rough guide to setting this up:

1. Install Julia 1.6 [(needed for Eirene compatibility)](https://github.com/Eetion/Eirene.jl/issues/47). In the following assume the binary for Julia 1.6 is at `/path/to/julia` - it is important that the filename is `julia`.
2. Install `grpphati` with the optional `[eirene]` feature flag, ideally in a virtual environment.
3. Install PyCall for Julia from within your virtual environment, e.g. if using `hatch`
```
$ hatch run python
>>> import julia
>>> julia.install(julia="/path/to/julia")
```
4. Make your own pipelines via the `make_grounded_pipeline` interface, using the `EireneBackend`. For example:

```python
# examples/eirene_simple_ex.py
import networkx as nx
from grpphati.pipelines.grounded import make_grounded_pipeline
from grpphati.homologies import RegularPathHomology
from grpphati.filtrations import ShortestPathFiltration
from grpphati.backends import EireneBackend
from grpphati.optimisations import all_optimisations_serial
from pprint import pprint

pipe = make_grounded_pipeline(
    ShortestPathFiltration,
    RegularPathHomology,
    backend=EireneBackend(
        runtime_path="/path/to/julia"
    ),
    optimisation_strat=all_optimisations_serial,
)

G = nx.DiGraph()
G.add_edges_from(
    [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (5, 6), (6, 3, {"weight": 10})]
)
result = pipe(G)
print(result.barcode)
pprint(result.reps)
```
```
$ python examples/eirene_simple_ex.py
[[0.0, 1.0], [0.0, 10.0]]
[[Edge (0, 2) :: 0, Edge (0, 1) :: 0, Edge (1, 3) :: 0, Edge (2, 3) :: 0],
 [Edge (5, 6) :: 0, Edge (4, 5) :: 0, Edge (3, 4) :: 0, Edge (6, 3) :: 0]]
```

> **Warning**
> Julia code [cannot be called in parallel](https://pyjulia.readthedocs.io/en/latest/limitations.html) via PyJulia.
> As such, the parallel optimisations should not be used without setting `n_jobs=1`.

When using `EireneBackend` you may notice it takes a while for the backend to initialise.
This is because `Julia` has to boot up and compile Eirene.
To speed this up, you can additionally provide `EireneBackend` with a `sysimage`.
This image should have Eirene pre-compiled and the necessary bootstrapping for compatibility with PyJulia.
To build such a system image:

1. Clone this repository and install `hatch`.
2. Install [juliaup](https://github.com/JuliaLang/juliaup).
3. Move into the `scripts` directory and run `./build_so.sh`.
4. The system image is now in the root of the project, named `patched_sys.so`.

See `examples/eirene_ex.py` for example usage

## TODO

- [ ] Implement non-regular path homology
- [ ] Improve performance of sparse matrix construction?
- [ ] Write unit tests
- [ ] Choose benchmark datasets
- [ ] Benchmark different reductions
- [ ] Switch to and benchmark `bit_tree_pivot_column` representation
- [ ] Benchmark optimisations
- [ ] Expand hypothesis test coverage - test combinations of backends + optimisations
- [ ] Add type hints
- [ ] Add docstrings
- [ ] Separate out entrance times?
- [ ] Rephrase optimisations with decorators?
- [ ] Benchmark Eirene vs PHAT
- [ ] Setup Eirene notebook
- [ ] Update to latest LoPHAT version

## References

<a id="1">[1]</a>
Chaplin, T., Harrington, H.A. and Tillmann, U., 2022.
Grounded persistent path homology: a stable, topological descriptor for weighted digraphs.
arXiv preprint [arXiv:2210.11274](https://arxiv.org/abs/2210.11274).

<a id="2">[2]</a>
Bauer, U., Kerber, M., Reininghaus, J. and Wagner, H., 2017.
Phat–persistent homology algorithms toolbox. Journal of symbolic computation, 78, pp.76-90.
github: [xoltar/phat](https://github.com/xoltar/phat)

<a id="3">[3]</a>
Henselman, G. and Ghrist, R., 2016.
Matroid filtrations and computational persistent homology.
arXiv preprint [arXiv:1606.00199](https://arxiv.org/abs/1606.00199).
github: [Eetion/Eirene.jl](https://github.com/Eetion/Eirene.jl)
