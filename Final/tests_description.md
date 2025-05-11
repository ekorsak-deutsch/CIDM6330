# Unit Tests for Email Forwarding Rules Audit API

This document provides descriptions of the unit tests implemented for the Email Forwarding Rules Audit API. The tests are designed to ensure that all API endpoints function correctly and that the application meets its requirements.

## API Endpoint Tests

### ForwardingRuleAPITests

These tests focus on the core API endpoints for managing forwarding rules.

#### test_get_all_rules
- **Purpose**: Verify that the API correctly returns all forwarding rules
- **Endpoint**: GET /api/rules/
- **Expected Behavior**: Returns a 200 status code and a list of all forwarding rules with their details
- **Edge Cases**: None (basic functionality test)

**Gherkin:**
```gherkin
Feature: Retrieve forwarding rules
  Scenario: Get all rules
    Given there are multiple forwarding rules in the system
    When I send a GET request to "/api/rules/"
    Then the response status code should be 200
    And the response should contain a list of all forwarding rules
    And the details of each rule should be correct
```

#### test_get_specific_rule
- **Purpose**: Verify that the API correctly returns a specific forwarding rule by ID
- **Endpoint**: GET /api/rules/{rule_id}
- **Expected Behavior**: Returns a 200 status code and the details of the requested rule
- **Edge Cases**: Returns a 404 status code when requesting a non-existent rule

**Gherkin:**
```gherkin
Feature: Retrieve specific forwarding rule
  Scenario: Get existing rule
    Given there is a forwarding rule with ID 1 in the system
    When I send a GET request to "/api/rules/1"
    Then the response status code should be 200
    And the response should contain the details of rule 1
    
  Scenario: Get non-existent rule
    Given there is no forwarding rule with ID 999 in the system
    When I send a GET request to "/api/rules/999"
    Then the response status code should be 404
```

#### test_update_investigation_note
- **Purpose**: Verify that the API correctly updates the investigation note for a forwarding rule
- **Endpoint**: PUT /api/rules/{rule_id}/investigation
- **Expected Behavior**: Returns a 200 status code and the updated rule with the new investigation note
- **Edge Cases**: Returns a 404 status code when updating a non-existent rule

**Gherkin:**
```gherkin
Feature: Update rule investigation note
  Scenario: Update note for existing rule
    Given there is a forwarding rule with ID 1 in the system
    When I send a PUT request to "/api/rules/1/investigation" with an updated note
    Then the response status code should be 200
    And the rule should be updated with the new investigation note
    
  Scenario: Update note for non-existent rule
    Given there is no forwarding rule with ID 999 in the system
    When I send a PUT request to "/api/rules/999/investigation" with an updated note
    Then the response status code should be 404
```

#### test_delete_rule
- **Purpose**: Verify that the API correctly deletes a forwarding rule
- **Endpoint**: DELETE /api/rules/{rule_id}
- **Expected Behavior**: Returns a 204 status code and removes the rule from the database
- **Edge Cases**: Returns a 404 status code when deleting a non-existent rule

**Gherkin:**
```gherkin
Feature: Delete forwarding rule
  Scenario: Delete existing rule
    Given there is a forwarding rule with ID 2 in the system
    When I send a DELETE request to "/api/rules/2"
    Then the response status code should be 204
    And the rule should be removed from the database
    
  Scenario: Delete non-existent rule
    Given there is no forwarding rule with ID 999 in the system
    When I send a DELETE request to "/api/rules/999"
    Then the response status code should be 404
```

#### test_search_rules
- **Purpose**: Verify that the API correctly searches for forwarding rules based on criteria
- **Endpoint**: GET /api/rules/search/
- **Expected Behavior**: Returns a 200 status code and a list of rules matching the search criteria
- **Edge Cases**: Returns an empty list when no rules match the criteria

**Gherkin:**
```gherkin
Feature: Search forwarding rules
  Scenario: Search by email
    Given there are multiple forwarding rules in the system
    When I send a GET request to "/api/rules/search/?email=user1"
    Then the response status code should be 200
    And the response should contain rules matching the email criteria
    
  Scenario: Search by filter presence
    Given there are multiple forwarding rules in the system
    When I send a GET request to "/api/rules/search/?has_filters=true"
    Then the response status code should be 200
    And the response should contain only rules that have filters
    
  Scenario: Search with no matches
    Given there are multiple forwarding rules in the system
    When I send a GET request to "/api/rules/search/?email=nonexistent"
    Then the response status code should be 200
    And the response should contain an empty list
```

#### test_get_statistics
- **Purpose**: Verify that the API correctly returns statistics about forwarding rules
- **Endpoint**: GET /api/stats/
- **Expected Behavior**: Returns a 200 status code and statistics including total_rules and rules_with_filters
- **Edge Cases**: None (basic functionality test)

**Gherkin:**
```gherkin
Feature: Get forwarding rule statistics
  Scenario: Retrieve statistics
    Given there are multiple forwarding rules in the system
    When I send a GET request to "/api/stats/"
    Then the response status code should be 200
    And the response should contain statistics about the rules
    And the statistics should include total_rules and rules_with_filters
```

#### test_get_rule_filter
- **Purpose**: Verify that the API correctly returns the filter for a specific rule
- **Endpoint**: GET /api/rules/{rule_id}/filter
- **Expected Behavior**: Returns a 200 status code and the filter details for the rule
- **Edge Cases**: 
  - Returns a 404 status code when requesting a filter for a rule without a filter
  - Returns a 404 status code when requesting a filter for a non-existent rule

**Gherkin:**
```gherkin
Feature: Retrieve rule filter
  Scenario: Get filter for rule with filter
    Given there is a forwarding rule with ID 1 that has a filter
    When I send a GET request to "/api/rules/1/filter"
    Then the response status code should be 200
    And the response should contain the filter details
    
  Scenario: Get filter for rule without filter
    Given there is a forwarding rule with ID 2 that does not have a filter
    When I send a GET request to "/api/rules/2/filter"
    Then the response status code should be 404
    
  Scenario: Get filter for non-existent rule
    Given there is no forwarding rule with ID 999 in the system
    When I send a GET request to "/api/rules/999/filter"
    Then the response status code should be 404
```

### ReportAPITests

These tests focus on the report generation endpoints, with Celery tasks mocked to avoid actual task execution.

#### test_generate_full_report
- **Purpose**: Verify that the API correctly initiates the generation of a full report
- **Endpoint**: POST /api/reports/generate
- **Expected Behavior**: Returns a 200 status code and calls the generate_rules_report.delay() Celery task
- **Edge Cases**: Tests both with and without a custom report name

**Gherkin:**
```gherkin
Feature: Generate full report
  Scenario: Generate report without custom name
    Given the report generation system is available
    When I send a POST request to "/api/reports/generate"
    Then the response status code should be 200
    And the generate_rules_report Celery task should be called with no report name
    
  Scenario: Generate report with custom name
    Given the report generation system is available
    When I send a POST request to "/api/reports/generate?report_name=custom_report.pdf"
    Then the response status code should be 200
    And the generate_rules_report Celery task should be called with "custom_report.pdf"
```

#### test_generate_stats_report
- **Purpose**: Verify that the API correctly initiates the generation of a statistics-only report
- **Endpoint**: POST /api/reports/stats
- **Expected Behavior**: Returns a 200 status code and calls the generate_stats_report.delay() Celery task
- **Edge Cases**: Tests both with and without a custom report name

**Gherkin:**
```gherkin
Feature: Generate statistics report
  Scenario: Generate report without custom name
    Given the report generation system is available
    When I send a POST request to "/api/reports/stats"
    Then the response status code should be 200
    And the generate_stats_report Celery task should be called with no report name
    
  Scenario: Generate report with custom name
    Given the report generation system is available
    When I send a POST request to "/api/reports/stats?report_name=stats_report.pdf"
    Then the response status code should be 200
    And the generate_stats_report Celery task should be called with "stats_report.pdf"
```

#### test_generate_rules_only_report
- **Purpose**: Verify that the API correctly initiates the generation of a rules-only report
- **Endpoint**: POST /api/reports/rules-only
- **Expected Behavior**: Returns a 200 status code and calls the generate_rules_only_report.delay() Celery task
- **Edge Cases**: Tests both with and without a custom report name

**Gherkin:**
```gherkin
Feature: Generate rules-only report
  Scenario: Generate report without custom name
    Given the report generation system is available
    When I send a POST request to "/api/reports/rules-only"
    Then the response status code should be 200
    And the generate_rules_only_report Celery task should be called with no report name
    
  Scenario: Generate report with custom name
    Given the report generation system is available
    When I send a POST request to "/api/reports/rules-only?report_name=rules_only_report.pdf"
    Then the response status code should be 200
    And the generate_rules_only_report Celery task should be called with "rules_only_report.pdf"
```

## Testing Approach

### Mock Objects

For the report generation tests, we use the `unittest.mock` module to patch the Celery task calls:

```python
@patch('forwarding_rules.tasks.generate_rules_report.delay')
def test_generate_full_report(self, mock_task):
    # Test code
```

This approach allows us to:
1. Verify that the correct task is called with the right parameters
2. Avoid actually executing the task during testing
3. Control the returned task ID for assertion purposes

### Test Data

The tests create a sample dataset with:
- Two forwarding rules (one with filters, one without)
- One filter configuration
- Various attributes to test different aspects of the API

### Coverage

These tests cover:
- All API endpoints
- Success cases for each endpoint
- Error cases (e.g., 404 for non-existent resources)
- Parameter handling (e.g., optional report names)

## Running the Tests

To run all tests:
```bash
docker-compose exec web python manage.py test forwarding_rules
```

To run a specific test class:
```bash
docker-compose exec web python manage.py test forwarding_rules.tests.ForwardingRuleAPITests
```

To run a specific test method:
```bash
docker-compose exec web python manage.py test forwarding_rules.tests.ForwardingRuleAPITests.test_get_all_rules
``` 