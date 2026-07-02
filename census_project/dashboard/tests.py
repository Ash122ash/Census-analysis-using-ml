from django.test import TestCase, Client
from .models import PopulationData

class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_dashboard(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please select a State and District")

    def test_post_all_scope(self):
        # Test posting with 'all' scope
        response = self.client.post('/', {
            'scope': 'all',
            'gender_analysis': 'on',
            'age_distribution': 'on',
            'literacy_education': 'on'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.context)
        data = response.context['data']
        self.assertGreater(data.persons, 0)
        self.assertGreater(data.population, 0)
        # Check comparative literacy rates
        self.assertGreater(data.literacy_rate_2001, 0)
        self.assertGreater(data.literacy_rate_2011, 0)
        # Check comparative age group counts
        self.assertGreater(data.age_0_4_2001, 0)
        self.assertGreater(data.age_0_29_2011, 0)
        # Check gender split sums
        self.assertGreater(data.males_2001, 0)
        self.assertGreater(data.male_2011, 0)
        # Check charts present in HTML
        self.assertContains(response, 'genderChart2001')
        self.assertContains(response, 'genderChart2011')
        self.assertContains(response, 'ageChart2001')
        self.assertContains(response, 'ageChart2011')
