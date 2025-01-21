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
def api(request):
    # Recuperar a mensagem armazenada na sessão, se houver
    mensagem = request.session.pop('mensagem', None)  
    return redirect("/api")


def login_view(request):
    form = AuthenticationForm(request)

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            return redirect("/api")
        else:
            messages.error(request, "Login inválido")

    context = {"form": form}
    return render(request, "login.html", context)

