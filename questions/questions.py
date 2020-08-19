import nltk
import sys
import os
import string
import math

FILE_MATCHES = 4
SENTENCE_MATCHES = 2


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    file_contents = dict()

    # Iterate through directory
    for file in os.listdir(directory):

        # Read contents of file and map filename to file contents in dictionary
        with open(os.path.join(directory, file), encoding='utf8') as f:
            text = f.read()
            file_contents[file] = text

    return file_contents


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    lst = nltk.word_tokenize(document.lower())
    return[x for x in lst if x not in string.punctuation and x not in nltk.corpus.stopwords.words("english")]


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    vals = dict()

    # We need to ensure we only count each word once
    words = []
    for doc in documents:
        for word in documents[doc]:
            if word not in words:
                words.append(word)

    for word in words:

        # Keeps track of how many documents the current word appears in
        appearances = 0

        # Iterate through document and check if word appears in it
        for doc in documents:
            if word in documents[doc]:
                appearances += 1

        # Update dictionary with IDF value
        vals[word] = math.log(len(documents) / appearances)

    return vals


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # dictionary that maps file names to the sum of tf-idf values of words that appear in the query and the file
    vals = dict()

    query1 = set([x.lower() for x in query])

    for file in files:
        vals[file] = 0

    for word in query1:

        # Go through each file for each word in query
        for file in files:

            if word not in files[file]:
                continue

            # Calculate term frequency for current word
            tf = files[file].count(word)

            # Updating dict with the tf-idf value for this word
            vals[file] += tf * idfs[word]

    # Sort dict into list of file names by max tf-idf
    vals = sorted(vals, key=vals.get, reverse=True)

    res = []
    i = 0

    # Only return the n top files
    while len(res) != n:
        res.append(vals[i])
        i += 1

    return res


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    # This dict will map sentences to matching word measure
    vals = dict()

    # This dict will map sentences to query term density
    qtd = dict()

    query1 = set([x.lower() for x in query])

    for sentence in sentences:
        vals[sentence] = 0

    for word in query1:

        # Go through each sentence for each word in the query
        for sentence in sentences:

            # Query term density = number of common words between query and sentence / number of words in sentence
            proportion = len([x for x in sentences[sentence] if x in query1]) / len(sentences[sentence])

            # Update qtd dict
            qtd[sentence] = proportion

            if word not in sentences[sentence]:
                continue

            # Update values dict with idf value of this word
            vals[sentence] += idfs[word]

    # Sort dict into list of sentences by max matching word measure
    val_lst = sorted(vals, key=vals.get, reverse=True)

    res = []
    i = 0
    prev_val = val_lst[0]

    # Only return the n top sentences by matching word measure
    while len(res) != n:

        res.append(val_lst[i])

        # If the MWM values of current sentence and previous sentence are the same, then sort the two sentences by QTD
        if val_lst[i] != prev_val and vals[val_lst[i]] == vals[prev_val]:

            # If the current sentence has a higher QTD, swap it and previous sentence around
            if qtd[val_lst[i]] > qtd[prev_val]:
                res[-1], res[-2] = res[-2], res[-1]

        prev_val = val_lst[i]
        i += 1

    return res


if __name__ == "__main__":
    main()
