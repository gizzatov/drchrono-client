from django.views.generic import TemplateView


class AuthView(TemplateView):
    template_name = "auth/login.html"
