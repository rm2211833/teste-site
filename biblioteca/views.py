# Create your views here.
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Q
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render

from . import forms, models, tratamento_dados


def inicial(request):
    return render(request, "inicial.html", context={"guia_atual": "inicial"})


def livros(request):    
    if request.method == "GET":
        livros = models.Livro.objects.all()        
    else:
        pesquisa = request.POST["termos_pesquisa"]
        livros = models.Livro.objects.filter(Q(titulo__icontains=pesquisa) | Q(isbn__icontains=pesquisa) | Q(autores__autor__nome__icontains=pesquisa))

    context = {"guia_atual": "Livros", "livros": livros}
    return render(request, "livros.html", context)


def detalhes(request, livro_id):
    livro = get_object_or_404(models.Livro, id=livro_id)
    exemplares = models.Exemplar.objects.filter(livro=livro)
    exemplares_disponiveis = (
        exemplares.annotate(
            emprestimos_ativos=Count(
                "emprestimo", filter=Q(emprestimo__devolvido=False)
            )
        )
        .filter(emprestimos_ativos=0)
        .count()
    )
    autores = livro.autores.select_related("autor")
    context = {
        "guia_atual": "Livros",
        "livro": livro,
        "exemplares": exemplares,
        "autores": autores,
        "exemplares_disponiveis": exemplares_disponiveis,
    }
    return render(request, "detalhes.html", context)


@login_required(login_url="biblioteca:login")
def restrito(request):
    # Recuperar a mensagem armazenada na sessão, se houver
    mensagem = request.session.pop('mensagem', None)
    
    # Contexto padrão com a guia atual e a mensagem (se existente)
    context = {
        "guia_atual": "Restrito",
        "mensagem": mensagem,
    }
    
    return render(request, "restrito.html", context)


def salvar_leitores(request):
    if request.method == 'POST':
        form = forms.UploadCSVLeitores(request.POST, request.FILES)
        if form.is_valid():            
            try:
                lista_leitores = tratamento_dados.ajustar_csv_leitores(request.FILES
                                                                       ["file"])
                tratamento_dados.salvar_leitor(lista_leitores)         
                # Armazene a mensagem no sistema de mensagens ou na sessão
                request.session['mensagem'] = {"situacao": "sucesso", "texto": "Arquivo enviado com sucesso!"}
            except IntegrityError:
                request.session['mensagem'] = {"situacao": "erro", "texto": "Existem leitores já cadastrados com esses dados. Verifique seu arquivo."}
            except Exception as e:
                print(e)
                request.session['mensagem'] = {"situacao": "erro", "texto": "Erro ao enviar o arquivo. Verifique o formulário."}
            # Redirecione para a página /restrito
            return redirect('/restrito')
        else:
            mensagem = {"situacao": "erro", "texto": "Erro ao enviar o arquivo. Verifique o formulário."}
            return render(request, 'restrito.html', {'form': form, 'mensagem': mensagem, "guia_atual": "Restrito"})

    # Caso seja um GET, exiba o formulário vazio
    form = forms.UploadCSVLeitores()
    # Verifique se há mensagem na sessão e remova após exibição
    mensagem = request.session.pop('mensagem', None)
    return render(request, 'restrito.html', {'form': form, 'mensagem': mensagem, "guia_atual": "Restrito"})
    

def login_view(request):
    form = AuthenticationForm(request)

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            return redirect("biblioteca:inicial")
        else:
            messages.error(request, "Login inválido")

    context = {"form": form, "guia_atual": "Login"}
    return render(request, "login.html", context)

