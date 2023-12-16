#!/usr/bin/env python
########################################################################
#
# day16_2.py
# Was written for AoC2023
#
########################################################################
import copy
import re
import sys
from typing import Dict, List, Sequence, Set, TextIO, Tuple, Union

########################################################################
# Initial data structures
########################################################################

# Data structures:

R: Tuple[int, int] = (1, 0)
L: Tuple[int, int] = (-1, 0)
U: Tuple[int, int] = (0, -1)
D: Tuple[int, int] = (0, 1)
# HINDSIGHT: The above should have been an enum class instance.

BOOL_INDEX: Dict[Tuple[int, int], int] = {
    R: 0,
    L: 1,
    U: 2,
    D: 3,
}
# HINDSIGHT: a proper enum class would have allowd me to index
# the tuple using int(R),int(L), etc.

# Transform (tile contents, entry direction) into
# List of next tile directions.
TRANSFORM: Dict[Tuple[str, Tuple[int, int]], List[Tuple[int, int]]] = {
    (".", R): [R],
    (".", L): [L],
    (".", U): [U],
    (".", D): [D],
    #
    ("/", R): [U],
    ("/", L): [D],
    ("/", U): [R],
    ("/", D): [L],
    #
    ("\\", R): [D],
    ("\\", L): [U],
    ("\\", U): [L],
    ("\\", D): [R],
    #
    ("|", R): [U, D],
    ("|", L): [U, D],
    ("|", U): [U],
    ("|", D): [D],
    #
    ("-", R): [R],
    ("-", L): [L],
    ("-", U): [R, L],
    ("-", D): [R, L],
}


########################################################################
# Functions
########################################################################


def legal_tile(contraption: List[str], next_tile: Tuple[int, int]) -> bool:
    """Check if the next_tile is inside the contraption."""
    if (next_tile[0] < 0) or (next_tile[0] >= len(contraption[0])):
        return False
    if (next_tile[1] < 0) or (next_tile[1] >= len(contraption)):
        return False
    return True


########################################################################
# BIG FUNCTION
########################################################################
def compute_energized_count(
    contraption: List[str], start: Tuple[Tuple[int, int], Tuple[int, int]]
) -> int:
    ########################################################################
    # Build the data structure for keeping track of energized tiles.
    # We maintain a separate flag for each direction.
    ########################################################################

    ########################################################################
    # Data structure description
    #
    # We want to record whether a beam alrady passed a tile in a certain
    # direction. This would allow us to skip further processing.
    #
    # Hence, a 2D array of 4-tuples.
    ########################################################################

    initial: Tuple[bool, bool, bool, bool] = (False, False, False, False)
    initial_row: List[Tuple[bool, bool, bool, bool]] = [
        copy.copy(initial) for _ in range(len(contraption[0]))
    ]
    energized: List[List[Tuple[bool, bool, bool, bool]]] = [
        copy.copy(initial_row) for _ in range(len(contraption))
    ]
    # HINDSIGHT: should have used Dict[(x,y)] instead of Dict[y][x],
    #     with defaultdict(lambda: (False, False, False, False))

    # sys.stdout.write(f"DEBUG Check Energized: {energized}\n")

    ########################################################################
    # Main loop
    ########################################################################

    queue: List[Tuple[Tuple[int, int], Tuple[int, int]]] = [start]

    # Each element in the queue describes the tile to be energized
    # and in which direction it got the beam.
    #
    # If the tile is already energized:
    #    we skip further processing.
    # Otherwise:
    #    we mark it as energized in the given direction and
    #    compute the coordinates and directions of the next 1-2 tiles.
    #    Each of the new tiles is appended to the queue unless:
    #    After marking it as energized, we append to the queue each of
    #    the next tile/s, unless:
    #        The next tile would have been outside the contraption.
    while len(queue) > 0:
        (tile, direction) = queue.pop(0)
        # sys.stdout.write(
        #    f"Inspecting {tile=}:{contraption[tile[1]][tile[0]]}, {direction=}\n"
        # )
        e_state: Tuple[bool, bool, bool, bool] = energized[tile[1]][tile[0]]
        # sys.stdout.write(
        #    f"DEBUG {direction=} BOOL_INDEX={BOOL_INDEX[direction]} energized={e_state}\n"
        # )
        is_already_energized: bool = e_state[BOOL_INDEX[direction]]
        if is_already_energized:
            # Beam already propagated in this direction.
            # sys.stdout.write("\t** already energized\n")
            continue
        e_state_list: List[bool] = list(e_state)
        e_state_list[BOOL_INDEX[direction]] = True
        energized[tile[1]][tile[0]] = tuple(e_state_list)  # type: ignore
        # HINDSIGHT: concatenating 3 tuple fragments may have been faster.
        # sys.stdout.write(f"\tDEBUG Updated Energized: {energized}\n")

        # Current tile is now energized in that direction.
        # Push next tile/s into queue.
        for next_direction in TRANSFORM[(contraption[tile[1]][tile[0]], direction)]:
            next_tile = (tile[0] + next_direction[0], tile[1] + next_direction[1])
            if legal_tile(contraption, next_tile):
                queue.append((next_tile, next_direction))
                # sys.stdout.write(
                #    f"\tAppended {next_tile=}, {next_direction=} to queue, which is now {len(queue)} items long\n"
                # )
            else:
                pass  # sys.stdout.write(f"\t** out of range {next_tile}\n")

    ########################################################################
    # Count energized tiles (regardless of directions).
    ########################################################################

    energized_count = 0
    for e_row in energized:
        for e_tile_state in e_row:
            if any(e_tile_state):
                energized_count += 1
    return energized_count


########################################################################
# Main code
########################################################################

if __name__ == "__main__":
    ########################################################################
    # Input data parsing
    ########################################################################

    contraption: List[str] = []

    for line in sys.stdin:
        sline = line.strip()
        contraption.append(sline)

    sys.stdout.write(
        f"DEBUG: contraption width={len(contraption[0])} height={len(contraption)}\n"
    )

    # Tuple[next tile coordinates,from which direction the beam enters it]
    startingpositions: List[Tuple[Tuple[int, int], Tuple[int, int]]] = (
        [((0, y), R) for y in range(len(contraption))]
        + [((len(contraption[0]) - 1, y), L) for y in range(len(contraption))]
        + [((x, 0), D) for x in range(len(contraption[0]))]
        + [((x, len(contraption) - 1), U) for x in range(len(contraption[0]))]
    )

    ########################################################################
    # Main loop
    ########################################################################

    energized_counts = [
        (starting, compute_energized_count(contraption, starting))
        for starting in startingpositions
    ]

    ########################################################################
    # Find maximum count of energized tiles.
    ########################################################################

    sys.stdout.write("\n\nSUMMARY\n\n")

    max_e_count = -1
    for starting, energized_count in energized_counts:
        sys.stdout.write(f"For {starting}: energized tiles: {energized_count}\n")
        if energized_count > max_e_count:
            max_e_count = energized_count
    # HINDSIGHT could use:
    #     max((something which computes and prints for each starting position))

    sys.stdout.write(f"\nMaximum energized: {max_e_count}\n")

else:
    pass

########################################################################
# End of day16_1.py
