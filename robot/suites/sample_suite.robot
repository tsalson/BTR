*** Settings ***
Metadata    generated_by    bdd-to-robot-pipeline
Metadata    source_feature    bdd/features/sample.feature

Resource    robot/resources/keywords/generated/sample_keywords.resource


*** Variables ***
${USERNAME}     ${EMPTY}    # TODO: set value
${PASSWORD}     ${EMPTY}    # TODO: set value


*** Test Cases ***
Valid Login
    [Tags]    generated
    Open Login Page
    Enter Username    ${USERNAME}
    Enter Password    ${PASSWORD}
    Click Login Button
    Verify Dashboard Is Displayed
    Verify Welcome Message Is Visible

Invalid Login Attempts — admin (1)
    [Tags]    generated
    Open Login Page
    Enter Username    admin
    Enter Password    wrong
    Click Login Button
    Verify Error Message Is Displayed    Invalid credentials

Invalid Login Attempts —    [Tags]    generated
    (2)
    Open Login Page
    Enter Username
    Enter Password    secret
    Click Login Button
    Verify Error Message Is Displayed    Username required

Invalid Login Attempts — admin (3)
    [Tags]    generated
    Open Login Page
    Enter Username    admin
    Enter Password
    Click Login Button
    Verify Error Message Is Displayed    Password required
