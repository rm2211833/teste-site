from django.contrib.auth.models import User
from rest_framework import permissions, viewsets

from . import serializers
from biblioteca import models


class IsAdminUserOrReadOnly(permissions.IsAdminUser):
    def has_permission(self, request, view):
        is_admin = super(IsAdminUserOrReadOnly, self).has_permission(request, view)
        return request.method in permissions.SAFE_METHODS or is_admin

class IsAdminUserOrAuthenticatedReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        elif request.user.is_authenticated and request.method in permissions.SAFE_METHODS:
            return True
        return False

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAdminUser]

class BookViewSet(viewsets.ModelViewSet):
    queryset = models.Livro.objects.all().order_by('id')
    serializer_class = serializers.BookSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = models.Autor.objects.all().order_by('id')
    serializer_class = serializers.AuthorSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class DDCViewSet(viewsets.ModelViewSet):
    queryset = models.Cdd.objects.all().order_by('id')
    serializer_class = serializers.DDCSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class CopyViewSet(viewsets.ModelViewSet):
    queryset = models.Exemplar.objects.all().order_by('id')
    serializer_class = serializers.CopySerializer
    permission_classes = [IsAdminUserOrReadOnly]

class HasAuthorViewSet(viewsets.ModelViewSet):
    queryset = models.LivroTemAutor.objects.all().order_by('id')
    serializer_class = serializers.HasAuthorSerializer
    permission_classes = [IsAdminUserOrReadOnly]

class BorrowViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.request.user.is_staff:
            return serializers.AdminBorrowSerializer
        return serializers.UserBorrowSerializer
    def get_queryset(self):
        if self.request.user.is_staff:
            return models.Emprestimo.objects.all().order_by('id')
        return models.Emprestimo.objects.filter(leitor_id=self.request.user.id).order_by('devolvido')
    permission_classes = [IsAdminUserOrAuthenticatedReadOnly]
