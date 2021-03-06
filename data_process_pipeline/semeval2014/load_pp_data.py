import ast
import pickle
from time import time

import operator

import h5py
import pandas as pd
import gensim
import numpy as np


def get_vocab(a, b):

    text_vocab = {}
    for x in a['text']:
        for word in x:
            if word in list(text_vocab.keys()):
                text_vocab[word] += 1
            else:
                text_vocab[word] = 1
    for x in b['text']:
        for word in x:
            if word in list(text_vocab.keys()):
                text_vocab[word] += 1
            else:
                text_vocab[word] = 1
    text_vocab = reversed(sorted(list(text_vocab.items()), key=operator.itemgetter(1)))
    aspect_vocab = {}
    for word in a['aspect']:
        if word == 'anecdotes/miscellaneous':
            word = 'miscellaneous'
        if word in list(aspect_vocab.keys()):
            aspect_vocab[word] += 1
        else:
            aspect_vocab[word] = 1

    for word in b['aspect']:
        if word == 'anecdotes/miscellaneous':
            word = 'miscellaneous'
        if word in list(aspect_vocab.keys()):
            aspect_vocab[word] += 1
        else:
            aspect_vocab[word] = 1

    aspect_vocab = reversed(sorted(list(aspect_vocab.items()), key=operator.itemgetter(1)))

    return list(text_vocab), list(aspect_vocab)


def get_vectors(text_vocab, aspect_vocab):
    text_skipped = 0
    aspect_skipped = 0
    st = time()
    # Load Google's pre-trained Word2Vec model.
    print('Loading Google News Word2Vec model')
    model = gensim.models.KeyedVectors.load_word2vec_format(
        '/home/gangeshwark/test_Google/GoogleNews-vectors-negative300.bin', binary=True)
    print(time() - st, " seconds to load the Google News vectors.")

    unk = np.random.uniform(-np.sqrt(3.0), np.sqrt(3.0), 300)
    pad = np.random.uniform(-np.sqrt(3.0), np.sqrt(3.0), 300)
    period = np.random.uniform(-np.sqrt(3.0), np.sqrt(3.0), 300)
    text_vector = {'__UNK__': unk, '__PAD__': pad, '.': period}
    for i, word in enumerate(text_vocab):
        if word[0] in list(text_vector.keys()):
            continue
        try:
            text_vector[word[0]] = model[word[0]]
        except:
            text_skipped += 1

    aspect_vector = {'__UNK__': unk}
    for i, word in enumerate(aspect_vocab):
        if word[0] in list(aspect_vector.keys()):
            continue
        try:
            aspect_vector[word[0]] = model[word[0]]
        except:
            aspect_skipped += 1

    print("Skipped %d words from text and %d words from aspects" % (text_skipped, aspect_skipped))
    return text_vector, aspect_vector


if __name__ == '__main__':

    text_vocab, aspect_vocab = get_vocab()
    print(text_vocab)
    print(len(text_vocab))
    # contains all the words
    with open('data/all_text_vocab.vocab', 'w') as f:
        for i, word in enumerate(text_vocab):
            f.write('%d\t%s\n' % (i, word[0]))

    print(aspect_vocab)
    print(len(aspect_vocab))
    with open('data/all_aspect_vocab.vocab', 'w') as f:
        for i, word in enumerate(aspect_vocab):
            f.write('%d\t%s\n' % (i, word[0]))

    text_vector, aspect_vector = get_vectors(text_vocab, aspect_vocab)

    # contains only the words that have embeddings
    with open('data/text_vocab.vocab', 'w') as f:
        for i, word in enumerate(text_vector.keys()):
            f.write('%d\t%s\n' % (i, word))

    with open('data/aspect_vocab.vocab', 'w') as f:
        for i, word in enumerate(aspect_vector.keys()):
            f.write('%d\t%s\n' % (i, word))

    print(len(text_vector), len(aspect_vector))
    with open('data/text_vector.pkl', 'wb') as f:
        pickle.dump(text_vector, f, protocol=pickle.HIGHEST_PROTOCOL)
    with open('data/aspect_vector.pkl', 'wb') as f:
        pickle.dump(aspect_vector, f, protocol=pickle.HIGHEST_PROTOCOL)

    h = h5py.File('data/text_vector.hdf5', 'w')
    for x in list(text_vector.keys()):
        h[x] = text_vector[x]
    h.close()

    h = h5py.File('data/aspect_vector.hdf5', 'w')
    for x in list(aspect_vector.keys()):
        h[x] = aspect_vector[x]
    h.close()
