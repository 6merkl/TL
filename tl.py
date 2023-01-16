import logging
from fractions import Fraction
from .diagram import Diagram

import tqdm
from itertools import product


class TL:
    """
    An Element of TL_n, i.e. a linear combiniation of diagrams.

    `n: int`
            The integer n in TL_n and in 'crossingles matching on 2n vertices'.

    `_diagrams`:
            A list of diagrams representing the linear combiniation.
    """

    n: int
    _diagrams: list

    def __init__(self, diagrams: list = [Diagram.id(2)]):
        # Some idiot testing
        if (not isinstance(diagrams, list) or
            not all(isinstance(diagram, Diagram) for diagram in diagrams) or
            not all(diagram.n == diagrams[0].n for diagram in diagrams) or
            not all(diagram.m == diagrams[0].m for diagram in diagrams)):

            raise ValueError(f"`diagrams` must be a non-empty list of diagrams of the same shape {diagrams}")

        # self.n = diagrams[0].n
        self._diagrams = diagrams

    def id(n):
        return TL([Diagram.id(n)])

    def U(n, i):
        return TL([Diagram.U(n, i)])

    def flip(self):
        newd = [x.flip() for x in self._diagrams]
        return TL(newd)

    def nestedCups(n):
        return TL([Diagram([(i,2*n-1-i) for i in range(n)],n = 2*n, m = 0)])

    def nestedCaps(n):
        return TL.nestedCups(n).flip()

    def empty():
        return TL([Diagram([],n = 0, m = 0)])

    def compose(self, tl):
        """
        This takes `self` and stacks it on top of `tl`.
        """

        return TL([a * b for a,b in product(self._diagrams,tl._diagrams)]).condense_diagrams()

    def tensor(self, tl):
        """
        This takes `self` and puts it to the left of `other`.
        """

        return TL([a & b for a in self._diagrams for b in tl._diagrams]).condense_diagrams()

    def condense_diagrams(self):
        diagrams = self._diagrams.copy()
        skip = len(diagrams)*[False]
        condensed_diagrams = []
        for i,diagram in enumerate(diagrams):
            if skip[i]:
                continue
            skip[i] = True
            for j,other in enumerate(diagrams[i:]):
                if skip[i+j]:
                    continue
                if diagram._has_same_diagram_as(other):
                    diagram += other
                    skip[i+j] = True

            if not diagram == 0:
                condensed_diagrams.append(diagram)

        return TL(condensed_diagrams)

    def __eq__(self, other):
        # self subset of other
        for diagram in self._diagrams:
            # Using `diagram in other._diagrams` is not possible
            if any(diagram == d for d in other._diagrams):
                continue
            else:
                logging.info(f"{repr(self)} is not euqal to {repr(other)} because of {repr(diagram)} in {repr(self)}")
                return False

        # self superset of other
        for diagram in other._diagrams:
            # Using `diagram in self._diagrams` is not possible
            if any(diagram == (d) for d in self._diagrams):
                continue
            else:
                logging.info(f"{repr(self)} is not euqal to {repr(other)} because of {repr(diagram)} in {repr(other)}")
                return False

        return True

    def __and__(self, other):
        return self.tensor(other)

    __matmul__ = __and__

    def __mul__(self, other):
        # TL * other
        # => other is TL
        return self.compose(other)

    def __rmul__(self, other):
        # other * TL
        # and other is not TL (because __mul__ wans't called)
        # => other is scalar
        return TL([other * diagram for diagram in self._diagrams])

    def __add__(self, other):
        # TL + other
        # => other is TL
        return TL(self._diagrams + other._diagrams).condense_diagrams()

    def __radd__(self, other):
        # other + TL
        # and other is not TL (because __add__ wasn't called)
        # => other is 0 (called by `sum`)
        return self

    def __repr__(self):
        return str(self._diagrams)

    def __str__(self):
        if len(self._diagrams) == 0:
            return "0"
        string = "\n"

        string += "\n +\n".join(str(diagram) for diagram in self._diagrams)

        return string + "\n"
