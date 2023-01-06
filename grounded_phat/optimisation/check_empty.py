def check_empty(pipeline):
    def new_pipeline(G):
        return [] if G.number_of_edges() == 0 else pipeline(G)

    return new_pipeline
