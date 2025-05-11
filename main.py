import customtkinter as ctk
from tkinter import messagebox
import requests
import json

link = 'https://app-est-4bca6-default-rtdb.firebaseio.com'

class MeuSalario(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Meu Salário")
        self.geometry("300x500")

        self.pages = {}
        for Page in (PagReceitas, PagDespesas, RM, AE):
            page = Page(self)
            self.pages[Page] = page

        self.show_page(PagReceitas)

    def show_page(self, page_class):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[page_class].pack(fill="both", expand=True)

class PagReceitas(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        ctk.CTkLabel(self, text="Cadastro de Receita").pack(pady=20)
        self.valor = ctk.CTkEntry(self, placeholder_text='Valor R$:')
        self.valor.pack(pady=10)

        self.opcoes = ["Renda Fixa", "Renda Variável", "Adicional"]
        self.combo = ctk.CTkOptionMenu(self, values=self.opcoes)
        self.combo.pack(pady=20)

        ctk.CTkButton(self, text='Salvar Receita', command=self.salvar_receita).pack(pady=10)
        ctk.CTkButton(self, text='Ir para Despesas', command=lambda: master.show_page(PagDespesas)).pack(pady=10)

    def salvar_receita(self):
        valor = self.valor.get()
        tipo = self.combo.get()

        if not valor or not tipo:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        try:
            dados = {"valor": float(valor), "tipo": tipo}
            response = requests.post(f'{link}/Ativo.json', data=json.dumps(dados))
            if response.status_code == 200:
                messagebox.showinfo("Sucesso", "Receita salva com sucesso!")
                self.valor.delete(0, "end")
            else:
                messagebox.showerror("Erro", "Falha ao salvar receita no servidor.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar receita: {e}")

class PagDespesas(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        ctk.CTkLabel(self, text="Cadastro de Despesas").pack(pady=20)
        self.valor = ctk.CTkEntry(self, placeholder_text='Valor R$:')
        self.valor.pack(pady=10)

        self.opcoes = ["Fixa", "Variável", "Eventual"]
        self.combo = ctk.CTkOptionMenu(self, values=self.opcoes)
        self.combo.pack(pady=20)

        ctk.CTkButton(self, text='Salvar Despesa', command=self.salvar_despesa).pack(pady=10)
        ctk.CTkButton(self, text='Ir para Relatório', command=lambda: master.show_page(RM)).pack(pady=10)

    def salvar_despesa(self):
        valor = self.valor.get()
        tipo = self.combo.get()

        if not valor or not tipo:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        try:
            dados = {"valor": float(valor), "tipo": tipo}
            response = requests.post(f'{link}/passivo.json', data=json.dumps(dados))
            if response.status_code == 200:
                messagebox.showinfo("Sucesso", "Despesa salva com sucesso!")
                self.valor.delete(0, "end")
            else:
                messagebox.showerror("Erro", "Falha ao salvar despesa no servidor.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar despesa: {e}")

class RM(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Relatório Mensal").pack(pady=20)
        self.resultado_label = ctk.CTkLabel(self, text="")
        self.resultado_label.pack(pady=10)
        ctk.CTkButton(self, text='Atualizar', command=self.calcular_resultado).pack(pady=5)
        ctk.CTkButton(self, text='Ir para Análise de Economia', command=lambda: master.show_page(AE)).pack(pady=10)

    def calcular_resultado(self):
        try:
            receitas = requests.get(f'{link}/Ativo.json').json() or {}
            despesas = requests.get(f'{link}/passivo.json').json() or {}

            total_receitas = sum(item["valor"] for item in receitas.values())
            total_despesas = sum(item["valor"] for item in despesas.values())

            saldo = total_receitas - total_despesas

            cor = "red" if saldo < 0 else "blue"
            texto = f"Saldo: R$ {saldo:.2f}"

            self.resultado_label.configure(text=texto, text_color=cor)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular relatório: {e}")

class AE(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Análise de Economia").pack(pady=20)
        self.resultado_label = ctk.CTkLabel(self, text="")
        self.resultado_label.pack(pady=10)
        ctk.CTkButton(self, text='Gerar Dicas', command=self.analisar_economia).pack(pady=5)
        ctk.CTkButton(self, text='Voltar para Receitas', command=lambda: master.show_page(PagReceitas)).pack(pady=10)

    def analisar_economia(self):
        try:
            despesas = requests.get(f'{link}/passivo.json').json() or {}

            total_por_tipo = {}
            for item in despesas.values():
                tipo = item["tipo"]
                total_por_tipo[tipo] = total_por_tipo.get(tipo, 0) + item["valor"]

            dica = "Dicas de economia:\n"
            for tipo, total in total_por_tipo.items():
                if total > 100:  # exemplo de critério para alto gasto
                    dica += f"- Reduza despesas do tipo {tipo}, você gastou R$ {total:.2f}.\n"

            self.resultado_label.configure(text=dica)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na análise: {e}")

app = MeuSalario()
app.mainloop()
