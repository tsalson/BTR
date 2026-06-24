*** Settings ***
Resource    robot/resources/keywords/generated/sample_keywords.resource
Metadata    generated_by    bdd-to-robot-pipeline
Metadata    source_feature    bdd/features/sample.feature

*** Test Cases ***
Valid Login
    [Tags]    smoke    authentication    generated
    Open Login Page
    Enter Username
    Enter Password
    Click Login Button
    Verify Dashboard Is Displayed
    Verify Welcome Message Is Visible
Invalid Login Attempts — admin
    [Tags]    generated
    Open Login Page
    Enter Username
    Enter Password
    Click Login Button
    Verify Error Message Is Displayed
Invalid Login Attempts —
    [Tags]    generated
    Open Login Page
    Enter Username
    Enter Password
    Click Login Button
    Verify Error Message Is Displayed
Invalid Login Attempts — admin
    [Tags]    generated
    Open Login Page
    Enter Username
    Enter Password
    Click Login Button
    Verify Error Message Is Displayed
