from datetime import datetime

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.views.generic import TemplateView

from application.apps.patients.handlers import PatientMigrator


class PatientView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = "patients/patients.html"

    def handle_no_permission(self):
        if 'code' in self.request.GET and not self.request.user.is_authenticated:
            redirect_url = reverse('social:complete', args=['drchrono'])
            return HttpResponseRedirect(f'{redirect_url}?{self.request.META["QUERY_STRING"]}')
        else:
            return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cached_at = cache.get(settings.DRCHRONO_PATIENTS_CACHE_KEY)
        if not cached_at:
            migrator = PatientMigrator(self.request.user)
            is_ok, status_message = migrator.sync_patients()

            if not is_ok:
                context['status_message'] = status_message

            cached_at = datetime.utcnow().isoformat()
            cache.set(
                settings.DRCHRONO_PATIENTS_CACHE_KEY,
                cached_at,
                timeout=settings.DRCHRONO_PATIENTS_CACHE_TTL
                )

        page_number = self.request.GET.get('page')
        page_size = self.request.GET.get('page_size', 25)
        paginator = Paginator(self.request.user.patients.all().order_by('id'), page_size)
        patients = paginator.get_page(page_number)
        context['patients'] = patients
        context['page_size'] = page_size
        context['latest_sync_at'] = parse_datetime(cached_at)
        return context
