from grpphati.utils.graph import without_appendages


def remove_appendages(pipeline):
    def new_pipeline(G):
        smaller_G = without_appendages(G)
        return pipeline(smaller_G)

    return new_pipeline
