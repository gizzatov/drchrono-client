from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import HttpResponseRedirect
from django.urls import reverse


class PatientView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = "patients/patients.html"

    def handle_no_permission(self):
        if 'code' in self.request.GET and not self.request.user.is_authenticated:
            redirect_url = reverse('social:complete', args=['drchrono'])
            return HttpResponseRedirect(f'{redirect_url}?{self.request.META["QUERY_STRING"]}')
        else:
            return super().handle_no_permission()
