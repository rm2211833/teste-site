# Create your views here.
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from . import forms, models


def inicial(request):
    return render(request, "inicial.html", context={"guia_atual": "inicial"})


def livros(request):
    if request.method == "GET":
        livros = models.Livro.objects.all()
    else:
        pesquisa = request.POST["termos_pesquisa"]
        livros = models.Livro.objects.filter(nome__icontains=pesquisa)

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
    autores = livro.livrotemautor_set.select_related("autor")
    context = {
        "guia_atual": "Livros",
        "livro": livro,
        "exemplares": exemplares,
        "autores": autores,
        "exemplares_disponiveis": exemplares_disponiveis,
    }
    return render(request, "detalhes.html", context)


@login_required(login_url="biblioteca:login")
def emprestimos(request):
    emprestimos = models.Emprestimo.objects.filter(leitor=request.user)
    context = {"guia_atual": "Empréstimos", "emprestimos": emprestimos}
    return render(request, "emprestimos.html", context)


def register(request):
    form = forms.RegisterForm()
    context = {
        "guia_atual": "Cadastrar",
        "form": form,
    }

    if request.method == "POST":
        form = forms.RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Usuário registrado")
            return redirect("biblioteca:login")

    return render(request, "create_user.html", context)


@login_required(login_url="biblioteca:login")
def user_update(request):
    form = forms.RegisterUpdateForm(instance=request.user)

    if request.method != "POST":
        return render(
            request, "user_update.html", {"guia_atual": "Perfil", "form": form}
        )

    form = forms.RegisterUpdateForm(data=request.POST, instance=request.user)

    if not form.is_valid():
        return render(
            request, "user_update.html", {"guia_atual": "Perfil", "form": form}
        )

    form.save()
    return redirect("biblioteca:user_update")


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


@login_required(login_url="biblioteca:login")
def logout_view(request):
    auth.logout(request)
    return redirect("biblioteca:login")
