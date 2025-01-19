from datetime import date, datetime, timedelta

from django.db import models


# Função para calcular a data de devolução padrão (hoje + 7 dias)
def get_default_return_date():
    return date.today() + timedelta(days=7)


class Autor(models.Model):
    class Meta:
        verbose_name = "autor"
        verbose_name_plural = "autores"

    def __str__(self):
        return self.nome

    nome = models.CharField(max_length=100)
    codigo_autor = models.CharField(max_length=10, null=True)


class Cdd(models.Model):
    class Meta:
        verbose_name = "CDD"

    def __str__(self):
        return self.nome

    nome = models.CharField(max_length=100)

class Editora(models.Model):
    class Meta:
        verbose_name = "Editora"

    def __str__(self):
        return self.nome

    nome = models.CharField(max_length=100)


class Leitor(models.Model):
    class Meta:
        verbose_name = "leitor"
        verbose_name_plural = "leitores"    
    
    nome = models.CharField(max_length=100)
    ra = models.CharField(max_length=20, unique=True)
    ativo = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.nome}"

class Local_Publicacao(models.Model):
    class Meta:
        verbose_name = "Local de Publicação"
        verbose_name_plural = "Locais de Publicação"

    def __str__(self):
        return self.nome

    nome = models.CharField(max_length=100)


class Livro(models.Model):
    class Meta:
        verbose_name = "livro"
        verbose_name_plural = "livros"

    def __str__(self):
        nome = self.titulo
        if self.subtitulo:
            nome+=" : "+self.subtitulo
        return nome

    titulo = models.CharField(max_length=100)
    subtitulo = models.CharField(max_length=100, blank=True)
    ano = models.IntegerField(blank=True, null=True)
    edicao = models.IntegerField(blank=True, null=True)    
    isbn = models.CharField(max_length=13, blank=True)
    iniciais_titulo=models.CharField(max_length=2)
    cdd = models.ForeignKey(Cdd, on_delete=models.SET_NULL, blank=True, null=True)
    editora = models.ForeignKey(Editora, on_delete=models.SET_NULL, blank=True, null=True)
    local_publicacao = models.ForeignKey(Local_Publicacao, on_delete=models.SET_NULL, blank=True, null=True)

class Exemplar(models.Model):
    class Meta:
        verbose_name = "exemplar"
        verbose_name_plural = "exemplares"

    def __str__(self):
        return f"Ex. {self.numero_exemplar}: {self.livro.titulo}"

    livro = models.ForeignKey(Livro, on_delete=models.SET_NULL, blank=True, null=True)
    tombo = models.CharField(max_length=45)
    numero_exemplar = models.IntegerField(verbose_name="Número de Exemplar")
    etiqueta_gerada = models.BooleanField()
    baixa = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):       
        if not self.tombo:  # Gera apenas se não existir
            ano_atual = datetime.now().year
            self.tombo = f"Crav.{ano_atual}.{self.id or 'ID_TEMP'}"
        if not self.numero_exemplar:
            ultimo_exemplar = Exemplar.objects.filter(livro=self.livro).order_by('-numero_exemplar').first()
            ultimo_numero = ultimo_exemplar.numero_exemplar if ultimo_exemplar else 0
            self.numero_exemplar = ultimo_numero + 1
        super().save(*args, **kwargs)    
        if 'ID_TEMP' in self.tombo:
            self.tombo = f"Crav.{datetime.now().year}.{self.id}"
            super().save(*args, **kwargs)


class Emprestimo(models.Model):
    class Meta:
        verbose_name = "empréstimo"
        verbose_name_plural = "empréstimos"

    def __str__(self):
        return f"Empréstimo de {self.exemplar.livro.titulo}"

    leitor = models.ForeignKey(Leitor, on_delete=models.SET_NULL, blank=True, null=True)
    exemplar = models.ForeignKey(
       Exemplar, on_delete=models.SET_NULL, blank=True, null=True
    )
    data_emprestimo = models.DateField(default=date.today, verbose_name="Data de Empréstimo")
    data_devolucao = models.DateField(default=get_default_return_date, verbose_name="Data de Devolução")
    devolvido = models.BooleanField(default=False)

class LivroTemAutor(models.Model):
    class Meta:
        verbose_name = "Livro e Autor"
        verbose_name_plural = "Livros e Autores"

    def __str__(self):
        return f"Autor: {self.autor.nome}, Livro: {self.livro.titulo}"

    autor = models.ForeignKey(Autor, on_delete=models.SET_NULL, blank=True, null=True, related_name="livros")
    livro = models.ForeignKey(Livro, on_delete=models.SET_NULL, blank=True, null=True, related_name="autores")