from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")



# Puzzle 0
# A says "I am both a knight and a knave." # A IS A KNAVE
knowledge0 = And(

    Or(AKnight, AKnave),
    Implication(AKnight, Not(AKnave)),
    Implication(AKnave, Not(AKnight)),

    Biconditional(AKnight, And(AKnight, AKnave))
)


# Puzzle 1
# A says "We are both knaves."     # A IS A KNAVE
# B says nothing.                  # B IS A KNIGHT
knowledge1 = And(

    Or(AKnight, AKnave),
    Implication(AKnight, Not(AKnave)),
    Implication(AKnave, Not(AKnight)),
    Or(BKnight, BKnave),
    Implication(BKnight, Not(BKnave)),
    Implication(BKnave, Not(BKnight)),

    Biconditional(AKnight, And(AKnave, BKnave)),

)

# Puzzle 2
# A says "We are the same kind."        # A IS A KNAVE
# B says "We are of different kinds."   # B IS A KNIGHT
knowledge2 = And(

    Or(AKnight, AKnave),
    Implication(AKnight, Not(AKnave)),
    Implication(AKnave, Not(AKnight)),
    Or(BKnight, BKnave),
    Implication(BKnight, Not(BKnave)),
    Implication(BKnave, Not(BKnight)),

    Biconditional(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    Biconditional(BKnight, Not(Or(And(AKnight, BKnight), And(AKnave, BKnave))))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.  # A can never say he is a knave  # A IS A KNIGHT
# B says "A said 'I am a knave'."                                               # B is a knave in every world    # B IS A KNAVE
# B says "C is a knave."
# C says "A is a knight."                                                       # C IS A KNIGHT
knowledge3 = And(
    Or(AKnight, AKnave),
    Implication(AKnight, Not(AKnave)),
    Implication(AKnave, Not(AKnight)),
    Or(BKnight, BKnave),
    Implication(BKnight, Not(BKnave)),
    Implication(BKnave, Not(BKnight)),
    Or(CKnight, CKnave),
    Implication(CKnight, Not(CKnave)),
    Implication(CKnave, Not(CKnight)),

    Biconditional(AKnight, And(CKnight, Or(AKnight,AKnave))),
    Biconditional(BKnight, And(CKnave, AKnight, AKnave)), # Contradiction
    Biconditional(CKnight, And(Or(AKnight, AKnave), BKnave))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
