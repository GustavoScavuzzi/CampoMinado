import random
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup

class Menu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        box = BoxLayout(orientation='vertical')
        button = Button(text='JOGAR')
        button2 = Button(text='REGRAS', on_release=self.ir_para_regras)
        button3 = Button(text='SAIR', on_release=self.sair)
        
        button.bind(on_release=self.ir_para_jogo)
        
        box.add_widget(button)
        box.add_widget(button2)
        box.add_widget(button3)
        self.add_widget(box)

    def ir_para_jogo(self, *args):
        self.manager.current = 'Jogo'

    def ir_para_regras(self, *args):
        self.manager.current = 'Regras'

    def sair(self, *args):
        App.get_running_app().stop()

class QuadradoCampoMinado(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tem_mina = False
        self.quantidade_minas = 0
        self.revelada = False
        self.marcada_com_bandeira = False  

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button == 'right':  
                self.marcar_com_bandeira()
                return True
        return super().on_touch_down(touch)

    def marcar_com_bandeira(self):
        if not self.revelada: 
            self.marcada_com_bandeira = not self.marcada_com_bandeira  
            self.text = "🚩" if self.marcada_com_bandeira else ""  

    def revelar(self):
        if not self.marcada_com_bandeira:  
            if self.tem_mina:
                self.text = "X"
                self.revelada = True
            else:
                self.text = str(self.quantidade_minas)
                self.revelada = True

class MalhaCampoMinado(GridLayout):
    def __init__(self, linhas=10, colunas=10, quantidade_minas=10, **kwargs):
        super().__init__(**kwargs)
        self.linhas = linhas
        self.colunas = colunas
        self.quantidade_minas = quantidade_minas
        self.buttons = []
        self.cols = colunas 
        self.criar_malha()

    def criar_malha(self):
        self.clear_widgets()
        self.buttons = []
        for row in range(self.linhas):
            row_buttons = []
            for col in range(self.colunas):
                quadrado = QuadradoCampoMinado()
                quadrado.bind(on_press=self.on_button_press)
                self.add_widget(quadrado)
                row_buttons.append(quadrado)
            self.buttons.append(row_buttons)
        self.colocar_minas()
        self.calcular_minas()

    def colocar_minas(self):
        minas_colocadas = 0
        while minas_colocadas < self.quantidade_minas:
            row = random.randint(0, self.linhas - 1)
            col = random.randint(0, self.colunas - 1)
            if not self.buttons[row][col].tem_mina:
                self.buttons[row][col].tem_mina = True
                minas_colocadas += 1

    def calcular_minas(self):
        for row in range(self.linhas):
            for col in range(self.colunas):
                if not self.buttons[row][col].tem_mina:
                    self.buttons[row][col].quantidade_minas = self.count_adjacent_mines(row, col)

    def count_adjacent_mines(self, row, col):
        count = 0
        for i in range(max(0, row-1), min(self.linhas, row+2)):
            for j in range(max(0, col-1), min(self.colunas, col+2)):
                if self.buttons[i][j].tem_mina:
                    count += 1
        return count

    def on_button_press(self, instance):
        if not instance.marcada_com_bandeira: 
            if instance.tem_mina:
                instance.text = "X"
                self.revelar_todas_minas()
                self.tela_derrota()
            else:
                instance.revelar()
                if instance.quantidade_minas == 0:
                    self.revelar_quadrados(instance)
                self.verificar_vitoria()  

    def revelar_quadrados(self, instance):
        for row in range(self.linhas):
            for col in range(self.colunas):
                if self.buttons[row][col] == instance:
                    self.reveal_cells(row, col)
                    break

    def reveal_cells(self, row, col):
        for i in range(max(0, row-1), min(self.linhas, row+2)):
            for j in range(max(0, col-1), min(self.colunas, col+2)):
                if not self.buttons[i][j].revelada and not self.buttons[i][j].marcada_com_bandeira:
                    self.buttons[i][j].revelar()
                    if self.buttons[i][j].quantidade_minas == 0:
                        self.reveal_cells(i, j)

    def revelar_todas_minas(self):
        for row in range(self.linhas):
            for col in range(self.colunas):
                if self.buttons[row][col].tem_mina:
                    self.buttons[row][col].text = "X"

    def verificar_vitoria(self):
        for row in range(self.linhas):
            for col in range(self.colunas):
                if not self.buttons[row][col].tem_mina and not self.buttons[row][col].revelada:
                    return  
        self.vitoria_popup()  

    def tela_derrota(self):
        content = Button(text='Game Over!\nClique para tentar de novo')
        popup = Popup(title='Game Over', content=content, size_hint=(0.5, 0.5))
        content.bind(on_press= lambda quadrado: self.restart_game(popup))
        popup.open()

    def vitoria_popup(self):
        content = Button(text='Você venceu!\nClique para jogar novamente')
        popup = Popup(title='Vitória!', content=content, size_hint=(0.5, 0.5))
        content.bind(on_press=lambda quadrado: self.restart_game(popup))
        popup.open()

    def restart_game(self, popup):
        popup.dismiss()
        self.criar_malha()

class Jogo(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        campo_minado = MalhaCampoMinado()
        botao_voltar = Button(text='Voltar', size_hint=(1, 0.1), on_release=self.voltar_para_menu)
        layout.add_widget(campo_minado)
        layout.add_widget(botao_voltar)
        self.add_widget(layout)

    def voltar_para_menu(self, *args):
        self.manager.current = 'Menu'

class Regras(Screen):
    def __init__(self, **kwargs):  
        super().__init__(**kwargs)  
        box = BoxLayout(orientation='vertical')
        label = Label(
            text='Regras do Campo Minado:\n\n1. Clique para revelar quadrados.\n2. Os números indicam minas próximas.\n3. Use o botão direito para colocar bandeira\n4. Revele todos os quadrados seguros para vencer.',
            font_size=20,
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=400, 
            text_size=(None, None)
        )
        button_voltar = Button(text='Voltar', on_release=self.voltar_para_menu)
        
        box.add_widget(label)
        box.add_widget(button_voltar)
        self.add_widget(box)

    def voltar_para_menu(self, *args):
        self.manager.current = 'Menu'

class CampoMinado(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Menu(name='Menu'))
        sm.add_widget(Jogo(name='Jogo'))
        sm.add_widget(Regras(name='Regras'))
        return sm

if __name__ == '__main__':
    CampoMinado().run()