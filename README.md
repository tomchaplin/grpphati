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

Due to issues with the `pypi` packaging of `phat`, `grpphati` is currently not available as a `pypi` package.
Instead, please install as a direct reference to the repository:

```
$ pip install git+https://github.com/tomchaplin/grpphati.git
```

> **Warning**
> Some package managers (in particular `poetry`) will fail to build the `phat` dependency, since it uses the `setup.py install` build method.
> At the time of writing, installing as a direct reference with `hatch` is known to work.
> As a fallback, enter the shell of your virtual environment, and install via `pip`.

## Basic Usage

The quickest way to get started is to use the defeault implementation of GrPPH or GrPdFlH.
All descriptors implemented in `grpphati` expect a `networkx.DiGraph` as input with the edge-weights stored in the `weight` attribute.

```python
# test.py
from grpphati.pipelines import GrPPH, GrPdFlH
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

## Advanced Usage

### Filtrations

### Homology

## Contributing

## TODO

- [ ] Implement non-regular path homology
- [ ] Implement vertex-based and edge-based filtrations
- [ ] Improve performance of sparse matrix construction?
- [ ] Write test
- [ ] Choose benchmark datasets
- [ ] Benchmark different reductions
- [ ] Switch to and benchmark `bit_tree_pivot_column` representation
- [ ] Benchmark optimisations
- [ ] Type hints
- [ ] Test `_sparsify`; is it worthwhile to split the dictionaries on dimension?
- [ ] Write README and LICENSE
- [ ] Write `setup.py`
- [ ] Figure out problem with leaked objects

## References

<a id="1">[1]</a>
Chaplin, T., Harrington, H.A. and Tillmann, U., 2022.
Grounded persistent path homology: a stable, topological descriptor for weighted digraphs.
arXiv preprint [arXiv:2210.11274](https://arxiv.org/abs/2210.11274).

<a id="2">[2]</a>
Bauer, U., Kerber, M., Reininghaus, J. and Wagner, H., 2017.
Phat–persistent homology algorithms toolbox. Journal of symbolic computation, 78, pp.76-90.
github: [xoltar/phat](https://github.com/xoltar/phat)
