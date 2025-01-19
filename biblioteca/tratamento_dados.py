import csv
from io import TextIOWrapper

from django.db import transaction

from . import models


def ajustar_csv_leitores(arquivo):
    turma = TextIOWrapper(arquivo.file, encoding='utf-8-sig')
    nomes = _pegar_lista(turma, 6)
    nome = nomes[0]
    alunos = {}
    try:
        nome["Situação do Aluno"] != "Ativo"              
    except Exception:
        nomes = _pegar_lista(turma, 2)    
    for nome in nomes:
        if nome["Situação do Aluno"] == "Remanejamento":
            continue
        ativo = nome["Situação do Aluno"] == "Ativo"                
        ra = (nome["RA"]+nome["Dig. RA"]).rjust(13,"0")
        aluno = {"nome": nome["Nome do Aluno"], "ra": ra, "ativo":ativo}
        alunos[ra] = aluno
    return alunos.values()         
    
def salvar_leitor(lista_leitores):
    with transaction.atomic():  # Garante a atomicidade da operação
        for leitor in lista_leitores:
            leitor_cadastrado = models.Leitor.objects.filter(ra=leitor["ra"]).first()
            if not leitor_cadastrado:
               if leitor["ativo"]:
                   models.Leitor.objects.create(
                      nome=leitor["nome"],
                      ra=leitor["ra"],
                      ativo=leitor["ativo"],
                  )    
               continue               
            if leitor_cadastrado.ativo != leitor["ativo"]:                
                leitor_cadastrado.ativo = leitor["ativo"]
                leitor_cadastrado.save()
    
def _pegar_lista(turma, linhas):   
        reader = iter(list(csv.reader(turma, delimiter=';')))
        for _ in range(linhas):
            next(reader)    
        header = next(reader)
        return [dict(zip(header, row)) for row in reader]
