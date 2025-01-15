from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from biblioteca import models

from . import views


class APITestCase(TestCase):
    def create_user(self):
        return models.User.objects.create(username="testuser0", is_staff=0)

    def create_staff(self):
        return models.User.objects.create(username="teststaff0", is_staff=1)


class UnauthenticatedAPITestCase(APITestCase):
    def test_api_root_view(self):
        """
        Ensure unauthenticated API availableness
        """
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)

    def test_api_users_view(self):
        """
        Ensure unauthenticated API users list unavailableness
        """
        factory = APIRequestFactory()
        view = views.UserViewSet.as_view({"get": "list"})
        request = factory.get("/api/usuarios/")
        response = view(request)
        self.assertEqual(response.status_code, 403)

    def test_api_books_view(self):
        """
        Ensure unauthenticated API books availableness
        """
        factory = APIRequestFactory()
        view = views.BookViewSet.as_view({"get": "list"})
        request = factory.get("/api/livros/")
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_api_authors_view(self):
        """
        Ensure unauthenticated API authors availableness
        """
        factory = APIRequestFactory()
        view = views.AuthorViewSet.as_view({"get": "list"})
        request = factory.get("/api/autores/")
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_api_ddc_view(self):
        """
        Ensure unauthenticated API DDC list availableness
        """
        factory = APIRequestFactory()
        view = views.DDCViewSet.as_view({"get": "list"})
        request = factory.get("/api/cdd/")
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_api_copy_view(self):
        """
        Ensure unauthenticated API copies list availableness
        """
        factory = APIRequestFactory()
        view = views.CopyViewSet.as_view({"get": "list"})
        request = factory.get("/api/exemplares/")
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_api_hasauthor_view(self):
        """
        Ensure unauthenticated API has authors list availableness
        """
        factory = APIRequestFactory()
        view = views.HasAuthorViewSet.as_view({"get": "list"})
        request = factory.get("/api/temautor/")
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_api_borrow_view(self):
        """
        Ensure unauthenticated API borrow list unavailableness
        """
        factory = APIRequestFactory()
        view = views.BorrowViewSet.as_view({"get": "list"})
        request = factory.get("/api/emprestimos/")
        response = view(request)
        self.assertEqual(response.status_code, 403)


class UserAPITestCase(APITestCase):
    def test_api_users_view(self):
        """
        Ensure normal user API users list unavailableness
        """
        factory = APIRequestFactory()
        view = views.UserViewSet.as_view({"get": "list"})
        request = factory.get("/api/usuarios/")
        user = self.create_user()
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 403)

    def test_api_borrow_view(self):
        """
        Ensure normal user API borrow list availableness
        """
        factory = APIRequestFactory()
        view = views.BorrowViewSet.as_view({"get": "list"})
        request = factory.get("/api/emprestimos/")
        user = self.create_user()
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200)


class StaffAPITestCase(APITestCase):
    def test_api_users_view(self):
        """
        Ensure staff API user list availableness
        """
        factory = APIRequestFactory()
        view = views.UserViewSet.as_view({"get": "list"})
        request = factory.get("/api/usuarios/")
        staff = self.create_staff()
        force_authenticate(request, user=staff)
        response = view(request)
        self.assertEqual(response.status_code, 200)


class StaffDataInsertionTestCase(APITestCase):
    def test_create_account(self):
        """
        Ensure staff API account creation
        """
        staff = self.create_staff()
        client = APIClient()
        client.force_authenticate(user=staff)
        response = client.post("/api/usuarios/", {"username": "testuser"})
        self.assertEqual(response.status_code, 201)

    def test_create_author(self):
        """
        Ensure staff API author creation
        """
        staff = self.create_staff()
        client = APIClient()
        client.force_authenticate(user=staff)
        response = client.post("/api/autores/", {"nome": "testauthor"})
        self.assertEqual(response.status_code, 201)

    def test_create_book_with_ddc(self):
        """
        Ensure staff API book creation
        """
        staff = self.create_staff()
        client = APIClient()
        client.force_authenticate(user=staff)
        ddc = client.post("/api/cdd/", {"nome": "000 test"})
        self.assertEqual(ddc.status_code, 201)
        book = client.post(
            "/api/livros/",
            {
                "nome": "testbook",
                "ano": 0,
                "edicao": 0,
                "volume": 0,
                "cdd_id": ddc.data["id"],
            },
        )
        self.assertEqual(book.status_code, 201)

    def test_create_copy(self):
        """
        Ensure staff API copy creation
        """
        staff = self.create_staff()
        client = APIClient()
        client.force_authenticate(user=staff)
        book = client.post(
            "/api/livros/", {"nome": "testbook", "ano": 0, "edicao": 0, "volume": 0}
        )
        copy1 = client.post("/api/exemplares/", {"livro_id": book.data["id"]})
        self.assertEqual(copy1.status_code, 201)
        copy2 = client.post("/api/exemplares/", {"livro_id": book.data["id"]})
        self.assertEqual(copy2.status_code, 201)

    def test_create_hasauthor(self):
        """
        Ensure staff API has author creation
        """
        staff = self.create_staff()
        client = APIClient()
        client.force_authenticate(user=staff)
        author = client.post("/api/autores/", {"nome": "testauthor"})
        book = client.post(
            "/api/livros/", {"nome": "testbook", "ano": 0, "edicao": 0, "volume": 0}
        )
        response = client.post(
            "/api/temautor/",
            {"author_id": author.data["id"], "livro_id": book.data["id"]},
        )
        self.assertEqual(response.status_code, 201)

    def test_create_borrow(self):
        """
        Ensure staff API borrow creation
        """
        staff = self.create_staff()
        user = self.create_user()
        client = APIClient()
        client.force_authenticate(user=staff)
        book = client.post(
            "/api/livros/", {"nome": "testbook", "ano": 0, "edicao": 0, "volume": 0}
        )
        copy = client.post("/api/exemplares/", {"livro_id": book.data["id"]})
        response = client.post(
            "/api/emprestimos/", {"leitor_id": user.id, "exemplar_id": copy.data["id"]}
        )
        self.assertEqual(response.status_code, 201)


class UserDataInsertionTestCase(APITestCase):
    def test_create_borrow(self):
        """
        Ensure that normal user API can't create borrowings
        """
        staff = self.create_staff()
        user = self.create_user()
        client = APIClient()
        client.force_authenticate(user=staff)
        book = client.post(
            "/api/livros/", {"nome": "testbook", "ano": 0, "edicao": 0, "volume": 0}
        )
        copy = client.post("/api/exemplares/", {"livro_id": book.data["id"]})
        client.force_authenticate(user=user)
        response = client.post(
            "/api/emprestimos/", {"leitor_id": user.id, "exemplar_id": copy.data["id"]}
        )
        self.assertEqual(response.status_code, 403)

    def test_create_account(self):
        """
        Ensure that normal user API can't create account
        """
        user = self.create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post("/api/usuarios/", {"username": "testuser"})
        self.assertEqual(response.status_code, 403)

    def test_create_author(self):
        """
        Ensure that normal user API can't create author
        """
        user = self.create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post("/api/autores/", {"nome": "testauthor"})
        self.assertEqual(response.status_code, 403)

    def test_create_book(self):
        """
        Ensure that normal user API can't create book
        """
        user = self.create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        ddc = client.post("/api/cdd/", {"nome": "000 test"})
        self.assertEqual(ddc.status_code, 403)

    def test_create_ddc(self):
        """
        Ensure that normal user API can't create DDC
        """
        user = self.create_user()
        client = APIClient()
        client.force_authenticate(user=user)
        book = client.post(
            "/api/livros/", {"nome": "testbook", "ano": 0, "edicao": 0, "volume": 0}
        )
        self.assertEqual(book.status_code, 403)

    def test_create_copy(self):
        """
        Ensure that normal user API can't create copy
        """
        staff = self.create_staff()
        user = self.create_user()
        client = APIClient()
        client.force_authenticate(user=staff)
        book = client.post(
            "/api/livros/", {"nome": "testbook", "ano": 0, "edicao": 0, "volume": 0}
        )
        client.force_authenticate()
        copy1 = client.post("/api/exemplares/", {"livro_id": book.data["id"]})
        self.assertEqual(copy1.status_code, 403)
        copy2 = client.post("/api/exemplares/", {"livro_id": book.data["id"]})
        self.assertEqual(copy2.status_code, 403)


class UnauthenticatedInsertionTestCase(APITestCase):
    def test_create_borrow(self):
        """
        Ensure unauthenticated API borrowing unavailableness
        """
        staff = self.create_staff()
        user = self.create_user()
        client = APIClient()
        client.force_authenticate(user=staff)
        book = client.post(
            "/api/livros/", {"nome": "testbook", "ano": 0, "edicao": 0, "volume": 0}
        )
        copy = client.post("/api/exemplares/", {"livro_id": book.data["id"]})
        client.force_authenticate()
        response = client.post(
            "/api/emprestimos/", {"leitor_id": user.id, "exemplar_id": copy.data["id"]}
        )
        self.assertEqual(response.status_code, 403)

    def test_create_account(self):
        """
        Ensure unauthenticated API account creation unavailableness
        """
        client = APIClient()
        response = client.post("/api/usuarios/", {"username": "testuser"})
        self.assertEqual(response.status_code, 403)

    def test_create_author(self):
        """
        Ensure unauthenticated API author creation unavailableness
        """
        client = APIClient()
        response = client.post("/api/autores/", {"nome": "testauthor"})
        self.assertEqual(response.status_code, 403)

    def test_create_book(self):
        """
        Ensure unauthenticated API book creation unavailableness
        """
        client = APIClient()
        ddc = client.post("/api/cdd/", {"nome": "000 test"})
        self.assertEqual(ddc.status_code, 403)

    def test_create_ddc(self):
        """
        Ensure unauthenticated API DDC creation unavailableness
        """
        client = APIClient()
        book = client.post(
            "/api/livros/", {"nome": "testbook", "ano": 0, "edicao": 0, "volume": 0}
        )
        self.assertEqual(book.status_code, 403)

    def test_create_copy(self):
        """
        Ensure unauthenticated API copy creation unavailableness
        """
        staff = self.create_staff()
        client = APIClient()
        client.force_authenticate(user=staff)
        book = client.post(
            "/api/livros/", {"nome": "testbook", "ano": 0, "edicao": 0, "volume": 0}
        )
        client.force_authenticate()
        copy1 = client.post("/api/exemplares/", {"livro_id": book.data["id"]})
        self.assertEqual(copy1.status_code, 403)
        copy2 = client.post("/api/exemplares/", {"livro_id": book.data["id"]})
        self.assertEqual(copy2.status_code, 403)
