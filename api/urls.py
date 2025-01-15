from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "api"

router = routers.DefaultRouter()
router.register(r"usuarios", views.UserViewSet)
router.register(r"autores", views.AuthorViewSet)
router.register(r"livros", views.BookViewSet)
router.register(r"exemplares", views.CopyViewSet)
router.register(r"emprestimos", views.BorrowViewSet, basename='emprestimos')
router.register(r"cdd", views.DDCViewSet)
router.register(r"temautor", views.HasAuthorViewSet)

urlpatterns = [
    path("api/", include((router.urls, app_name))),
    path("api/auth", include("rest_framework.urls", namespace="rest_framework"))
]
