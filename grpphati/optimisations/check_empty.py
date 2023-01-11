from grpphati.results import Result


def check_empty(pipeline):
    def new_pipeline(G):
        return Result.empty() if G.number_of_edges() == 0 else pipeline(G)

    return new_pipeline
