## ADDED Requirements

### Requirement: Matrix generator base
The system SHALL provide a `Matrix(rows, cols)` generator that produces a 2D matrix. The generator SHALL only accept `rows`, `cols`, and optionally `element` as core parameters; all other behavior SHALL be injected via decorators.

#### Scenario: Generate numeric matrix with default element
- **WHEN** user creates `Matrix(rows=3, cols=3)` without decorators
- **THEN** the result is a 3x3 matrix with default integer elements

#### Scenario: Generate matrix with custom element
- **WHEN** user creates `Matrix(rows=3, cols=3, element=Int(1, 100))`
- **THEN** the result is a 3x3 matrix where each cell is an integer from 1 to 100

### Requirement: Maze mode decorator
The system SHALL provide a `@as_maze(path, wall)` decorator that converts the matrix to a maze with specified symbols.

#### Scenario: Basic maze
- **WHEN** user applies `@as_maze(path='.', wall='#')`
- **THEN** the matrix contains only '.' and '#' characters

#### Scenario: Custom maze symbols
- **WHEN** user applies `@as_maze(path='0', wall='1')`
- **THEN** the matrix contains only '0' and '1' characters

### Requirement: Maze path guarantee decorator
The system SHALL provide a `@with_path_between(start, end)` decorator that guarantees a path exists between two coordinates in a maze.

#### Scenario: Guaranteed path
- **WHEN** user applies `@as_maze(path='.', wall='#')` and `@with_path_between((0,0), (9,9))`
- **THEN** the generated maze has a traversable path from (0,0) to (9,9) using '.' cells

#### Scenario: Invalid coordinates error
- **WHEN** user applies `@with_path_between((0,0), (100,100))` to a 10x10 matrix
- **THEN** the system raises a friendly error about coordinates exceeding matrix bounds

### Requirement: Border decorator
The system SHALL provide a `@with_border(symbol)` decorator that ensures the matrix edges use the specified symbol.

#### Scenario: Wall border
- **WHEN** user applies `@as_maze(path='.', wall='#')` and `@with_border('#')`
- **THEN** all cells on the matrix boundary are '#'

### Requirement: Coordinate constraint decorator
The system SHALL provide a `@with_coord_constraint(predicate)` decorator that enforces custom constraints on specific coordinates.

#### Scenario: Fixed cells
- **WHEN** user applies `@with_coord_constraint(lambda r, c: '.' if (r, c) in [(1,1), (2,2)] else None)`
- **THEN** cells (1,1) and (2,2) are guaranteed to be '.'

### Requirement: Row sum constraint decorator
The system SHALL provide a `@row_sum_max(value)` decorator that limits the sum of each row in a numeric matrix.

#### Scenario: Row sum limit
- **WHEN** user applies `@row_sum_max(100)` to a numeric matrix
- **THEN** the sum of each row does not exceed 100

### Requirement: Column sum constraint decorator
The system SHALL provide a `@col_sum_max(value)` decorator that limits the sum of each column in a numeric matrix.

#### Scenario: Column sum limit
- **WHEN** user applies `@col_sum_max(50)` to a numeric matrix
- **THEN** the sum of each column does not exceed 50

### Requirement: Row product constraint decorator
The system SHALL provide a `@row_product_max(value)` decorator that limits the product of each row.

#### Scenario: Row product limit
- **WHEN** user applies `@row_product_max(1000)` to a numeric matrix
- **THEN** the product of each row does not exceed 1000

### Requirement: Column product constraint decorator
The system SHALL provide a `@col_product_max(value)` decorator that limits the product of each column.

#### Scenario: Column product limit
- **WHEN** user applies `@col_product_max(500)` to a numeric matrix
- **THEN** the product of each column does not exceed 500

### Requirement: Custom operator constraint decorator
The system SHALL provide a `@with_row_operator(op, max_val)` and `@with_col_operator(op, max_val)` decorators for custom aggregate constraints.

#### Scenario: Custom row operator
- **WHEN** user applies `@with_row_operator(lambda cells: max(cells) - min(cells), 10)`
- **THEN** the difference between max and min in each row does not exceed 10

#### Scenario: Custom column operator
- **WHEN** user applies `@with_col_operator(lambda cells: sum(c**2 for c in cells), 500)`
- **THEN** the sum of squares in each column does not exceed 500

### Requirement: Decorator composition for matrix
The system SHALL allow multiple matrix decorators to be combined.

#### Scenario: Maze with border and path
- **WHEN** user applies `@as_maze`, `@with_border('#')`, and `@with_path_between((1,1), (8,8))`
- **THEN** the maze has walls on the border and a guaranteed internal path

#### Scenario: Numeric matrix with row and column constraints
- **WHEN** user applies `@row_sum_max(100)` and `@col_sum_max(50)`
- **THEN** both constraints are satisfied simultaneously
