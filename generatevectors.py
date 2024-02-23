import torchtext

def create_embeddings():
    return torchtext.vocab.GloVe(name="6B", # trained on Wikipedia 2014 corpus
                                 dim=300)    # embedding size = 50
    
glove = create_embeddings()