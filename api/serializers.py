from biblioteca import models
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
        )


class BookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Livro
        fields = ("id", "nome", "ano", "edicao", "volume", "cdd_id")


class AuthorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Autor
        fields = ("id", "nome")


class DDCSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Cdd
        fields = ("id", "nome")


class CopySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Exemplar
        fields = ("id", "livro_id")


class HasAuthorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.LivroTemAutor
        fields = ("id", "autor_id", "livro_id")


class AdminBorrowSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Emprestimo
        fields = (
            "id",
            "data_emprestimo",
            "data_devolucao",
            "devolvido",
            "leitor_id",
            "exemplar_id",
        )


class UserBorrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Emprestimo
        fields = (
            "id",
            "data_emprestimo",
            "data_devolucao",
            "devolvido",
            "leitor_id",
            "exemplar_id",
        )
        read_only_fields = fields
