## ADDED Requirements

### Requirement: String generator base
The system SHALL provide a `String(length)` generator that produces random strings. The generator SHALL only accept `length` as its core parameter; all other behavior SHALL be injected via decorators.

#### Scenario: Generate random string with default charset
- **WHEN** user creates `String(length=10)` without decorators
- **THEN** the result is a 10-character string using default lowercase letters

### Requirement: Charset decorator
The system SHALL provide a `@from_charset(chars)` decorator that specifies the character set for string generation.

#### Scenario: Custom charset
- **WHEN** user applies `@from_charset("ABC123")` to a String generator
- **THEN** the generated string only contains characters from "ABC123"

#### Scenario: Charset with special characters
- **WHEN** user applies `@from_charset("()[]{}.")` to a String generator
- **THEN** the generated string only contains the specified special characters

### Requirement: Template decorator
The system SHALL provide a `@from_template(pattern)` decorator where `*` represents any character from the charset.

#### Scenario: Template with wildcards
- **WHEN** user applies `@from_template("ab*cd*ef")` with charset "xyz"
- **THEN** the generated string matches pattern like "abxcdyef"

#### Scenario: Template with fixed positions
- **WHEN** user applies `@from_template("test_***")` with charset "0123456789"
- **THEN** the generated string is like "test_123" with exactly 3 random digits

### Requirement: Substring constraint decorator
The system SHALL provide a `@must_contain(substrings)` decorator that ensures the generated string contains all specified substrings.

#### Scenario: Single substring
- **WHEN** user applies `@must_contain(["abc"])`
- **THEN** the generated string contains "abc" as a substring

#### Scenario: Multiple substrings
- **WHEN** user applies `@must_contain(["foo", "bar"])`
- **THEN** the generated string contains both "foo" and "bar" as substrings

#### Scenario: Impossible constraint error
- **WHEN** user applies `@must_contain(["abcdef"])` to `String(length=3)`
- **THEN** the system raises a friendly error explaining the substring is longer than the string length

### Requirement: Trie words decorator
The system SHALL provide a `@as_trie_words(count, max_depth)` decorator that generates a set of strings suitable for building a Trie structure.

#### Scenario: Generate Trie word set
- **WHEN** user applies `@as_trie_words(count=10, max_depth=5)`
- **THEN** the result is a list of 10 strings, each with length at most 5

#### Scenario: Trie with shared prefixes
- **WHEN** user applies `@as_trie_words(count=10, max_depth=5, shared_prefix_prob=0.5)`
- **THEN** approximately half the words share a common prefix with another word

### Requirement: String length as range
The system SHALL support `length` as either a fixed integer or a tuple `(min, max)` for variable length.

#### Scenario: Variable length string
- **WHEN** user creates `String(length=(5, 10))`
- **THEN** the generated string has length between 5 and 10 inclusive

### Requirement: Decorator composition for strings
The system SHALL allow multiple string decorators to be combined, with constraints accumulated.

#### Scenario: Charset with substring constraint
- **WHEN** user applies both `@from_charset("abc")` and `@must_contain(["ab"])`
- **THEN** the generated string uses only "abc" and contains "ab"

#### Scenario: Conflicting decorators error
- **WHEN** user applies `@from_charset("xyz")` and `@must_contain(["abc"])`
- **THEN** the system raises a friendly error explaining the charset doesn't contain the required substring characters
