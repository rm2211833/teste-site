from datetime import datetime

from django.contrib import admin

from . import forms, models


class AutorAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "codigo_autor")
    # list_display_links = ("id", "nome", "codigo_autor")
    fields = ["nome", "codigo_autor"]
    search_fields = ("nome",)    
    list_per_page = 30
    ordering = ("id",)


class CddAdmin(admin.ModelAdmin):
    list_display = ("id", "nome")
    list_display_links = ("id", "nome")
    search_fields = ("nome",)
    ordering = ("id",)
    list_per_page = 10

class EditoraAdmin(admin.ModelAdmin):
    list_display = ("id", "nome")
    list_display_links = ("id", "nome")
    search_fields = ("nome",)
    ordering = ("id",)
    list_per_page = 30
   
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "leitor",
        "exemplar",
        "data_emprestimo",
        "data_devolucao",
        "devolvido",
    )
    search_fields = ("leitor__nome", "exemplar__livro__titulo" )  
    autocomplete_fields = ["leitor", "exemplar"]    
    ordering = ("devolvido", "data_emprestimo")
    list_display_links = ("id", "leitor", "exemplar")
    list_editable = ("devolvido",)
    list_per_page = 30
    def get_form(self, request, obj = None, change = False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["data_emprestimo"].label = "Data de Empréstimo"
        form.base_fields["data_devolucao"].label = "Data de Devolução"
        return form
    
class ExemplarAdmin(admin.ModelAdmin):
    form = forms.ExemplarAdminForm
    list_display = ("id", "livro", "tombo", "numero_exemplar", "baixa", "etiqueta_gerada" )
    list_display_links = ("id", "livro", "tombo")
    list_editable = ("baixa","etiqueta_gerada")        
    search_fields = ("livro__titulo","numero_exemplar")  
    ordering = ("id",)      
    autocomplete_fields = ["livro"] 
    list_per_page = 20
    fieldsets = (
    (None, {
        "fields": ("livro", "tombo", "numero_exemplar", "baixa", "etiqueta_gerada", "quantidade"),
    }),
    )    
       
    def save_model(self, request, obj, form, change):
        quantidade = form.cleaned_data.get("quantidade")
        
        if quantidade and quantidade > 1:
            # Obter o maior número de exemplar existente para este livro
            ultimo_numero = (
                models.Exemplar.objects.filter(livro=obj.livro)
                .order_by("-numero_exemplar")
                .values_list("numero_exemplar", flat=True)
                .first()
                or 0
            )           
            ano_atual = datetime.now().year
            
            # Criar uma lista de objetos para inserir em lote
            exemplares = [
                models.Exemplar(
                    livro=obj.livro,
                    tombo=f"Crav.{ano_atual}.'ID_TEMP'",
                    numero_exemplar=ultimo_numero + i,
                    baixa=obj.baixa,
                    etiqueta_gerada=obj.etiqueta_gerada,
                )
                for i in range(1, quantidade + 1)
            ]
            
            # Inserir todos os exemplares em uma única operação
            models.Exemplar.objects.bulk_create(exemplares)
            
            exemplares_criados = models.Exemplar.objects.filter(
            livro=obj.livro,
            tombo__icontains="ID_TEMP"
        )

            for _, exemplar in enumerate(exemplares_criados):
                # Atualiza o campo 'tombo' para cada exemplar, usando o ID recém-gerado
                exemplar.tombo = f"Crav.{ano_atual}.{exemplar.id}"
            
            # Atualizando os objetos em massa com os novos valores de 'tombo'
            models.Exemplar.objects.bulk_update(exemplares_criados, ['tombo'])
            
        else:
            # Salvar o exemplar normalmente
            super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):        
        if obj is None:  
            return ("numero_exemplar", "tombo")
        return ("id")


class LivroTemAutorInline(admin.TabularInline):
    model = models.LivroTemAutor  # Modelo de relacionamento
    extra = 1  # Número de formulários extras vazios
    verbose_name="Autor"
    verbose_name_plural="Autores"
    search_files=("autor__nome", "livro__titulo")
    autocomplete_fields =("autor",)

class LeitorAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "ra", "ativo")
    search_fields = ("nome","ra")
    list_per_page = 30
    ordering = ("id",)
    list_editable = ("ativo",)   


class LivroAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "subtitulo", "ano", "edicao", "iniciais_titulo", "isbn")
    search_fields = ("titulo","isbn")
    list_display_links = ("id", "titulo", "subtitulo")
    ordering = ("id",)
    list_per_page = 30
    autocomplete_fields = ["cdd", "editora", "local_publicacao"] 
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
    list_display_links = ("id", "autor", "livro")
    search_fields = ("livro__titulo","autor__nome")  
    autocomplete_fields=("autor", "livro")      
    ordering = ("id",)
    list_per_page = 30

class Local_PublicacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome")
    search_fields = ("nome",)
    list_display_links = ("id", "nome")
    ordering = ("id",)
    list_per_page = 30


admin.site.register(models.Cdd, CddAdmin)
admin.site.register(models.Autor, AutorAdmin)
admin.site.register(models.Livro, LivroAdmin)
admin.site.register(models.LivroTemAutor, LivroTemAutorAdmin)
admin.site.register(models.Emprestimo, EmprestimoAdmin)
admin.site.register(models.Exemplar, ExemplarAdmin)
admin.site.register(models.Local_Publicacao, Local_PublicacaoAdmin)
admin.site.register(models.Editora, EditoraAdmin)
admin.site.register(models.Leitor, LeitorAdmin)
