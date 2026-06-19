Feature: Calculator

    Scenario: Add two numbers
        Given first number is <a>
        And second number is <b>
        When two numbers are added
        Then result should be <x>
        Examples:
            | a   | b  | x  |
            | 10  | 9  | 19 |
            | -10 | 4  | -6 |
            | 15  | -7 | 8  |