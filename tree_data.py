"""Assignment 2: Trees for Treemap

=== CSC148 Fall 2020 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""

from __future__ import annotations
import os
from random import randint
import math

from typing import Tuple, List, Optional

leafs = {}


class AbstractTree:
    """A tree that is compatible with the treemap visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you adding and implementing
    new public *methods* for this interface.

    === Public Attributes ===
    data_size: the total size of all leaves of this tree.
    colour: The RGB colour value of the root of this tree.
        Note: only the colours of leaves will influence what the user sees.

    === Private Attributes ===
    _root: the root value of this tree, or None if this tree is empty.
    _subtrees: the subtrees of this tree.
    _parent_tree: the parent tree of this tree; i.e., the tree that contains
        this tree
        as a subtree, or None if this tree is not part of a larger tree.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.
    - colour's elements are in the range 0-255.

    - If _root is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.
    - _subtrees IS allowed to contain empty subtrees (this makes deletion
      a bit easier).

    - if _parent_tree is not empty, then self is in _parent_tree._subtrees
    """
    data_size: int
    colour: (int, int, int)
    _root: Optional[object]
    _subtrees: List[AbstractTree]
    _parent_tree: Optional[AbstractTree]

    def __init__(self: AbstractTree, root: Optional[object],
                 subtrees: List[AbstractTree], data_size: int = 0) -> None:
        """Initialize a new AbstractTree.

        If <subtrees> is empty, <data_size> is used to initialize this tree's
        data_size. Otherwise, the <data_size> parameter is ignored, and this
        tree's data_size is computed from the data_sizes of the subtrees.

        If <subtrees> is not empty, <data_size> should not be specified.

        This method sets the _parent_tree attribute for each subtree to self.

        A random colour is chosen for this tree.

        Precondition: if <root> is None, then <subtrees> is empty.
        """
        self._root = root
        self._subtrees = subtrees
        self._parent_tree = None
        self.colour = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.data_size = 0
        if not self._subtrees:
            self.data_size = data_size
        else:
            for sub in self._subtrees:
                self.data_size += sub.data_size
                sub._parent_tree = self

    def __str__(self, level=0):
        ret = "\t" * level + str(self._root) + ' ' + str(self.data_size) + "\n"
        for child in self._subtrees:
            ret += child.__str__(level + 1)
        return ret

    def is_empty(self: AbstractTree) -> bool:
        """Return True if this tree is empty."""
        return self._root is None

    def generate_treemap(self: AbstractTree, rect: Tuple[int, int, int, int]) \
            -> List[Tuple[Tuple[int, int, int, int], Tuple[int, int, int]]]:
        """Run the treemap algorithm on this tree and return the rectangles.

        Each returned tuple contains a pygame rectangle and a colour:
        ((x, y, width, height), (r, g, b)).

        One tuple should be returned per non-empty leaf in this tree.

        @type self: AbstractTree
        @type rect: (int, int, int, int)
            Input is in the pygame format: (x, y, width, height)
        @rtype: list[((int, int, int, int), (int, int, int))]
        """
        output = []

        if self.data_size <= 0 or self.is_empty():
            return []
        elif not self._subtrees:
            leafs[self] = rect
            return [(rect, self.colour)]

        x, y, width, height = rect
        i = 0

        while i < len(self._subtrees):
            subtree = self._subtrees[i]

            if width > height:

                if i == len(self._subtrees) - 1:
                    new_width = abs(width - x)
                    output.extend(
                        subtree.generate_treemap((x, y, new_width, height)))
                else:
                    new_width = int(
                        (subtree.data_size / self.data_size) * width)
                    output.extend(
                        subtree.generate_treemap((x, y, new_width, height)))
                    x += new_width

            else:  # if height >= width

                if i == len(self._subtrees) - 1:
                    new_height = abs(height - y)
                    output.extend(
                        subtree.generate_treemap((x, y, width, new_height)))
                else:
                    new_height = int(
                        (subtree.data_size / self.data_size) * height)
                    output.extend(
                        subtree.generate_treemap((x, y, width, new_height)))
                    y += new_height

            i += 1
        return output

        # Read the handout carefully to help get started identifying base cases,
        # and the outline of a recursive step.
        #
        # Programming tip: use "tuple unpacking assignment" to easily extract
        # coordinates of a rectangle, as follows.
        # x, y, width, height = rect

    def get_separator(self: AbstractTree) -> str:
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        Used by the treemap visualiser to generate a string displaying
        the items from the root of the tree to the currently selected leaf.

        This should be overridden by each AbstractTree subclass, to customize
        how these items are separated for different data domains.
        """
        raise NotImplementedError

    def find_rect(self: AbstractTree, mouse_pos: Tuple) -> AbstractTree:
        """return the tree that corresponds to the rectangle that
        the mouse was clicked on"""
        x = mouse_pos[0]
        y = mouse_pos[1]
        for i in leafs:
            rec_x, rec_y, rec_w, rec_h = leafs[i]
            if rec_x <= x <= (rec_x + rec_w) and rec_y <= y <= (rec_y + rec_h):
                return i

    def get_path(self: AbstractTree) -> str:
        """return complete path of given tree"""
        path = ' '
        r_path = [self._root]
        x = self._parent_tree
        while x._parent_tree:
            r_path.append(x._root)
            x = x._parent_tree
        for i in r_path[::-1]:
            path += str(i) + self.get_separator()
        return path[:-3]

    def del_update_parents(self: AbstractTree) -> None:
        size = self.data_size
        x = self._parent_tree
        while x:
            x.data_size -= size
            x = x._parent_tree

    def delete_leaf(self: AbstractTree) -> None:
        """delete the specified leaf"""
        self._root = None
        self.data_size = 0

    def adjust_size(self: AbstractTree, case: bool) -> None:
        """Adjust the size of the specified leaf based on the case"""
        if case:
            new_size = (self.data_size * 0.01)
            self.data_size += new_size
            x = self._parent_tree
            while x:
                x.data_size += new_size
                x = x._parent_tree
        else:
            new_size = (self.data_size * 0.01)
            self.data_size -= new_size
            x = self._parent_tree
            while x:
                x.data_size -= new_size
                x = x._parent_tree


class FileSystemTree(AbstractTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _root attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/David/csc148/assignments'

    The data_size attribute for regular files as simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self: FileSystemTree, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """
        trees = []
        if os.path.isdir(path):
            trees = []
            size = 0
            for filename in os.listdir(path):
                subitem = os.path.join(path, filename)
                trees.append(FileSystemTree(subitem))
            for tree in trees:
                size += tree.data_size
            super().__init__(os.path.basename(path), trees, size)
        else:
            super().__init__(os.path.basename(path), [], os.path.getsize(path))

    def get_separator(self: AbstractTree) -> str:
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        Used by the treemap visualiser to generate a string displaying
        the items from the root of the tree to the currently selected leaf.
        """
        return " -> "


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(
        config={
            'extra-imports': ['os', 'random', 'math'],
            'generated-members': 'pygame.*'})
