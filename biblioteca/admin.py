from datetime import date, datetime

from django.contrib import admin, messages
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import path

from biblioteca.PDFsGerados.GeradorEtiquetaPDF import GerarEtiquetaPDF
from biblioteca.PDFsGerados.RelatoriosPDF import (RelatorioDevedores,
                                                  RelatorioEmprestimosAnual,
                                                  RelatorioEmprestimosMensal,
                                                  RelatorioLeitores)

from . import forms, models, tratamento_dados


def gerar_pdf_etiquetas(modeladmin, request, exemplares):
    """
    Gera um PDF com etiquetas para os livros selecionados.
    """
    gerador = GerarEtiquetaPDF(exemplares)
    pdf = gerador.criar_pdf()
    # Cria uma resposta HTTP para o arquivo PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    data_e_hora = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    response['Content-Disposition'] = f'attachment; filename="etiquetas-{data_e_hora}.pdf"'
   
    for exemplar in exemplares:       
        exemplar.etiqueta_gerada = True
        
    models.Exemplar.objects.bulk_update(exemplares, ['etiqueta_gerada'])       
    return response

gerar_pdf_etiquetas.short_description = "Gerar PDF de Etiquetas" #type:ignore

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
    search_fields = ("leitor__nome", "exemplar__livro__titulo", "exemplar__numero_exemplar" )  
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
    
    def relatorio_devedores(self, request):       
            emprestimos_atrasados = models.Emprestimo.objects.filter(
            devolvido=False,
            data_devolucao__lt=date.today()  # Data de devolução menor que hoje (atraso)
        ).select_related('leitor', 'exemplar')  # Evita consultas adicionais para leitor/exemplar
    
            # Ordena pelo empréstimo mais antigo
            emprestimos_atrasados = emprestimos_atrasados.order_by('data_devolucao')
            response = HttpResponse(content_type='application/pdf')
            relatorio_devedores = RelatorioDevedores(emprestimos_atrasados, "relatorio-devedores")
            relatorio_devedores.Gerar(response)                
            return response
        
    def relatorio_leitores(self, request):
            leitores= models.Leitor.objects.filter(ativo=True).annotate(
            quantidade_emprestada=Count('emprestimo')
            ).filter(quantidade_emprestada__gt=0).order_by('-quantidade_emprestada')
            response = HttpResponse(content_type='application/pdf')
            relatorio_leitores = RelatorioLeitores(leitores, "relatorio-leitores")
            relatorio_leitores.Gerar(response)            
            return response
                
    def relatorio_emprestimos_mensal(self, request):
        if request.method == 'POST': 
            mes = request.POST.get("mes")
            ano = request.POST.get("ano")
            emprestimos = models.Emprestimo.objects.filter(data_emprestimo__year = ano, data_emprestimo__month=mes).order_by("leitor", "data_emprestimo")
            response = HttpResponse(content_type='application/pdf')
            relatorio_emprestimo = RelatorioEmprestimosMensal(emprestimos, f"relatorio-emprestimos-{mes}-{ano}")
            relatorio_emprestimo.Gerar(response, mes, ano)              
            return response    
        return redirect('..')

    def relatorio_emprestimos_anual(self, request):
        if request.method == 'POST':            
            ano = request.POST.get("ano")
            emprestimos = models.Emprestimo.objects.filter(data_emprestimo__year = ano).order_by("leitor", "data_emprestimo")
            response = HttpResponse(content_type='application/pdf')
            relatorio_emprestimo = RelatorioEmprestimosAnual(emprestimos, f"relatorio-emprestimos-{ano}")
            relatorio_emprestimo.Gerar(response, ano)              
            return response    
        return redirect('..')
      
    # Adiciona a ação no Admin
    change_list_template = "admin/emprestimo_changelist.html"
    
    def get_urls(self):
        """Adiciona a URL personalizada."""
        urls = super().get_urls()
        custom_urls = [
            path('relatorio_devedores/', self.admin_site.admin_view(self.relatorio_devedores), name='relatorio_devedores'),
            path('relatorio_leitores/', self.admin_site.admin_view(self.relatorio_leitores), name='relatorio_leitores'),
            path('relatorio_emprestimos_mensal/', self.admin_site.admin_view(self.relatorio_emprestimos_mensal), name='relatorio_emprestimos_mensal'),
            path('relatorio_emprestimos_anual/', self.admin_site.admin_view(self.relatorio_emprestimos_anual), name='relatorio_emprestimos_anual'),
        ]
        return custom_urls + urls     
    
class ExemplarAdmin(admin.ModelAdmin):
    form = forms.ExemplarAdminForm
    list_display = ("id", "livro", "tombo", "numero_exemplar", "baixa", "etiqueta_gerada" )
    list_display_links = ("id", "livro", "tombo")
    list_editable = ("baixa","etiqueta_gerada")        
    search_fields = ("id", "livro__titulo","numero_exemplar")  
    ordering = ("id",)      
    autocomplete_fields = ["livro"] 
    list_per_page = 30
    fieldsets = (
    (None, {
        "fields": ("livro", "tombo", "numero_exemplar", "baixa", "etiqueta_gerada", "quantidade"),
    }),
    )  
    list_filter =  ("etiqueta_gerada",)
    actions =[gerar_pdf_etiquetas]  
       
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
    list_display_links = ("id","nome", "ra")
    list_per_page = 30
    ordering = ("id",)
    list_editable = ("ativo",)   
    
    def importar_csv(self, request):
        if request.method == 'POST':         
            try:
                lista_leitores = tratamento_dados.ajustar_csv_leitores(request.FILES
                                                                       ["csv_file"])  
                tratamento_dados.salvar_leitor(lista_leitores)         
                # Armazene a mensagem no sistema de mensagens ou na sessão     
                self.message_user(request, "Leitores importados com sucesso!", messages.SUCCESS)
                return redirect('..')          
            except StopIteration:
                 self.message_user(request, f"Arquivo inválido.", messages.ERROR)
                 return redirect('..')         
            

    # Adiciona a ação no Admin
    change_list_template = "admin/leitor_changelist.html"
    
    def get_urls(self):
        """Adiciona a URL personalizada."""
        urls = super().get_urls()
        custom_urls = [
            path('importar-csv/', self.admin_site.admin_view(self.importar_csv), name='importar_csv'),
        ]
        return custom_urls + urls

class LivroAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "subtitulo", "ano", "edicao", "iniciais_titulo", "isbn")
    search_fields = ("titulo","isbn")
    list_display_links = ("id", "titulo", "subtitulo")
    ordering = ("id",)
    list_per_page = 30
    autocomplete_fields = ["cdd", "editora", "local_publicacao"] 
    inlines = [LivroTemAutorInline]    

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

