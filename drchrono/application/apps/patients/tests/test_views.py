import json
from unittest.mock import patch

import fakeredis
import httpretty
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils.dateparse import parse_date
from social_django.models import UserSocialAuth

from application.apps.patients.handlers import PatientMigrator
from application.apps.patients.models import Patient

User = get_user_model()


class AuthViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.username = 'testuser'
        cls.user = User.objects.create(username=cls.username, email='admin@acme.test')
        cls.user.set_password('123')
        cls.user.save()
        UserSocialAuth.objects.create(
            user=cls.user,
            uid='1111',
            provider='drchrono',
            extra_data={
                "auth_time": 1541322623,
                "token_type": "Bearer",
                "access_token": "HPcpYLicAHxiqhKPsQs6dmNPp8QmTR"
                }
            )
        cls.url = reverse('patient_list')
        cls.patient_data_url = PatientMigrator.patients_data_url

    def setUp(self):
        self.fake_redis = fakeredis.FakeStrictRedis()

    def tearDown(self):
        self.fake_redis.flushall()

    @httpretty.activate
    def test_get_empty_patient_list_success(self):
        httpretty.register_uri(
            httpretty.GET,
            self.patient_data_url,
            body=json.dumps({
                'next': None,
                'previous': None,
                'results': []
            })
        )
        self.assertTrue(httpretty.is_enabled())
        self.assertEqual(self.user.patients.all().count(), 0)
        self.client.login(username=self.username, password='123')

        response = self.client.get(self.url)

        context = response.context
        self.assertEqual(len(context['patients'].object_list), 0)
        self.assertEqual(context['page_size'], 25)
        self.assertTrue(context['latest_sync_at'])
        self.assertTrue('status_message' not in context)

        self.assertEqual(self.user.patients.all().count(), 0)
        self.assertEqual(Patient.objects.all().count(), 0)

    @httpretty.activate
    def test_get_patient_list__patient_on_one_page_success(self):
        httpretty.register_uri(
            httpretty.GET,
            self.patient_data_url,
            body=json.dumps({
                'next': None,
                'previous': None,
                'results': [
                    {
                        'id': 1,
                        'first_name': 'Mark',
                        'last_name': 'Adams',
                        'date_of_birth': '1958-09-02',
                        'home_phone': '',
                        'photo': None,
                        'updated_at': '2018-03-19T12:25:32',
                    }
                ]
            })
        )
        self.assertTrue(httpretty.is_enabled())
        self.assertEqual(self.user.patients.all().count(), 0)
        self.client.login(username=self.username, password='123')

        response = self.client.get(self.url)

        context = response.context
        self.assertEqual(len(context['patients'].object_list), 1)
        self.assertEqual(context['page_size'], 25)
        self.assertTrue(context['latest_sync_at'])
        self.assertTrue('status_message' not in context)

        self.assertEqual(self.user.patients.all().count(), 1)
        self.assertEqual(Patient.objects.all().count(), 1)

        patient = self.user.patients.first()
        self.assertEqual(patient.internal_id, '1')
        self.assertEqual(patient.internal_updated_at, '2018-03-19T12:25:32')
        self.assertEqual(patient.first_name, 'Mark')
        self.assertEqual(patient.last_name, 'Adams')
        self.assertEqual(patient.birth_date, parse_date('1958-09-02'))
        self.assertEqual(patient.phone_number, '')
        self.assertEqual(patient.photo, None)

    @httpretty.activate
    def test_get_patient_list__patient_on_few_page_success(self):
        next_url = f'{self.patient_data_url}?page=2'

        def request_callback(request, uri, response_headers):
            if uri == self.patient_data_url:
                body = {
                    'next': next_url,
                    'previous': None,
                    'results': [
                        {
                            'id': 1,
                            'first_name': 'Mark',
                            'last_name': 'Adams',
                            'date_of_birth': '1958-09-02',
                            'home_phone': '',
                            'photo': None,
                            'updated_at': '2018-03-19T12:25:32',
                        },
                        {
                            'id': 1,  # check for duplicates
                            'first_name': 'Mark',
                            'last_name': 'Adams',
                            'date_of_birth': '1958-09-02',
                            'home_phone': '',
                            'photo': None,
                            'updated_at': '2018-03-19T12:25:32',
                        }
                    ]
                }
            if uri == next_url:
                body = {
                    'next': None,
                    'previous': None,
                    'results': [
                        {
                            'id': 2,
                            'first_name': 'John',
                            'last_name': 'Smith',
                            'date_of_birth': '1990-01-12',
                            'home_phone': '999-999-999',
                            'photo': None,
                            'updated_at': '2018-03-19T12:25:32',
                        }
                    ]
                }
            return [200, response_headers, json.dumps(body)]

        httpretty.register_uri(
            httpretty.GET,
            self.patient_data_url,
            match_querystring=True,
            body=request_callback,
        )

        httpretty.register_uri(
            httpretty.GET,
            next_url,
            match_querystring=True,
            body=request_callback,
        )
        self.assertTrue(httpretty.is_enabled())
        self.assertEqual(self.user.patients.all().count(), 0)
        self.client.login(username=self.username, password='123')

        response = self.client.get(self.url)

        context = response.context
        self.assertEqual(len(context['patients'].object_list), 2)
        self.assertEqual(context['page_size'], 25)
        self.assertTrue(context['latest_sync_at'])
        self.assertTrue('status_message' not in context)

        self.assertEqual(self.user.patients.all().count(), 2)
        self.assertEqual(Patient.objects.all().count(), 2)

        first_patient = self.user.patients.first()
        self.assertEqual(first_patient.internal_id, '1')
        self.assertEqual(first_patient.internal_updated_at, '2018-03-19T12:25:32')
        self.assertEqual(first_patient.first_name, 'Mark')
        self.assertEqual(first_patient.last_name, 'Adams')
        self.assertEqual(first_patient.birth_date, parse_date('1958-09-02'))
        self.assertEqual(first_patient.phone_number, '')
        self.assertEqual(first_patient.photo, None)

        last_patient = self.user.patients.last()
        self.assertEqual(last_patient.internal_id, '2')
        self.assertEqual(last_patient.internal_updated_at, '2018-03-19T12:25:32')
        self.assertEqual(last_patient.first_name, 'John')
        self.assertEqual(last_patient.last_name, 'Smith')
        self.assertEqual(last_patient.birth_date, parse_date('1990-01-12'))
        self.assertEqual(last_patient.phone_number, '999-999-999')
        self.assertEqual(last_patient.photo, None)

    @httpretty.activate
    def test_get_patient_list_update_data_success(self):
        raw_patient = {
            'id': 1,
            'first_name': 'Mark',
            'last_name': 'Adams',
            'date_of_birth': '1958-09-02',
            'home_phone': '',
            'photo': None,
            'updated_at': '2018-03-19T12:25:32',
        }

        migrator = PatientMigrator(user=self.user)
        migrator.add_new_patient(raw_patient)

        raw_patient['first_name'] = 'Markus'
        raw_patient['updated_at'] = '2018-05-19T12:25:32'

        httpretty.register_uri(
            httpretty.GET,
            self.patient_data_url,
            body=json.dumps({
                'next': None,
                'previous': None,
                'results': [raw_patient]
            })
        )
        self.assertTrue(httpretty.is_enabled())
        self.assertEqual(self.user.patients.all().count(), 1)
        self.client.login(username=self.username, password='123')

        response = self.client.get(self.url)

        context = response.context
        self.assertEqual(len(context['patients'].object_list), 1)
        self.assertEqual(context['page_size'], 25)
        self.assertTrue(context['latest_sync_at'])
        self.assertTrue('status_message' not in context)

        self.assertEqual(self.user.patients.all().count(), 1)
        self.assertEqual(Patient.objects.all().count(), 1)

        patient = self.user.patients.first()
        self.assertEqual(patient.internal_id, '1')
        self.assertEqual(patient.internal_updated_at, '2018-05-19T12:25:32')
        self.assertEqual(patient.first_name, 'Markus')
        self.assertEqual(patient.last_name, 'Adams')
        self.assertEqual(patient.birth_date, parse_date('1958-09-02'))
        self.assertEqual(patient.phone_number, '')
        self.assertEqual(patient.photo, None)

    @httpretty.activate
    def test_get_list_with_cached_migrator_calls_success(self):
        httpretty.register_uri(
            httpretty.GET,
            self.patient_data_url,
            body=json.dumps({
                'next': None,
                'previous': None,
                'results': []
            })
        )
        self.assertTrue(httpretty.is_enabled())
        self.assertEqual(self.user.patients.all().count(), 0)
        self.client.login(username=self.username, password='123')

        with patch.object(PatientMigrator, 'sync_patients'):
            PatientMigrator.sync_patients.return_value = (True, '')

            cached_at = cache.get(settings.DRCHRONO_PATIENTS_CACHE_KEY)
            self.assertIsNone(cached_at)

            self.client.get(self.url)
            PatientMigrator.sync_patients.assert_called_once()
            cached_at = cache.get(settings.DRCHRONO_PATIENTS_CACHE_KEY)
            self.assertIsNotNone(cached_at)

            PatientMigrator.sync_patients.reset_mock()
            self.client.get(self.url)
            PatientMigrator.sync_patients.assert_not_called()

    @httpretty.activate
    def test_get_list_with_overlimit_api_call_success(self):
        raw_patient = {
            'id': 1,
            'first_name': 'Mark',
            'last_name': 'Adams',
            'date_of_birth': '1958-09-02',
            'home_phone': '',
            'photo': None,
            'updated_at': '2018-03-19T12:25:32',
        }

        migrator = PatientMigrator(user=self.user)
        migrator.add_new_patient(raw_patient)

        httpretty.register_uri(
            httpretty.GET,
            self.patient_data_url,
            status=429,
            body='Over limit',
        )
        self.assertTrue(httpretty.is_enabled())
        self.assertEqual(self.user.patients.all().count(), 1)
        self.client.login(username=self.username, password='123')

        response = self.client.get(self.url)

        context = response.context
        self.assertEqual(len(context['patients'].object_list), 1)
        self.assertEqual(context['page_size'], 25)
        self.assertTrue(context['latest_sync_at'])
        self.assertEqual(context['status_message'], 'Over limit')

        self.assertEqual(self.user.patients.all().count(), 1)
