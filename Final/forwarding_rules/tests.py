from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json

from .models import AutoForwarding, ForwardingFilter
from .tasks import generate_rules_report, generate_stats_report, generate_rules_only_report


class ForwardingRuleAPITests(TestCase):
    """Tests for the Forwarding Rules API endpoints"""

    def setUp(self):
        """Set up test data before each test"""
        # Create test forwarding rules
        self.rule1 = AutoForwarding.objects.create(
            email="user1@example.com",
            name="User One",
            forwarding_email="forward1@example.com",
            disposition="Under Review",
            has_forwarding_filters=True,
            investigation_note="Initial investigation"
        )
        
        self.rule2 = AutoForwarding.objects.create(
            email="user2@example.com",
            name="User Two",
            forwarding_email="forward2@example.com",
            disposition="Approved",
            has_forwarding_filters=False
        )
        
        # Create a filter for rule1
        self.filter1 = ForwardingFilter.objects.create(
            forwarding_id=self.rule1.id,
            criteria={"from": "newsletter@example.com", "subject": "Weekly Update"},
            action={"forward": "archive@example.com", "addLabels": ["NEWSLETTER"]}
        )

    def test_get_all_rules(self):
        """Test retrieving all forwarding rules"""
        response = self.client.get('/api/rules/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        # Verify rule details are present
        self.assertEqual(data[0]['email'], "user1@example.com")
        self.assertEqual(data[1]['email'], "user2@example.com")

    def test_get_specific_rule(self):
        """Test retrieving a specific rule by ID"""
        response = self.client.get(f'/api/rules/{self.rule1.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['email'], "user1@example.com")
        self.assertEqual(data['name'], "User One")
        self.assertEqual(data['disposition'], "Under Review")
        
        # Test getting a non-existent rule
        response = self.client.get('/api/rules/999')
        self.assertEqual(response.status_code, 404)

    def test_update_investigation_note(self):
        """Test updating the investigation note for a rule"""
        update_data = {
            "investigation_note": "Updated investigation details"
        }
        response = self.client.put(
            f'/api/rules/{self.rule1.id}/investigation',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['investigation_note'], "Updated investigation details")
        
        # Verify the update in database
        updated_rule = AutoForwarding.objects.get(id=self.rule1.id)
        self.assertEqual(updated_rule.investigation_note, "Updated investigation details")
        
        # Test updating a non-existent rule
        response = self.client.put(
            '/api/rules/999/investigation',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_rule(self):
        """Test deleting a forwarding rule"""
        # First verify we have 2 rules
        self.assertEqual(AutoForwarding.objects.count(), 2)
        
        # Delete one rule
        response = self.client.delete(f'/api/rules/{self.rule2.id}')
        self.assertEqual(response.status_code, 204)
        
        # Verify rule was deleted
        self.assertEqual(AutoForwarding.objects.count(), 1)
        self.assertFalse(AutoForwarding.objects.filter(id=self.rule2.id).exists())
        
        # Test deleting a non-existent rule
        response = self.client.delete('/api/rules/999')
        self.assertEqual(response.status_code, 404)

    def test_search_rules(self):
        """Test searching for rules with filters"""
        # Test search by email
        response = self.client.get('/api/rules/search/', {'email': 'user1'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['email'], "user1@example.com")
        
        # Test search by has_filters flag
        response = self.client.get('/api/rules/search/', {'has_filters': 'true'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['email'], "user1@example.com")
        self.assertTrue(data[0]['has_forwarding_filters'])
        
        # Test search with no results
        response = self.client.get('/api/rules/search/', {'email': 'nonexistent'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)

    def test_get_statistics(self):
        """Test retrieving statistics about forwarding rules"""
        response = self.client.get('/api/stats/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify expected statistics
        self.assertIn('total_rules', data)
        self.assertIn('rules_with_filters', data)
        self.assertEqual(data['total_rules'], 2)
        self.assertEqual(data['rules_with_filters'], 1)

    def test_get_rule_filter(self):
        """Test retrieving the filter for a specific rule"""
        # Get filter for rule with filter
        response = self.client.get(f'/api/rules/{self.rule1.id}/filter')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['forwarding_id'], self.rule1.id)
        self.assertEqual(data['criteria']['from'], "newsletter@example.com")
        self.assertEqual(data['action']['forward'], "archive@example.com")
        
        # Try to get filter for rule without filter
        response = self.client.get(f'/api/rules/{self.rule2.id}/filter')
        self.assertEqual(response.status_code, 404)
        
        # Try to get filter for non-existent rule
        response = self.client.get('/api/rules/999/filter')
        self.assertEqual(response.status_code, 404)


class ReportAPITests(TestCase):
    """Tests for the report generation API endpoints"""

    @patch('forwarding_rules.tasks.generate_rules_report.delay')
    def test_generate_full_report(self, mock_task):
        """Test generating a full report"""
        # Configure the mock
        mock_task.return_value = MagicMock(id='fake-task-id')
        
        # Test without report name
        response = self.client.post('/api/reports/generate')
        self.assertEqual(response.status_code, 200)
        mock_task.assert_called_once_with(None)
        
        # Reset mock for next test
        mock_task.reset_mock()
        
        # Test with custom report name as query parameter
        response = self.client.post('/api/reports/generate?report_name=custom_report.pdf')
        self.assertEqual(response.status_code, 200)
        mock_task.assert_called_once_with("custom_report.pdf")

    @patch('forwarding_rules.tasks.generate_stats_report.delay')
    def test_generate_stats_report(self, mock_task):
        """Test generating a statistics-only report"""
        # Configure the mock
        mock_task.return_value = MagicMock(id='fake-task-id')
        
        # Test without report name
        response = self.client.post('/api/reports/stats')
        self.assertEqual(response.status_code, 200)
        mock_task.assert_called_once_with(None)
        
        # Reset mock for next test
        mock_task.reset_mock()
        
        # Test with custom report name as query parameter
        response = self.client.post('/api/reports/stats?report_name=stats_report.pdf')
        self.assertEqual(response.status_code, 200)
        mock_task.assert_called_once_with("stats_report.pdf")

    @patch('forwarding_rules.tasks.generate_rules_only_report.delay')
    def test_generate_rules_only_report(self, mock_task):
        """Test generating a rules-only report"""
        # Configure the mock
        mock_task.return_value = MagicMock(id='fake-task-id')
        
        # Test without report name
        response = self.client.post('/api/reports/rules-only')
        self.assertEqual(response.status_code, 200)
        mock_task.assert_called_once_with(None)
        
        # Reset mock for next test
        mock_task.reset_mock()
        
        # Test with custom report name as query parameter
        response = self.client.post('/api/reports/rules-only?report_name=rules_only_report.pdf')
        self.assertEqual(response.status_code, 200)
        mock_task.assert_called_once_with("rules_only_report.pdf") 