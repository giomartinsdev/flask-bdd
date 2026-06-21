Feature: Employee area assignment with seeded areas

  Areas are inserted directly via the database (db_seed pattern) so the
  test setup does not depend on the area creation endpoint. Employees are
  still created through the API so the full hire flow is exercised.

  Background:
    Given the areas "Engineering" and "Operations" are seeded directly in the database

  Scenario: Assign an employee to a seeded area
    Given an employee exists with name "Alice" email "alice@corp.com" role "MID" salary 7000
    When I assign employee "alice@corp.com" to area "Engineering"
    Then the response status is 200
    And the employee area is "Engineering"

  Scenario: Reassign an employee between seeded areas
    Given an employee exists with name "Bob" email "bob@corp.com" role "SENIOR" salary 9000
    When I assign employee "bob@corp.com" to area "Engineering"
    And I assign employee "bob@corp.com" to area "Operations"
    Then the response status is 200
    And the employee area is "Operations"
    And employee "bob@corp.com" is confirmed in area "Operations" via GET

  Scenario: An employee can only belong to one area at a time
    Given an employee exists with name "Carol" email "carol@corp.com" role "MID" salary 7000
    When I assign employee "carol@corp.com" to area "Engineering"
    Then the employee area is "Engineering"
    When I assign employee "carol@corp.com" to area "Operations"
    Then the employee area is "Operations"
    And employee "carol@corp.com" is confirmed in area "Operations" via GET
