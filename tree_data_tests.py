import tree_data


def print_size(self, level=0):
    ret = "\t" * level + str(self._root) + ' ' + str(self.data_size) + "\n"
    for child in self._subtrees:
        ret += child.print_size(level + 1)
    return ret

