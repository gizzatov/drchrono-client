import requests
import logging

from application.apps.patients.models import Patient

logger = logging.getLogger(__name__)


class PatientMigrator:
    '''
    This class sync patient data from drchrono
    '''
    patients_data_url = 'https://drchrono.com/api/patients'

    def __init__(self, user):
        self.user = user

    def sync_patients(self):
        '''
        Main interface.
        Returns data and status message.
        status_message - is string with some possibly text (response warning for example)
        '''
        is_ok = True
        status_message = ''

        patients_from_provider, error_message = self._get_patients_list_from_provider()
        if error_message:
            return False, error_message

        self._match_user_patients(patients_from_provider)

        return is_ok, status_message

    def _get_patients_list_from_provider(self):
        '''
        drchrono paitents endpoint response example:
        {
            "next": null,
            "previous": null,
            "results": [
                {
                    "id": 2,
                    "first_name": "John",
                    "last_name": "Smith",
                    "date_of_birth": "1990-01-12",
                    "home_phone": "999-999-999",
                    "photo": null,
                    "updated_at": "2018-03-19T12:25:32",
                    ...
                }
            ]
        }
        '''
        patients = []
        error_message = ''

        auth = self.user.social_auth.filter(provider='drchrono').first()

        if auth is None:
            return patients, "Didn't found social auth session record"

        headers = {'Authorization': f'Bearer {auth.access_token}'}

        next_url = self.patients_data_url
        while next_url:
            try:
                raw_response = requests.get(next_url, headers=headers)
            except Exception as exc:
                logger.warning('Issues with connection to data provider', exc_info=True)
                break

            if raw_response.status_code != 200:
                response_message = raw_response.text or raw_response.reason
                logger.info(f'Issues with geting data from provider: {response_message}')

                if not patients:
                    error_message = response_message

                return patients, error_message

            response = raw_response.json()

            if next_url is not None and response['next'] == next_url:
                next_url = None
            else:
                next_url = response['next']

            if 'results' in response:
                patients.extend(response['results'])

        return patients, error_message

    def _match_user_patients(self, patients_from_provider: list):
        exist_patients = self.user.patients.values_list('internal_id', 'internal_updated_at')
        exist_patients_info = {
            patient_id: patient_updated_at for patient_id, patient_updated_at in exist_patients
            }

        for patient in patients_from_provider:
            if str(patient['id']) not in exist_patients_info:
                self.add_new_patient(patient)
            elif patient['updated_at'] != exist_patients_info[str(patient['id'])]:
                self.update_patient_info(patient)

    def add_new_patient(self, patient: dict):
        new_patient, _ = Patient.objects.get_or_create(
            internal_id=str(patient['id']),
            defaults={
                'first_name': patient.get('first_name', ''),
                'last_name': patient.get('last_name', ''),
                'birth_date': patient.get('date_of_birth'),
                'phone_number': patient.get('home_phone', '') or patient.get('cell_phone', '') or patient.get('office_phone', ''),
                'photo': patient.get('patient_photo'),
                'internal_updated_at': patient.get('updated_at', ''),
            }
        )
        self.user.patients.add(new_patient)

    def update_patient_info(self, patient: dict):
        self.user.patients.filter(internal_id=str(patient['id'])).update(
            first_name=patient.get('first_name', ''),
            last_name=patient.get('last_name', ''),
            birth_date=patient.get('date_of_birth'),
            phone_number=patient.get('home_phone', '') or patient.get('cell_phone', '') or patient.get('office_phone', ''),
            photo=patient.get('patient_photo'),
            internal_updated_at=patient.get('updated_at', ''),
        )
