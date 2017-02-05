assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'


def cross(a, b):
    return [s + t for s in a for t in b]

diags = [[rows[i]+cols[i] for i in range(9)], [rows[i]+cols[::-1][i] for i in range(9)]]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]

column_units = [cross(rows, c) for c in cols]

square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]

unit_list = row_units + column_units + square_units

units = dict((s, [u for u in unit_list if s in u]) for s in boxes)

peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def assign_value(values_board, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values_board[box] = value
    if len(value) == 1:
        assignments.append(values_board.copy())
    return values_board


def naked_twins(values_board):
    """Eliminate values using the naked twins strategy.
    Args:
        values_board(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for box in values_board:
        for unit in units[box]:

            for peer in set(unit).difference(set({box})):

                if len(values_board[box]) == 2 and values_board[peer] == values_board[box]:
                    digit0 = values_board[box][0]
                    digit1 = values_board[box][1]
                    for square in set(unit).difference(set([box, peer])):
                        if digit0 in values_board[square]:
                            values_board = assign_value(values_board, square, values_board[square].replace(digit0, ''))
                        if digit1 in values_board[square]:
                            values_board = assign_value(values_board, square, values_board[square].replace(digit1, ''))

    return values_board


def grid_values(grid):
    """Convert grid string into {<box>: <value>} dict with '123456789' value for empties.

    Args:
        grid: Sudoku grid in string form, 81 characters long
    Returns:
        Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '123456789' if it is empty.
    """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(values) == 81
    return dict(zip(boxes, values))


def display(values_board):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1 + max(len(values_board[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values_board[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values_board):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values_board: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values_board.keys() if len(values_board[box]) == 1]
    for box in solved_values:
        digit = values_board[box]
        for peer in peers[box]:
            values_board[peer] = values_board[peer].replace(digit, '')
    return values_board


def only_choice(values_board):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    new_values = values_board.copy()  # note: do not modify original values

    for unit in unit_list:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values_board[box]]
            if len(dplaces) == 1:
                new_values[dplaces[0]] = digit
    return new_values


def fit_diag(values_board):
    for diag in diags:
        for box in diag:
            if len(values_board[box]) == 1:
                for diag_peer in set(diag).difference({box}):
                    if len(values_board[diag_peer]) > 1 and values_board[box] in values_board[diag_peer]:
                        item = values_board[box]
                        values_board[diag_peer] = values_board[diag_peer].replace(item, '')

    return values_board


def reduce_puzzle(values_board):
    # solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values_board.keys() if len(values_board[box]) == 1])

        values_board = fit_diag(values_board)
        values_board = eliminate(values_board)
        values_board = only_choice(values_board)
        values_board = naked_twins(values_board)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values_board.keys() if len(values_board[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values_board.keys() if len(values_board[box]) == 0]):
            return False
    return values_board


def search(values_board):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values_board = reduce_puzzle(values_board)
    if values_board is False:
        return False  # Failed earlier
    if all(len(values_board[s]) == 1 for s in boxes):
        return values_board  # Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values_board[s]), s) for s in boxes if len(values_board[s]) > 1)

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False),
    # return that answer!
    for value in values_board[s]:
        new_sudoku = values_board.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    values = reduce_puzzle(values)
    values = search(values)

    return values


if __name__ == '__main__':

    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    values = solve(diag_sudoku_grid)
    display(values)
    assignments.append(values)

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
