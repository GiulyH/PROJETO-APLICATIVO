from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
import sqlite3
from kivy.graphics import Rectangle, Line
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout

# Definindo cores
primary_color = get_color_from_hex("#4CAF50")  # verde
secondary_color = get_color_from_hex("#FFC107")  # amarelo
background_color = get_color_from_hex("#FFFFFF")  # branco

Window.clearcolor = background_color

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            last_name TEXT NOT NULL,
                            email TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            gender TEXT,
                            repeat_password TEXT)''')
        self.conn.commit()

    def register_user(self, name, last_name, email, password, gender, repeat_password):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''INSERT INTO users (name, last_name, email, password, gender, repeat_password) 
                              VALUES (?, ?, ?, ?, ?, ?)''', (name, last_name, email, password, gender, repeat_password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def login_user(self, email, password):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * FROM users WHERE email = ? AND password = ?''', (email, password))
        user = cursor.fetchone()
        return user

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=10, padding=(30, 30, 30, 30))

        self.name_input = TextInput(hint_text="Nome", multiline=False, background_color=(1, 1, 1, 0.8), font_name='BebasNeue-Regular.otf')
        self.last_name_input = TextInput(hint_text="Sobrenome", multiline=False, background_color=(1, 1, 1, 0.8), font_name='BebasNeue-Regular.otf')
        self.email_input = TextInput(hint_text="E-mail", multiline=False, background_color=(1, 1, 1, 0.8), font_name='BebasNeue-Regular.otf')
        self.password_input = TextInput(hint_text="Senha", password=True, multiline=False, background_color=(1, 1, 1, 0.8), font_name='BebasNeue-Regular.otf')
        self.repeat_password_input = TextInput(hint_text="Repita a Senha", password=True, multiline=False, background_color=(1, 1, 1, 0.8), font_name='BebasNeue-Regular.otf')
        
        # Spinner para seleção de gênero
        self.gender_spinner = Spinner(text='Selecione o gênero', values=('Feminino', 'Masculino', 'Outros'), font_name='BebasNeue-Regular.otf')
        self.gender_spinner.bind(text=self.on_gender_spinner_change)

        # Campo de texto para gênero personalizado, inicialmente oculto
        self.other_gender_input = TextInput(hint_text="Outro (especifique)", multiline=False, background_color=(1, 1, 1, 0.8), opacity=0, font_name='BebasNeue-Regular.otf')

        self.register_button = Button(text="Registrar", background_normal='Botao_resized.png', size_hint=(None, None), size=(100, 50))
        self.register_button.bind(on_press=self.register_user)
        back_button = Button(text="Voltar", size_hint=(None, None), size=(100, 50), background_color=secondary_color, font_name='BebasNeue-Regular.otf')
        back_button.bind(on_press=self.go_back_to_login)

        layout.add_widget(Label(text="Registrar", font_size=36, color=(0, 0, 0, 1), font_name='BebasNeue-Regular.otf'))
        layout.add_widget(self.name_input)
        layout.add_widget(self.last_name_input)
        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.repeat_password_input)
        
        # Adicionando o Spinner e o campo de texto "Outros"
        layout.add_widget(self.gender_spinner)
        layout.add_widget(self.other_gender_input)

        layout.add_widget(self.register_button)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def on_gender_spinner_change(self, spinner, text):
        # Exibir o campo de texto "Outros" apenas se "Outros" for selecionado
        if text == 'Outros':
            self.other_gender_input.opacity = 1
        else:
            self.other_gender_input.opacity = 0

    def register_user(self, instance):
        name = self.name_input.text.strip()
        last_name = self.last_name_input.text.strip()
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()
        repeat_password = self.repeat_password_input.text.strip()
        
        # Verificar se todos os campos estão preenchidos
        if not name or not last_name or not email or not password or not repeat_password:
            self.show_popup("Erro", "Por favor, preencha todos os campos.")
            return
        
        # Obter o valor do gênero do Spinner ou do campo de texto "Outros"
        if self.gender_spinner.text == 'Outros':
            gender = self.other_gender_input.text.strip()
        else:
            gender = self.gender_spinner.text

        if password != repeat_password:
            self.show_popup("Erro", "As senhas não coincidem.")
            return

        db = Database()
        if db.register_user(name, last_name, email, password, gender, repeat_password):
            self.show_popup("Registro bem-sucedido", "Usuário registrado com sucesso!")
            self.go_back_to_login(None)
        else:
            self.show_popup("Erro", "E-mail já cadastrado.")

    def go_back_to_login(self, instance):
        self.parent.current = 'login'

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(None, None), size=(400, 200))
        popup.open()

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = GridLayout(cols=1, spacing=10, padding=(30, 30, 30, 30))

        # Adicionar imagem de fundo
        with layout.canvas.before:
            self.background = Rectangle(source='TelaLogin.jpg', pos=layout.pos, size=layout.size)

        # Definir tamanho dos campos de e-mail e senha
        self.email_input = TextInput(hint_text="E-mail", multiline=False, background_color=(0, 0, 0, 0), size_hint=(None, None), size=(300, 40), font_size=18, font_name='BebasNeue-Regular.otf')
        self.password_input = TextInput(hint_text="Senha", password=True, multiline=False, background_color=(0, 0, 0, 0), size_hint=(None, None), size=(300, 40), font_size=18, font_name='BebasNeue-Regular.otf')

        # Adicionar linha abaixo dos campos de e-mail e senha
        self.email_input.bind(size=self.update_line, pos=self.update_line)
        self.password_input.bind(size=self.update_line, pos=self.update_line)

        login_button = Button(text="Login", background_normal='Botao_resized.png', size_hint=(None, None), size=(100, 40))
        login_button.bind(on_press=self.check_login)

        # Usar GridLayout para posicionar os botões "Registrar" e "Esqueci a senha"
        button_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=40)
        register_button = Button(text="Registrar", size_hint=(None, None), size=(100, 40), background_normal='Botao_resized.png')
        register_button.bind(on_press=self.go_to_register)
        forgot_password_button = Button(text="Esqueci a senha", size_hint=(None, None), size=(150, 40), background_normal='Botao_resized.png')
        forgot_password_button.bind(on_press=self.go_to_forgot_password)

        # Adicionar os botões ao GridLayout de botões
        button_layout.add_widget(register_button)
        button_layout.add_widget(forgot_password_button)

        layout.add_widget(Label(text="Digital Skills Academy", font_size=36, color=(1, 1, 1, 1), font_name='BebasNeue-Regular.otf'))
        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)
        layout.add_widget(login_button)
        layout.add_widget(button_layout)

        self.add_widget(layout)

    def update_line(self, instance, value):
        instance.canvas.after.clear()
        with instance.canvas.after:
            Line(points=[instance.x, instance.y, instance.right, instance.y], width=2)

    def on_size(self, *args):
        self.background.size = self.size
        self.background.pos = self.pos

    def check_login(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()

        # Verificar se o email e a senha foram fornecidos
        if not email or not password:
            self.show_popup("Erro", "Por favor, insira o e-mail e a senha.")
            return

        db = Database()
        user = db.login_user(email, password)
        if user:
            print("Login bem-sucedido")
            print("Usuário:", user)
            self.parent.current = 'home'
        else:
            self.show_popup("Login Falhou", "Usuário ou senha incorretos.")

    def go_to_register(self, instance):
        self.parent.current = 'register'

    def go_to_forgot_password(self, instance):
        self.parent.current = 'forgot_password'

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(None, None), size=(400, 200))
        popup.open()

class ForgotPasswordScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=10, padding=(30, 30, 30, 30))

        self.email_input = TextInput(hint_text="E-mail", multiline=False, background_color=(1, 1, 1, 0.8), size_hint=(None, None), size=(300, 40), font_size=18, font_name='BebasNeue-Regular.otf')
        recover_button = Button(text="Recuperar Senha", background_normal='Botao_resized.png', size_hint=(None, None), size=(100, 40))
        recover_button.bind(on_press=self.recover_password)
        back_button = Button(text="Voltar", size_hint=(None, None), size=(100, 40), background_normal='Botao_resized.png', font_size=18, font_name='BebasNeue-Regular.otf')
        back_button.bind(on_press=self.go_back_to_login)

        layout.add_widget(Label(text="Esqueci a Senha", font_size=36, color=(1, 1, 1, 1), font_name='BebasNeue-Regular.otf'))
        layout.add_widget(self.email_input)
        layout.add_widget(recover_button)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def recover_password(self, instance):
        # Por enquanto, vamos apenas exibir uma mensagem
        self.show_popup("Recuperar Senha", "Instruções de recuperação de senha enviadas para o seu e-mail.")

    def go_back_to_login(self, instance):
        self.parent.current = 'login'

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(None, None), size=(400, 200))
        popup.open()

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical')

        # Add tabs
        tabs = TabbedPanel(do_default_tab=False)
        tabs.add_widget(TabbedPanelHeader(text='Cursos'))
        tabs.add_widget(TabbedPanelHeader(text='Trilhas'))
        tabs.add_widget(TabbedPanelHeader(text='Comunidade'))
        tabs.add_widget(TabbedPanelHeader(text='Perguntas'))
        tabs.add_widget(TabbedPanelHeader(text='Artigos'))
        layout.add_widget(tabs)

       
        search_bar = TextInput(hint_text='Pesquisar...')
        layout.add_widget(search_bar)

      
        level_panel = BoxLayout(orientation='vertical')
        level_panel.add_widget(Label(text='Nível'))
        level_panel.add_widget(Button(text='Iniciante'))
        level_panel.add_widget(Button(text='Intermediário'))
        level_panel.add_widget(Button(text='Avançado'))
        layout.add_widget(level_panel)

       
        categories = GridLayout(cols=2)
        categories.add_widget(Label(text='Saúde'))
        categories.add_widget(Button(text='Saiba Mais'))
        categories.add_widget(Label(text='Gestão'))
        categories.add_widget(Button(text='Saiba Mais'))
        categories.add_widget(Label(text='Programação'))
        categories.add_widget(Button(text='Saiba Mais'))
        layout.add_widget(categories)

        self.add_widget(layout)

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(ForgotPasswordScreen(name='forgot_password'))
        sm.add_widget(HomeScreen(name='home')) 
        return sm
    
if __name__ == "__main__":
    MyApp().run()
