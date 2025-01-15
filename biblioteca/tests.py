from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from . import models


class BibliotecaViewsTestCase(TestCase):
    def setUp(self):
        ...
        # Configuração inicial para todos os testes
        # self.user = User.objects.create_user(username="testuser", password="12345")
        # self.livro = models.Livro.objects.create(nome="Livro de Teste")
        # self.exemplar = models.Exemplar.objects.create(livro=self.livro)
        # self.emprestimo = models.Emprestimo.objects.create(
        #     leitor=self.user, exemplar=self.exemplar, devolvido=False
        # )

    # Teste para a view inicial
    def test_inicial_view(self):
        response = self.client.get(reverse("biblioteca:inicial"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("inicial", response.context["guia_atual"])


    # Teste para a view register (GET)
    def test_register_view_get(self):
        response = self.client.get(reverse("biblioteca:register"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    # Teste para a view register (POST)
    def test_register_view_post(self):
        response = self.client.post(
            reverse("biblioteca:register"),
            {
                "username": "newuser",
                "password1": "newpassword123",
                "password2": "newpassword123",
            },
        )
        self.assertEqual(response.status_code, 200)  # Redireciona após o sucesso
        self.assertFalse(User.objects.filter(username="newuser").exists())

    # Teste para a view login_view (GET)
    def test_login_view_get(self):
        response = self.client.get(reverse("biblioteca:login"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    # Teste para a view logout_view:
    def test_logout_view(self):
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("biblioteca:logout"))
        self.assertEqual(
            response.status_code, 302
        )  # Redireciona para a página de login
        response = self.client.get(reverse("biblioteca:inicial"))
        self.assertNotIn(
            "_auth_user_id", self.client.session
        )  # Confirma que o usuário foi deslogado
