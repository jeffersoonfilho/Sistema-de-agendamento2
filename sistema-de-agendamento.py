import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import csv
import os

# Dados dos horários e valores
horarios = [
    "09:00 - 10:00",
    "10:00 - 11:00",
    "11:00 - 12:00",
    "13:00 - 14:00",
    "14:00 - 15:00",
    "15:00 - 16:00",
]

valores = [
    50.0,
    50.0,
    55.0,
    60.0,
    60.0,
    65.0,
]

ARQUIVO_AGENDAMENTOS = "agendamentos.csv"

def salvar_agendamento(horario, valor):
    file_exists = os.path.isfile(ARQUIVO_AGENDAMENTOS)
    with open(ARQUIVO_AGENDAMENTOS, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Horário", "Valor"])
        writer.writerow([horario, valor])

def agendar():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Aviso", "Por favor, selecione um horário para agendar.")
        return
    item = tree.item(selected[0])
    horario, valor_str = item['values']
    # Remover "R$ " e converter para float
    valor_num = float(valor_str.replace("R$ ", "").replace(",", "."))

    salvar_agendamento(horario, valor_num)
    messagebox.showinfo("Agendamento", f"Agendamento confirmado para o horário {horario}.\nValor: R$ {valor_num:.2f}")

    tree.delete(selected[0])

def mostrar_agendamentos():
    if not os.path.isfile(ARQUIVO_AGENDAMENTOS):
        messagebox.showinfo("Agendamentos", "Nenhum agendamento encontrado.")
        return

    # Criar nova janela
    janela_agendamentos = tk.Toplevel(root)
    janela_agendamentos.title("Agendamentos Salvos")
    janela_agendamentos.geometry("300x250")

    tree_agend = ttk.Treeview(janela_agendamentos, columns=("horario", "valor"), show="headings")
    tree_agend.heading("horario", text="Horário")
    tree_agend.heading("valor", text="Valor (R$)")
    tree_agend.pack(expand=True, fill=tk.BOTH, pady=10, padx=10)

    # Ler arquivo CSV e inserir dados na tabela
    with open(ARQUIVO_AGENDAMENTOS, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # pular cabeçalho
        for row in reader:
            horario, valor = row
            # Formatar valor para exibir com R$
            valor_formatado = f"R$ {float(valor):.2f}"
            tree_agend.insert("", tk.END, values=(horario, valor_formatado))

# Criar janela principal
root = tk.Tk()
root.title("Horários e Valores da Manicure")
root.geometry("350x350")

# Treeview para horários disponíveis
tree = ttk.Treeview(root, columns=("horario", "valor"), show="headings", height=8)
tree.heading("horario", text="Horário")
tree.heading("valor", text="Valor (R$)")

for h, v in zip(horarios, valores):
    tree.insert("", tk.END, values=(h, f"R$ {v:.2f}"))

tree.pack(pady=10, expand=True, fill=tk.BOTH)

# Botões
btn_agendar = ttk.Button(root, text="Agendar Horário", command=agendar)
btn_agendar.pack(pady=5)

btn_ver_agendamentos = ttk.Button(root, text="Ver Agendamentos", command=mostrar_agendamentos)
btn_ver_agendamentos.pack(pady=5)

root.mainloop()