import random
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup

# Tela inicial do aplicativo
class Menu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Orientação do layout
        box = BoxLayout(orientation='vertical')

        # Botões da tela inicial do jogo
        button_jogar = Button(text='JOGAR', on_release=self.mostrar_dificuldades)
        button_regras = Button(text='REGRAS', on_release=self.ir_para_regras)
        button_sair = Button(text='SAIR', on_release=self.sair)

        # Adiciona os botões ao layout
        box.add_widget(button_jogar)
        box.add_widget(button_regras)
        box.add_widget(button_sair)

        # Adiciona o layout à tela
        self.add_widget(box)

    # Método para mostrar um popup com opções de dificuldade
    def mostrar_dificuldades(self, *args):
        layout = BoxLayout(orientation='vertical')

        # Cria um popup para escolher a dificuldade
        popup = Popup(title="Escolha a Dificuldade", content=layout, size_hint=(0.5, 0.5))

        # Cria botões para cada nível de dificuldade
        button_facil = Button(text='FÁCIL', on_release=lambda x: (self.ir_para_jogo(8, 8, 10), popup.dismiss()))
        button_medio = Button(text='MÉDIO', on_release=lambda x: (self.ir_para_jogo(12, 12, 20), popup.dismiss()))
        button_dificil = Button(text='DIFÍCIL', on_release=lambda x: (self.ir_para_jogo(16, 16, 40), popup.dismiss()))
        button_fechar = Button(text='Fechar', on_release=popup.dismiss)

        # Adiciona os botões ao layout do popup
        layout.add_widget(button_facil)
        layout.add_widget(button_medio)
        layout.add_widget(button_dificil)
        layout.add_widget(button_fechar)

        # Abre o popup
        popup.open()

    # Método para ir para a tela do jogo com a configuração escolhida
    def ir_para_jogo(self, linhas, colunas, quantidade_minas, *args):
        self.manager.get_screen('Jogo').criar_novo_jogo(linhas, colunas, quantidade_minas)
        self.manager.current = 'Jogo'

    # Método para ir para a tela de regras
    def ir_para_regras(self, *args):
        self.manager.current = 'Regras'

    # Método para sair do jogo
    def sair(self, *args):
        App.get_running_app().stop()

# Classe que representa um quadrado do campo minado
class QuadradoCampoMinado(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Inicializa as propriedades do quadrado
        self.tem_mina = False
        self.quantidade_minas = 0
        self.revelada = False
        self.marcada_com_bandeira = False

    # Método para detectar toques (cliques) no quadrado
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.button == 'right':
            self.marcar_com_bandeira()
            return True
        return super().on_touch_down(touch)

    # Método para marcar/desmarcar o quadrado com uma bandeira
    def marcar_com_bandeira(self):
        if not self.revelada:
            self.marcada_com_bandeira = not self.marcada_com_bandeira
            self.text = "🚩" if self.marcada_com_bandeira else ""

    # Método para revelar o conteúdo do quadrado
    def revelar(self):
        if not self.marcada_com_bandeira and not self.revelada:
            self.revelada = True
            if self.tem_mina:
                self.text = "X"
                self.background_color = (1, 0, 0, 1)  # Vermelho se tiver mina
            else:
                self.text = str(self.quantidade_minas) if self.quantidade_minas > 0 else ""
                self.background_color = (0, 1, 0, 1) if self.quantidade_minas == 0 else (1, 1, 1, 1)

# Classe que representa a grade do campo minado
class MalhaCampoMinado(GridLayout):
    def __init__(self, linhas=10, colunas=10, quantidade_minas=10, **kwargs):
        super().__init__(**kwargs)
        # Inicializa as propriedades da grade
        self.linhas = linhas
        self.colunas = colunas
        self.quantidade_minas = quantidade_minas
        self.cols = colunas
        self.criar_malha()

    # Método para criar a grade de quadrados
    def criar_malha(self):
        self.clear_widgets()
        self.buttons = [[QuadradoCampoMinado() for _ in range(self.colunas)] for _ in range(self.linhas)]
        
        # Adiciona os quadrados à grade e vincula eventos de clique
        for i, row in enumerate(self.buttons):
            for j, quadrado in enumerate(row):
                quadrado.bind(on_press=lambda instance, x=i, y=j: self.on_button_press(x, y))
                self.add_widget(quadrado)

        # Coloca as minas e calcula o número de minas ao redor de cada quadrado
        self.colocar_minas()
        self.calcular_minas()

    # Método para colocar minas aleatoriamente na grade
    def colocar_minas(self):
        minas_colocadas = 0
        while minas_colocadas < self.quantidade_minas:
            row, col = random.randint(0, self.linhas - 1), random.randint(0, self.colunas - 1)
            if not self.buttons[row][col].tem_mina:
                self.buttons[row][col].tem_mina = True
                minas_colocadas += 1

    # Método para calcular o número de minas ao redor de cada quadrado
    def calcular_minas(self):
        for row in range(self.linhas):
            for col in range(self.colunas):
                if not self.buttons[row][col].tem_mina:
                    self.buttons[row][col].quantidade_minas = sum(
                        self.buttons[i][j].tem_mina
                        for i in range(max(0, row-1), min(self.linhas, row+2))
                        for j in range(max(0, col-1), min(self.colunas, col+2))
                    )

    # Método para lidar com o clique em um quadrado
    def on_button_press(self, row, col):
        quadrado = self.buttons[row][col]

        if quadrado.marcada_com_bandeira or quadrado.revelada:
            return

        if quadrado.tem_mina:
            quadrado.revelar()
            self.revelar_todas_minas()
            self.tela_derrota()
        else:
            self.revelar_area_vazia(row, col)
            self.verificar_vitoria()

    # Método para revelar uma área vazia (sem minas ao redor)
    def revelar_area_vazia(self, row, col):
        if row < 0 or row >= self.linhas or col < 0 or col >= self.colunas:
            return

        quadrado = self.buttons[row][col]

        if quadrado.revelada or quadrado.marcada_com_bandeira:
            return

        quadrado.revelar()

        if quadrado.quantidade_minas == 0:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i != 0 or j != 0:
                        self.revelar_area_vazia(row + i, col + j)

    # Método para revelar todas as minas (quando o jogador perde)
    def revelar_todas_minas(self):
        for row in self.buttons:
            for quadrado in row:
                if quadrado.tem_mina:
                    quadrado.revelar()

    # Método para verificar se o jogador venceu
    def verificar_vitoria(self):
        if all(quadrado.revelada or quadrado.tem_mina for row in self.buttons for quadrado in row):
            self.vitoria_popup()

    # Método para exibir um popup de derrota
    def tela_derrota(self):
        popup = Popup(title='Game Over', content=Button(text='Game Over!\nClique para tentar de novo', on_press=lambda x: self.restart_game(popup)), size_hint=(0.5, 0.5))
        popup.open()

    # Método para exibir um popup de vitória
    def vitoria_popup(self):
        popup = Popup(title='Vitória!', content=Button(text='Você venceu!\nClique para jogar novamente', on_press=lambda x: self.restart_game(popup)), size_hint=(0.5, 0.5))
        popup.open()

    # Método para reiniciar o jogo
    def restart_game(self, popup):
        popup.dismiss()
        self.criar_malha()

# Classe que representa a tela do jogo
class Jogo(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Cria um layout vertical para organizar a grade e o botão de voltar
        self.layout = BoxLayout(orientation='vertical')
        self.campo_minado = MalhaCampoMinado()
        self.botao_voltar = Button(text='Voltar', size_hint=(1, 0.1), on_release=self.voltar_para_menu)
        self.layout.add_widget(self.campo_minado)
        self.layout.add_widget(self.botao_voltar)
        self.add_widget(self.layout)

    # Método para criar um novo jogo com a configuração escolhida
    def criar_novo_jogo(self, linhas, colunas, quantidade_minas):
        self.layout.remove_widget(self.campo_minado)
        self.campo_minado = MalhaCampoMinado(linhas, colunas, quantidade_minas)
        self.layout.add_widget(self.campo_minado)

    # Método para voltar ao menu principal
    def voltar_para_menu(self, *args):
        self.manager.current = 'Menu'

# Classe que representa a tela de regras
class Regras(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Cria um layout vertical para organizar o texto e o botão de voltar
        box = BoxLayout(orientation='vertical')
        label = Label(text="Regras do Campo Minado:\n\n1. Clique para revelar quadrados.\n2. Números indicam minas próximas.\n3. Botão direito para bandeira.\n4. Revele tudo para vencer.", size_hint_y=None, height=300)
        button_voltar = Button(text='Voltar', on_release=self.voltar_para_menu)
        box.add_widget(label)
        box.add_widget(button_voltar)
        self.add_widget(box)

    # Método para voltar ao menu principal
    def voltar_para_menu(self, *args):
        self.manager.current = 'Menu'

# Classe principal do aplicativo
class CampoMinado(App):
    def build(self):
        # Cria um gerenciador de telas e adiciona as telas do jogo
        sm = ScreenManager()
        sm.add_widget(Menu(name='Menu'))
        sm.add_widget(Jogo(name='Jogo'))
        sm.add_widget(Regras(name= 'Regras'))
        return sm

# Inicia o aplicativo
if __name__ == '__main__':
    CampoMinado().run()