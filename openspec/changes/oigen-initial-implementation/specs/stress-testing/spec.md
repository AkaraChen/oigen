## ADDED Requirements

### Requirement: Stress test runner
The system SHALL provide a `StressTest` class that compares outputs of two executables on generated data.

#### Scenario: Initialize stress test
- **WHEN** user creates `StressTest(workflow, std="./std", hack="./hack", output="./failures")`
- **THEN** a stress test runner is configured with the given parameters

### Requirement: Execute stress test loop
The system SHALL repeatedly generate data, run both executables, and compare outputs until stopped or a limit is reached.

#### Scenario: Run stress test with limit
- **WHEN** user calls `stress.run(max_iterations=1000)`
- **THEN** the system runs up to 1000 iterations, stopping early if hack found

#### Scenario: Run stress test until hack
- **WHEN** user calls `stress.run(until_hack=True)`
- **THEN** the system runs until a hack is found or interrupted

### Requirement: Compare executable outputs
The system SHALL compare stdout of std and hack executables. Outputs SHALL be compared after stripping trailing whitespace from each line.

#### Scenario: Outputs match
- **WHEN** std and hack produce identical output (after whitespace normalization)
- **THEN** the iteration is marked as passed

#### Scenario: Outputs differ
- **WHEN** std and hack produce different output
- **THEN** the iteration is marked as a hack (failure)

### Requirement: Save hack data
The system SHALL save input data that causes output differences to the specified output directory.

#### Scenario: Save failing input
- **WHEN** a hack is found
- **THEN** the input data is saved to `{output}/hack_{n}.in`

#### Scenario: Save both outputs
- **WHEN** a hack is found
- **THEN** both std output (`hack_{n}.std.out`) and hack output (`hack_{n}.hack.out`) are saved

### Requirement: Executable timeout
The system SHALL support configurable timeout for executable runs. Default timeout SHALL be 5 seconds.

#### Scenario: Executable exceeds timeout
- **WHEN** std or hack exceeds the timeout
- **THEN** the process is killed and the iteration is marked as timeout (not a hack)

#### Scenario: Custom timeout
- **WHEN** user specifies `timeout=10`
- **THEN** executables are allowed to run for up to 10 seconds

### Requirement: Runtime error handling
The system SHALL detect and handle runtime errors (non-zero exit codes) from executables.

#### Scenario: Std runtime error
- **WHEN** std returns non-zero exit code
- **THEN** the iteration is logged as std error and saved for inspection

#### Scenario: Hack runtime error
- **WHEN** hack returns non-zero exit code but std succeeds
- **THEN** the case is saved as a hack (runtime error counts as incorrect behavior)

### Requirement: Progress reporting
The system SHALL report progress during stress testing, including iterations completed, hacks found, and current rate.

#### Scenario: Show live progress
- **WHEN** stress test is running
- **THEN** terminal shows current iteration count and hack count

#### Scenario: Show summary on completion
- **WHEN** stress test completes
- **THEN** terminal shows total iterations, total hacks, and time elapsed

### Requirement: Stdin input format
The system SHALL write generated data to executable stdin in a format determined by the workflow's output formatter.

#### Scenario: Default text format
- **WHEN** workflow does not specify format
- **THEN** data is written as space-separated values with newlines

#### Scenario: Custom formatter
- **WHEN** workflow specifies a custom formatter function
- **THEN** the formatter is used to convert generated data to stdin text
