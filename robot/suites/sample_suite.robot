*** Settings ***
Metadata    generated_by    bdd-to-robot-pipeline
Metadata    source_feature    bdd/features/sample.feature

Resource    ../resources/keywords/generated/sample_keywords.resource


*** Variables ***
${VALID_USERNAME}       ${EMPTY}    # TODO: set value
${VALID_PASSWORD}       ${EMPTY}    # TODO: set value


*** Test Cases ***
Valid Login
    [Tags]    smoke    authentication    generated
    Navigate To Login Page
    Enter Username    ${VALID_USERNAME}
    Enter Password    ${VALID_PASSWORD}
    Click Login Button
    Verify Dashboard Is Displayed
    Verify Welcome Message Is Displayed

Invalid Login Attempts — admin
    [Tags]    smoke    authentication    generated
    Navigate To Login Page
    Enter Username    admin
    Enter Password    wrong
    Click Login Button
    Verify Error Message Is Displayed    Invalid credentials

Invalid Login Attempts —
    [Tags]    smoke    authentication    generated
    Navigate To Login Page
    Enter Username
    Enter Password    secret
    Click Login Button
    Verify Error Message Is Displayed    Username required

Invalid Login Attempts — admin
    [Tags]    smoke    authentication    generated
    Navigate To Login Page
    Enter Username    admin
    Enter Password
    Click Login Button
    Verify Error Message Is Displayed    Password required
