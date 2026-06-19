*** Settings ***
Resource    robot/resources/keywords/generated/calculator_keywords.resource
Metadata    generated_by    bdd-to-robot-pipeline
Metadata    source_feature    bdd/features/calculator.feature

*** Test Cases ***
Add Two Numbers — 10
    [Tags]    generated
    Given    first number is    10
    And    second number is    9
    When    two numbers are added
    Then    result should be    19

Add Two Numbers — -10
    [Tags]    generated
    Given    first number is    -10
    And    second number is    4
    When    two numbers are added
    Then    result should be    -6

Add Two Numbers — 15
    [Tags]    generated
    Given    first number is    15
    And    second number is    -7
    When    two numbers are added
    Then    result should be    8
