import csv
from io import TextIOWrapper

from django.db import transaction

from . import models


def ajustar_csv_leitores(arquivo):
    turma = TextIOWrapper(arquivo.file, encoding='utf-8-sig')
    nomes = _pegar_lista(turma, 6)
    nome = nomes[0]
    alunos_ativos = []
    try:
        nome["Situação do Aluno"] != "Ativo"              
    except Exception:
        nomes = _pegar_lista(turma, 2)
    for nome in nomes:
        if nome["Situação do Aluno"] != "Ativo":
                continue
        ra = nome["RA"]+nome["Dig. RA"]
        aluno = {"nome": nome["Nome do Aluno"], "ra": ra, "ativo":True}
        alunos_ativos.append(aluno)
    return alunos_ativos         
    
def salvar_leitor(lista_leitores):
    with transaction.atomic():  # Garante a atomicidade da operação
        for leitor in lista_leitores:
            models.Leitor.objects.create(
                nome=leitor["nome"],
                ra=leitor["ra"],
                ativo=leitor["ativo"],
            )    
    
def _pegar_lista(turma, linhas):   
        reader = iter(list(csv.reader(turma, delimiter=';')))
        for _ in range(linhas):
            next(reader)    
        header = next(reader)
        return [dict(zip(header, row)) for row in reader]
