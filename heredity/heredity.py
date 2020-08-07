import csv
import itertools
import sys
import random
import numpy

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def has_parents(people, person):
    """
    Return boolean value describing whether a person's parents are documented in the csv
    """
    return people[person]['mother'] != None and people[person]['father'] != None


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    p = 0

    # List of probabilities for each person
    probabilities = []

    for person in people:

        if person in one_gene:
            gene_number = 1
        elif person in two_genes:
            gene_number = 2
        else:
            gene_number = 0

        if person in have_trait:
            trait = True
        else:
            trait = False

        # If person has no parents listed, take the probabilities from the PROBS dict
        if not has_parents(people, person):

            gene_prob = PROBS["gene"][gene_number]
            trait_prob = PROBS["trait"][gene_number][trait]

            probabilities.append(gene_prob * trait_prob)
            continue

        # If person has parents:
        # Getting parent's names
        mother = people[person]['mother']
        father = people[person]['father']

        # Number of target genes each parent has
        mother_gene = 1 if mother in one_gene else 2 if mother in two_genes else 0
        father_gene = 1 if father in one_gene else 2 if father in two_genes else 0

        # Mother has 0 copies of target gene
        if not mother_gene:
            mother_prob = PROBS["mutation"]

        # Mother has 1 copy
        elif mother_gene == 1:
            # 50/50 chance whether the target gene or the other gene will be passed down
            mother_prob = 0.5

        # father has 2 copies
        else:
            # Equal to 1 - mutation factor
            mother_prob = 1 - PROBS["mutation"]

        # father has 0 copies of target gene
        if not father_gene:
            father_prob = PROBS["mutation"]

            # father has 1 copy
        elif father_gene == 1:
            # 50/50 chance whether the target gene or the other copy will be passed down
            father_prob = 0.5

        # father has 2 copies
        else:
            # Equal to 1 - mutation factor
            father_prob = 1 - PROBS["mutation"]

        # ONE GENE: Either gets the gene from mother and not from father, or gets from father and not from mother
        if person in one_gene:
            # P(ChildGene = 1 | P(MotherGene), P(FatherGene))
            gene_prob = (mother_prob * (1 - father_prob)) + (father_prob * (1 - mother_prob))

        # TWO GENES: Person needs a target gene from both parents
        elif person in two_genes:
            # Probability of mother gene AND father gene
            gene_prob = (mother_prob * father_prob)

        # 0 GENES: Person needs to NOT get the gene from either their mother or their father
        else:
            # Probability of not mother gene and not father gene
            gene_prob = (1 - mother_prob) * (1 - father_prob)

        trait_prob = PROBS["trait"][gene_number][trait]

        probabilities.append(gene_prob * trait_prob)

    return numpy.prod(probabilities)


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:

        gene_number = 1 if person in one_gene else 2 if person in two_genes else 0
        trait = True if person in have_trait else False

        probabilities[person]["gene"][gene_number] += p
        probabilities[person]["trait"][trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:

        # Sum of all the probabilities of each gene number and trait number
        gene_sum = sum(probabilities[person]["gene"][x] for x in range(len(probabilities[person]["gene"])))
        trait_sum = probabilities[person]["trait"][True] + probabilities[person]["trait"][False]

        # What we need to multiply each gene/trait probability by to normalize them
        gene_multiplier = 1 / gene_sum
        trait_multiplier = 1 / trait_sum

        for gene in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene] *= gene_multiplier
        for trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][trait] *= trait_multiplier


if __name__ == "__main__":
    main()
