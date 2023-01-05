
def _add_nodes(G, bd_data):
    for idx, node in enumerate(G.nodes):
        bd_data['columns'].append((0,  []))
        bd_data['times'].append(0)
        bd_data['idx_map'][node] = idx
    return bd_data

def _add_underlying_edges(G, bd_data):
    for i, j in G.edges:
        insertion_idx = len(bd_data['times'])
        bd_data['columns'].append((1, [ bd_data['idx_map'][i], bd_data['idx_map'][j] ]))
        bd_data['times'].append(0)
        bd_data['idx_map'][(i, j)] = insertion_idx
    return bd_data

def _add_filtration_edges(G, filtration, bd_data):
    for i in G.nodes:
        for j in G.nodes:
            if i == j:
                continue
            if G.has_edge(i, j):
                continue
            entrance_time = filtration((i, j))
            if entrance_time == np.inf:
                continue
            insertion_idx = len(bd_data['times'])
            bd_data['columns'].append((1, [ bd_data['idx_map'][i], bd_data['idx_map'][j] ]))
            bd_data['times'].append(entrance_time)
            bd_data['idx_map'][(i, j)] = insertion_idx
    return bd_data

# TODO: Don't add iji and jij
def _add_double_edges(G, filtration, bd_data):
    idx_map = bd_data['idx_map']
    for i in G.nodes:
        for j in G.nodes:
            if i == j:
                continue
            entrance_time = max(filtration((i, j)), filtration((j, i)))
            if entrance_time == np.inf:
                continue
            dimension = 2
            # d(iji) = ij + ji
            boundary = sorted([idx_map[(i, j)], idx_map[(j, i)]])
            bd_data['columns'].append((dimension, boundary))
            bd_data['times'].append(entrance_time)
    return bd_data

# TODO: Implement
def _add_eyeglasses(G, filtration, bd_data):
    return bd_data

# TODO: Re-implement to make use of output of djikstra
def _add_directed_triangles(G, filtration, bd_data):
    idx_map = bd_data['idx_map']
    for i in G.nodes:
        for k in G.nodes:
            if i==k:
                continue
            for j in G.nodes:
                if i == j or j == k:
                    continue
                entrance_time = max(filtration((i, j)), filtration((j, k)), filtration((i, k)))
                if entrance_time == np.inf:
                    continue
                print(f"Adding {i}, {j}, {k}")
                dimension = 2
                # d(ijk) = ij + jk + ik
                boundary = sorted([idx_map[(i, j)], idx_map[(j, k)], idx_map[(i, k)]])
                bd_data['columns'].append((dimension, boundary))
                bd_data['times'].append(entrance_time)
    return bd_data

# TODO: Re-implement to make use of output of djikstra
def _add_long_squares(G, filtration, bd_data):
    idx_map = bd_data['idx_map']
    for i in G.nodes:
        for k in G.nodes:
            if i==k:
                continue
            if G.has_edge(i, k):
                continue
            # The edge i->k appears at max_time
            # No point adding long squares if they appear after this
            # Since they can be written as differences of directed triangles
            max_time = filtration((i, k))
            bridges= []
            for j in G.nodes:
                if i == j or j == k:
                    continue
                this_time = max(filtration((i, j)), filtration((j, k)))
                if this_time >= max_time:
                    continue
                if this_time == np.inf:
                    continue
                bridges.append((j, this_time))
            # No long squares ever appear i->k
            if len(bridges) <= 1 :
                continue
            # So that we don't add linearly dependent long squares
            # We append the difference from the first arriving bridge to all the others
            bridges.sort(key=lambda b: b[1])
            first_bridge_node = bridges[0][0]
            for j in range(1,len(bridges)):
                dimension = 2
                # d(ijk) = ij + jk + ik
                second_bridge_node = bridges[j][0]
                boundary = sorted([idx_map[(i, first_bridge_node)], idx_map[(first_bridge_node, k)], 
                                   idx_map[(i, second_bridge_node)], idx_map[(second_bridge_node, k)]])
                bd_data['columns'].append((dimension, boundary))
                bd_data['times'].append(bridges[j][1])
    return bd_data

