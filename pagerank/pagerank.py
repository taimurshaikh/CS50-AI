import os
import random
from numpy.random import choice
import re
import sys
import math

DAMPING = 0.85
SAMPLES = 100000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # All pages in entire corpus
    all_pages = set(key for key in corpus.keys())

    # Set of pages that are reachable via this page
    linked_pages = corpus[page]

    # Dictionary we will populate with pages mapped to probabilites of that page being visited from current page
    res = dict()

    # If page has no outgoing links, return a distribution that has equal probability for all pages
    if not linked_pages:
        #print("No outgoing links")
        for page in all_pages:
            res[page] = 1 / len(all_pages)
        return res

    damping_factor_split = damping_factor / len(linked_pages)
    remainder = 1 - damping_factor
    remainder_split = remainder / len(all_pages)

    # Add a key value pair for every page in corpus
    for page in all_pages:
        page_value = 0

        # Every page gets an even split of 1 - damping_factor
        page_value += remainder_split

        # If page is a link on the current page, add an even split of the damping_factor
        if page in linked_pages:
            page_value += damping_factor_split

        # Adding key value pair to dict
        res[page] = page_value

    return res


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # All pages in entire corpus
    all_pages = [key for key in corpus.keys()]

    # Dictionary which will map each page to the number of generated samples that were the page
    counts = dict()
    for page in all_pages:
        counts[page] = 0

    # Choosing first sample randomly and updating counts dict
    first_sample = random.choice(all_pages)
    counts[first_sample] += 1

    for i in range(1, n):
        # If we are on the second sample, do the calculation based on the first
        if i == 1:
            prev_sample = first_sample

        distributions = transition_model(corpus, prev_sample, damping_factor)

        keys = [key for key in distributions.keys()]
        values = [distributions[key] for key in distributions.keys()]

        # Using random.choices to select an option given a list of weights (distribution)
        current_sample = random.choices(keys, weights=values, k=1)[0]

        # Updating counts dict given the current sample
        counts[current_sample] += 1

        prev_sample = current_sample

    # Modifying counts dict to represent the proportion of samples that corresponded to that page instead of the raw amount
    for page in all_pages:
        counts[page] /= n

    return counts


def get_links(corpus, page):
    """
    Return list of all pages in corpus that link to page
    """
    res = []
    for p in corpus:
        if page in corpus[p]:
            res.append(p)
    return res


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = dict()
    newrank = dict()

    for page in corpus:
        pagerank[page] = 1 / len(corpus)

    repeat = True

    while repeat:

        for page in pagerank:

            summation = 0

            links = get_links(corpus, page)

            if not links:
                for p in corpus:
                    summation += pagerank[p] / len(corpus)

            for link in links:
                summation += pagerank[link] / len(corpus[link])

            newrank[page] = (1 - damping_factor) / len(corpus) + damping_factor * summation

        repeat = False

        for page in pagerank:
            if abs(newrank[page] - pagerank[page]) > 0.001:
                repeat = True

            pagerank[page] = newrank[page]

    return pagerank


if __name__ == "__main__":
    main()
