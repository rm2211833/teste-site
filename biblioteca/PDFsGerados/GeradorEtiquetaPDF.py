from fpdf import FPDF  # type:ignore


class GerarEtiquetaPDF:

    def __init__(self, exemplares):
       # Valores bases para a etiqueta e espaçamento inicial   
       self._ETIQUETAS_POR_PAGINA = 20
       self._valor_vertical = 10
       self._base_horizontal = 9  
       self.exemplares = exemplares
       self._TAMANHO_FONTE = 10.2
       self._TAMANHO_CORTE = 37
    
    def criar_pdf(self):
        # Definições do tipo papel no FPDF
        self._pdf = self._criar_pdf()
        for i, exemplar in enumerate(self.exemplares):
            if i % self._ETIQUETAS_POR_PAGINA == 0 and i != 0:
                # Inicia uma nova página a cada ETIQUETAS_POR_PAGINA etiquetas
                self._pdf.add_page()
                self._valor_vertical = 10
                self._base_horizontal = 9
            elif i % (self._ETIQUETAS_POR_PAGINA//2) == 0 and i != 0:
                # Salta para a próxima coluna a cada ETIQUETAS_POR_PAGINA//2 etiquetas
                self._valor_vertical = 10
                self._base_horizontal = 104
            self._texto_externa = self._texto_externo(exemplar)
            self._texto_interna = self._texto_interno(exemplar)
          # Primeira etiqueta - externa
            self._etiqueta_externa(exemplar)
          # Segunda etiqueta - interna
            self._etiqueta_interna()
          # Ajuste para próxima leva
            self._valor_vertical += 27
          # Salva o arquivo PDF
        # self.pdf.output('etiquetas.pdf')
        return bytes(self._pdf.output())
    def _etiqueta_externa(self, exemplar):
        self._pdf.set_xy(self._base_horizontal, self._valor_vertical)
        # Adiciona texto com os dados do tombo
        self._pdf.multi_cell(70, 4.5, text=self._texto_externa, align='C')
        # Ajusta o id para o formato correto
        id = str(exemplar.id).rjust(10,"0")       
        # Adiciona código numérico do código de barras
        self._pdf.code39('*'+id+'*', x=self._base_horizontal + 16, y=self._valor_vertical+11, w=0.6, h=7)
        # Reposiciona o ponteiro de inserção de texto
        self._pdf.set_xy(self._base_horizontal, self._valor_vertical+18)
        self._pdf.set_font_size(8)
        self._pdf.cell(70, 5, text=id, align='C')      
        self._pdf.set_font_size(self._TAMANHO_FONTE)
   
    def _etiqueta_interna(self):
        self._pdf.set_xy(self._base_horizontal + 70, self._valor_vertical)
        self._pdf.multi_cell(25, 3.5, text=self._texto_interna, align='C')

    def _corte(self, string: str, tamanho: int):
        # Retorna um texto cortado em um comprimento máximo
        return string[0:min(len(string), tamanho)]
   
    def _texto_externo(self, exemplar):
             
       # Retorna o texto a ser exibido na etiqueta externa
       return (self._corte(str(exemplar.livro.autores.first().autor.nome), self._TAMANHO_CORTE)
               + '\n'
               + self._corte(str(exemplar.livro.titulo), self._TAMANHO_CORTE))
      
    def _texto_interno(self, exemplar):
       
       return (str(exemplar.livro.cdd.nome)
               + '\n'
               +str(exemplar.livro.autores.first().autor.codigo_autor)            
               + '\n'
               + str(exemplar.livro.iniciais_titulo)
               + "\nex. "+ str(exemplar.numero_exemplar)
               + '\n'
               + str(exemplar.tombo))     
   
   
    def _criar_pdf(self):
       pdf = FPDF(format='A4')
       pdf.set_margins(left=4, top=4)
       pdf.set_font('Helvetica', size=self._TAMANHO_FONTE)
       pdf.add_page()
       return pdf
   
   
  