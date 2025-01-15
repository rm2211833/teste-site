from django import forms
from django.contrib import admin

from . import models


class CddAdmin(admin.ModelAdmin):
    list_display = ("id", "nome")
    ordering = ("id",)
    list_per_page = 20

class Local_PublicacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome")
    ordering = ("id",)
    list_per_page = 20

class EditoraAdmin(admin.ModelAdmin):
    list_display = ("id", "nome")
    ordering = ("id",)
    list_per_page = 20

class LivroTemAutorInline(admin.TabularInline):
    model = models.LivroTemAutor  # Modelo de relacionamento
    extra = 1  # Número de formulários extras vazios


class AutorAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "codigo_autor")
    list_per_page = 20
    ordering = ("id",)


class LeitorAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "ra")
    list_per_page = 20
    ordering = ("id",)

class LivroForm(forms.ModelForm):
    quantidade_exemplares = forms.IntegerField(
        min_value=1, required=False, label="Quantidade de Exemplares"
    )

    class Meta:
        model = models.Livro
        fields = ["titulo", "ano", "edicao"]


class LivroAdmin(admin.ModelAdmin):
    form = LivroForm
    list_display = ("id", "titulo", "subtitulo", "ano", "edicao", "iniciais_titulo", "isbn")
    search_fields = ("titulo","isbn")
    list_filter = ("titulo", "ano")
    ordering = ("id",)
    list_per_page = 20
    inlines = [LivroTemAutorInline]

    def save_model(self, request, obj, form, change):
        """
        Sobrescreve o método para salvar o livro e criar múltiplos exemplares associados.
        """
        super().save_model(request, obj, form, change)

        # Obtém a quantidade de exemplares do formulário
        quantidade = form.cleaned_data.get("quantidade_exemplares", 0)

        # Gera os exemplares se a quantidade for maior que zero
        if quantidade > 0:
            models.Exemplar.objects.bulk_create(
                [models.Exemplar(livro=obj) for _ in range(quantidade)]
            )


class LivroTemAutorAdmin(admin.ModelAdmin):
    list_display = ("id", "autor", "livro")
    ordering = ("id",)
    list_per_page = 20


class ExemplarAdmin(admin.ModelAdmin):
    list_display = ("id", "livro", "tombo", "numero_exemplar", "baixa")
    ordering = ("id",)
    list_per_page = 20


class EmprestimoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "leitor",
        "exemplar",
        "data_emprestimo",
        "data_devolucao",
        "devolvido",
    )
    list_per_page = 20
    ordering = ("id",)


admin.site.register(models.Cdd, CddAdmin)
admin.site.register(models.Autor, AutorAdmin)
admin.site.register(models.Livro, LivroAdmin)
admin.site.register(models.LivroTemAutor, LivroTemAutorAdmin)
admin.site.register(models.Emprestimo, EmprestimoAdmin)
admin.site.register(models.Exemplar, ExemplarAdmin)
admin.site.register(models.Local_Publicacao, Local_PublicacaoAdmin)
admin.site.register(models.Editora, EditoraAdmin)
admin.site.register(models.Leitor, LeitorAdmin)
