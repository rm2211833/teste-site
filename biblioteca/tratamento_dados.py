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
        leitores_existentes = models.Leitor.objects.filter(ra__in=[leitor["ra"] for leitor in lista_leitores])
        leitores_por_ra = {leitor.ra: leitor for leitor in leitores_existentes}

        novos_leitores = []
        leitores_para_atualizar = []

        for leitor in lista_leitores:
            leitor_cadastrado = leitores_por_ra.get(leitor["ra"])
            
            if not leitor_cadastrado:
                if leitor["ativo"]:
                    novos_leitores.append(models.Leitor(
                        nome=leitor["nome"],
                        ra=leitor["ra"],
                        ativo=leitor["ativo"],
                    ))
            elif leitor_cadastrado.ativo != leitor["ativo"]:
                leitor_cadastrado.ativo = leitor["ativo"]
                leitores_para_atualizar.append(leitor_cadastrado)
        
        # Inserção em lote para novos leitores
        if novos_leitores:
            models.Leitor.objects.bulk_create(novos_leitores)
        
        # Atualização em lote para leitores existentes
        if leitores_para_atualizar:
            models.Leitor.objects.bulk_update(leitores_para_atualizar, ['ativo'])
    
def _pegar_lista(turma, linhas):   
        reader = iter(list(csv.reader(turma, delimiter=';')))
        for _ in range(linhas):
            next(reader)    
        header = next(reader)
        return [dict(zip(header, row)) for row in reader]
