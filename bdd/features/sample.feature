Feature: User Login
    As a user
    I want to log in to the system
    So that I can access my account

    @smoke @authentication
    Scenario: Valid login
        Given I am on the login page
        When I enter username "admin"
        And I enter password "secret123"
        And I click the login button
        Then I see the dashboard
        And I see a welcome message

    Scenario Outline: Invalid login attempts
        Given I am on the login page
        When I enter username "<username>"
        And I enter password "<password>"
        And I click the login button
        Then I see an error message "<expected_error>"

        Examples:
            | username | password | expected_error      |
            | admin    | wrong    | Invalid credentials |
            |          | secret   | Username required   |
            | admin    |          | Password required   |