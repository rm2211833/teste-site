from datetime import date, datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)


class Relatorio():
    def __init__(self, dados, nome_relatorio):
        self._dados = dados
        self._nome_relatorio = nome_relatorio
        
    def Gerar(self, response):
        data_e_hora = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        response['Content-Disposition'] = f'attachment; filename="{self._nome_relatorio}-{data_e_hora}.pdf"'
        self._pdf = SimpleDocTemplate(response, pagesize=A4, leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
    
    def _config_tabela(self, dados, col_width=None):
        table = Table(dados, col_width)
       
        table.setStyle(         TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Cabeçalho cinza
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texto branco no cabeçalho
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Centraliza o texto
            ('VALIGN', (-1, -1), (-1, -1), 'MIDDLE'),  # Centraliza o texto
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Cabeçalho em negrito
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),  # Espaçamento no cabeçalho
            ('TOPPADDING', (0, 0), (-1, 0), 6),  # Espaçamento no cabeçalho
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Fundo branco para os dados
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grade preta
        ]))
        return table
        
    def _titulo_pdf(self, titulo):
        styles = getSampleStyleSheet()
        titulo_style = styles['Title']
        data_atual = date.today().strftime("%d/%m/%Y")
        return Paragraph(f"{titulo} - {data_atual}", titulo_style)
        
        
class RelatorioDevedores(Relatorio):           
    def Gerar(self, response):        
        super().Gerar(response)       
        emprestimos = self._dados    
        # Cabeçalho da tabela
        dados = [["Leitor", "Exemplar", "Data de Empréstimo", "Data de Devolução", "Dias de Atraso"]]
        titulo = self._titulo_pdf("Relatório de Devedores")
        
        # Preenchendo os dados
        for emprestimo in emprestimos:
            dias_atraso = (date.today() - emprestimo.data_devolucao).days
            dados.append([
                emprestimo.leitor.nome,
                emprestimo.exemplar.livro.titulo,
                emprestimo.data_emprestimo.strftime("%d/%m/%Y"),
                emprestimo.data_devolucao.strftime("%d/%m/%Y"),
                dias_atraso,
            ])
           
        table = self._config_tabela(dados)       
        elementos =[titulo, Spacer(1,10), table]
        self._pdf.build(elementos)
        
class RelatorioLeitores(Relatorio):
    def Gerar(self, response):
        super().Gerar(response)       
        leitores = self._dados    
        # Cabeçalho da tabela
        dados = [["Leitor", "Quantidade de Empréstimos"]]
        titulo = self._titulo_pdf("Relatório de Empréstimos por Leitor")
        
        # Preenchendo os dados
        for leitor in leitores:            
            dados.append([
                leitor.nome,
                leitor.quantidade_emprestada,                               
            ])
        col_widths = [530 / len(dados[0])] * len(dados[0])   
        table = self._config_tabela(dados, col_widths)       
        elementos =[titulo, Spacer(1,10), table]
        self._pdf.build(elementos)
        
class RelatorioEmprestimosMensal(Relatorio):
    def Gerar(self, response, mes, ano):
        super().Gerar(response)       
        emprestimos = self._dados    
        # Cabeçalho da tabela
        dados = [["Leitor", "Exemplar", "Data de Devolução", "Devolvido"]]
        mes = mes.rjust(2,"0")
        titulo = self._titulo_pdf(f"Relatório de Empréstimos de {mes}/{ano}")
        
        valor_quantidade = len(emprestimos)
        estilo = getSampleStyleSheet()["Normal"]
        estilo.fontSize=12
        quantidade = Paragraph(f"<b>Total de empréstimos:</b> {valor_quantidade}.", estilo)

        # Preenchendo os dados
        for emprestimo in emprestimos:            
            obra = f"(ID: {emprestimo.exemplar.id}) {emprestimo.exemplar.livro.titulo}"
            data = emprestimo.data_devolucao.strftime('%d/%m/%Y')
            devolvido = "Sim" if emprestimo.devolvido else "Não"
            dados.append([
                emprestimo.leitor.nome,
                obra,                
                data,
                devolvido,                            
            ])        
        table = self._config_tabela(dados)       
        elementos =[titulo, Spacer(1,10), quantidade, Spacer(1,15), table]
        self._pdf.build(elementos)
        
class RelatorioEmprestimosAnual(Relatorio):
    def Gerar(self, response, ano):
        super().Gerar(response)       
        emprestimos = self._dados    
        # Cabeçalho da tabela
        dados = [["Leitor", "Exemplar", "Data de Devolução", "Devolvido"]]        
        titulo = self._titulo_pdf(f"Relatório de Empréstimos de {ano}")
        
        valor_quantidade = len(emprestimos)
        estilo = getSampleStyleSheet()["Normal"]
        estilo.fontSize=12
        quantidade = Paragraph(f"<b>Total de empréstimos:</b> {valor_quantidade}.", estilo)

        # Preenchendo os dados
        for emprestimo in emprestimos:            
            obra = f"(ID: {emprestimo.exemplar.id}) {emprestimo.exemplar.livro.titulo}"
            data = emprestimo.data_devolucao.strftime('%d/%m/%Y')
            devolvido = "Sim" if emprestimo.devolvido else "Não"
            dados.append([
                emprestimo.leitor.nome,
                obra,                
                data,
                devolvido,                            
            ])
        # col_widths = [530 / len(dados[0])] * len(dados[0])   
        table = self._config_tabela(dados)       
        elementos =[titulo, Spacer(1,10), quantidade, Spacer(1,15), table]
        self._pdf.build(elementos)