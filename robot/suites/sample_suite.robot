*** Settings ***
Resource    robot/resources/keywords/generated/sample_keywords.resource
Metadata    generated_by    bdd-to-robot-pipeline
Metadata    source_feature    bdd/features/sample.feature

*** Variables ***
${USERNAME}    # TODO: set value
${PASSWORD}    # TODO: set value
${EXPECTED_ERROR}    # TODO: set value

*** Test Cases ***
Valid Login
    [Tags]    smoke    authentication    generated
    Go To Login Page
    Enter Username    ${USERNAME}
    Enter Password    ${PASSWORD}
    Click Login Button
    Verify Dashboard Is Displayed
    Verify Welcome Message Is Displayed

Invalid Login Attempts — admin
    [Tags]    generated
    Go To Login Page
    Enter Username    admin
    Enter Password    wrong
    Click Login Button
    Verify Error Message Is Displayed    Invalid credentials

Invalid Login Attempts
    [Tags]    generated
    Go To Login Page
    Enter Username
    Enter Password    secret
    Click Login Button
    Verify Error Message Is Displayed    Username required

Invalid Login Attempts — admin
    [Tags]    generated
    Go To Login Page
    Enter Username    admin
    Enter Password
    Click Login Button
    Verify Error Message Is Displayed    Password required
