def convert_to_sparse(cols):
    sparse_cols = []
    col2idx_map = [{}, {}, {}]
    for col in cols:
        sparse_bdry = col.sparse_boundary(col2idx_map)
        insertion_idx = len(sparse_cols)
        sparse_cols.append(sparse_bdry)
        col2idx_map[col.dimension()][col] = insertion_idx
    return sparse_cols
