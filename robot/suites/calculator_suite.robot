*** Settings ***
Metadata    generated_by    bdd-to-robot-pipeline
Metadata    source_feature    bdd/features/calculator.feature

Library     BuiltIn
Resource    robot/resources/keywords/generated/calculator_keywords.resource


*** Variables ***
${A}    ${EMPTY}    # TODO: set value
${B}    ${EMPTY}    # TODO: set value
${X}    ${EMPTY}    # TODO: set value


*** Test Cases ***
Add Two Numbers — 10
    [Tags]    generated
    Set First Number    10
    Set Second Number    9
    Add Two Numbers
    Verify Result Is    19

Add Two Numbers — -10
    [Tags]    generated
    Set First Number    -10
    Set Second Number    4
    Add Two Numbers
    Verify Result Is    -6

Add Two Numbers — 15
    [Tags]    generated
    Set First Number    15
    Set Second Number    -7
    Add Two Numbers
    Verify Result Is    8
