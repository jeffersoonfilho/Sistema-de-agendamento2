import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import csv
import os

# Dados dos horários (sem valores base por horário)
horarios = [
    "09:00 - 10:00",
    "10:00 - 11:00",
    "11:00 - 12:00",
    "13:00 - 14:00",
    "14:00 - 15:00",
    "15:00 - 16:00",
]

# Descrições modernas e simples para cada horário (estilo clean, minimalista com emojis e palavras-chave)
DESCRICOES = [
    "Manhã Energizada 💅",
    "Brilho Matinal ☀️",
    "Relax Rápido 🍃",
    "Tarde Premium 👑",
    "Happy Hour ✨",
    "Glow Final 🔥",
]

# Opções de serviços e valores adicionais (agora o valor total é apenas do serviço)
SERVICOS = {
    "Manicure simples": 35.0,
    "Pedicure simples": 35.0,
    "Manicure simples e pedicure simples": 60.0,
    "Aplicação na tips": 100.0,
    "Manutenção": 70.0,
    "Esmaltação em gel": 60.0,
    "Aplicação fibra de vidro": 110.0,
    "Manutenção fibra de vidro": 80.0,
}

# Serviços que envolvem aplicação de unha (para mostrar observação)
SERVICOS_APLICACAO = ["Aplicação na tips", "Aplicação fibra de vidro"]

ARQUIVO_AGENDAMENTOS = "agendamentos.csv"
ATENDENTES = ["Allany", "Vivian"]

def migrar_csv_antigo():
    """Migra arquivo CSV antigo (5 colunas) para novo formato (6 colunas, com valor_horario = 0)."""
    if not os.path.isfile(ARQUIVO_AGENDAMENTOS):
        return

    try:
        with open(ARQUIVO_AGENDAMENTOS, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader, None)
            if len(header) != 5 or header != ["Nome", "Atendente", "Horário", "Serviço", "Valor"]:
                return  # Não é formato antigo, ignora

            # É formato antigo: lê e converte
            agendamentos_antigos = []
            for row in reader:
                if len(row) >= 5:
                    agendamentos_antigos.append(row)

        if agendamentos_antigos:
            novos_agendamentos = []
            for row in agendamentos_antigos:
                nome, atendente, horario, servico, valor_str = row
                valor_servico = float(valor_str)  # O valor antigo é agora o total (apenas serviço)
                valor_horario = 0.0  # Sem valor de horário
                valor_total = valor_servico
                novos_agendamentos.append([nome, atendente, horario, servico, valor_horario, valor_total])

            # Reescreve o arquivo no novo formato
            with open(ARQUIVO_AGENDAMENTOS, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Nome", "Atendente", "Horário", "Serviço", "Valor Horário", "Valor Total"])
                for row in novos_agendamentos:
                    writer.writerow(row)

            messagebox.showinfo("Migração", "Arquivo de agendamentos migrado para o novo formato com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro na Migração", f"Erro ao migrar CSV: {str(e)}\nO arquivo pode estar corrompido.")

def carregar_agendados():
    """Lê o arquivo CSV e retorna os horários já reservados por atendente (independente do serviço)."""
    agendados = {}
    if not os.path.isfile(ARQUIVO_AGENDAMENTOS):
        return agendados

    try:
        with open(ARQUIVO_AGENDAMENTOS, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # pular cabeçalho
            for row in reader:
                if len(row) >= 6:
                    nome, atendente, horario, servico, valor_horario, valor_total = row
                    agendados[(atendente, horario)] = (nome, servico, float(valor_horario), float(valor_total))
                # Ignora linhas com menos colunas (compatibilidade)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar agendamentos: {str(e)}")
    return agendados

def salvar_agendamento(nome, atendente, horario, servico, valor_horario, valor_total):
    file_exists = os.path.isfile(ARQUIVO_AGENDAMENTOS)
    try:
        with open(ARQUIVO_AGENDAMENTOS, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Nome", "Atendente", "Horário", "Serviço", "Valor Horário", "Valor Total"])
            writer.writerow([nome, atendente, horario, servico, valor_horario, valor_total])
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar agendamento: {str(e)}")

def sobrescrever_agendamentos(agendamentos_restantes):
    """Regrava o arquivo CSV com a lista atualizada de agendamentos (aceita lista de rows)."""
    try:
        with open(ARQUIVO_AGENDAMENTOS, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Nome", "Atendente", "Horário", "Serviço", "Valor Horário", "Valor Total"])
            for row in agendamentos_restantes:
                # Garante que row tem 6 itens (pad com 0 se necessário para compatibilidade)
                while len(row) < 6:
                    row.append("0.0")
                writer.writerow(row[:6])  # Limita a 6 colunas
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao sobrescrever agendamentos: {str(e)}")

def atualizar_tree():
    """Atualiza a tree com horários disponíveis para a atendente selecionada."""
    tree.delete(*tree.get_children())  # Limpa a tree
    atendente_sel = combo_atendente.get()
    if not atendente_sel:
        return
    horarios_agendados = carregar_agendados()
    for i, h in enumerate(horarios):
        if (atendente_sel, h) not in horarios_agendados:
            descricao = DESCRICOES[i]
            tree.insert("", tk.END, values=(h, descricao))

def escolher_servico():
    """Abre uma janela para escolher o serviço."""
    janela_servico = tk.Toplevel(root)
    janela_servico.title("Escolha o Serviço")
    janela_servico.geometry("300x150")
    janela_servico.transient(root)  # Fica na frente da janela principal
    janela_servico.grab_set()  # Modal

    ttk.Label(janela_servico, text="Selecione o serviço:").pack(pady=10)

    combo_servico = ttk.Combobox(janela_servico, values=list(SERVICOS.keys()), state="readonly", width=30)
    combo_servico.pack(pady=5)

    resultado = {"servico": None, "valor": None}

    def confirmar():
        servico_sel = combo_servico.get()
        if not servico_sel:
            messagebox.showwarning("Aviso", "Por favor, selecione um serviço.")
            return
        resultado["servico"] = servico_sel
        resultado["valor"] = SERVICOS[servico_sel]
        janela_servico.destroy()

    def cancelar():
        janela_servico.destroy()

    btn_confirmar = ttk.Button(janela_servico, text="Confirmar", command=confirmar)
    btn_confirmar.pack(pady=5)

    btn_cancelar = ttk.Button(janela_servico, text="Cancelar", command=cancelar)
    btn_cancelar.pack(pady=5)

    # Aguardar seleção
    janela_servico.wait_window()

    return resultado["servico"], resultado["valor"]

def agendar():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Aviso", "Por favor, selecione um horário para agendar.")
        return

    nome_cliente = simpledialog.askstring("Cliente", "Digite o nome do cliente:")
    if not nome_cliente:
        return

    atendente_sel = combo_atendente.get()
    if not atendente_sel:
        messagebox.showwarning("Aviso", "Por favor, selecione uma atendente.")
        return

    item = tree.item(selected[0])
    horario = item["values"][0]  # Pega o horário

    # Escolher serviço
    servico, valor_servico = escolher_servico()
    if not servico:
        return  # Cancelado

    valor_horario_num = 0.0  # Sem valor de horário
    valor_total = valor_servico  # Total é apenas o serviço

    # Verificar se é serviço de aplicação e mostrar observação
    if servico in SERVICOS_APLICACAO:
        messagebox.showinfo(
            "Observação Importante",
            "Será cobrado uma taxa de 5 reais por cada unha quebrada."
        )

    salvar_agendamento(nome_cliente, atendente_sel, horario, servico, valor_horario_num, valor_total)
    messagebox.showinfo(
        "Agendamento",
        f"{nome_cliente}, seu horário {horario} com {atendente_sel} para {servico} foi agendado!\n"
        f"Valor do serviço: R$ {valor_servico:.2f}\n"
        f"Valor total: R$ {valor_total:.2f}",
    )

    tree.delete(selected[0])  # Remove o horário da tree

def mostrar_agendamentos():
    if not os.path.isfile(ARQUIVO_AGENDAMENTOS):
        messagebox.showinfo("Agendamentos", "Nenhum agendamento encontrado.")
        return

    janela_agendamentos = tk.Toplevel(root)
    janela_agendamentos.title("Agendamentos Salvos")
    janela_agendamentos.geometry("750x350")

    tree_agend = ttk.Treeview(
        janela_agendamentos, columns=("nome", "atendente", "horario", "servico", "valor_horario", "valor_total"), show="headings"
    )
    tree_agend.heading("nome", text="Cliente")
    tree_agend.heading("atendente", text="Atendente")
    tree_agend.heading("horario", text="Horário")
    tree_agend.heading("servico", text="Serviço")
    tree_agend.heading("valor_horario", text="Valor Horário (R$)")
    tree_agend.heading("valor_total", text="Valor Total (R$)")
    tree_agend.pack(expand=True, fill=tk.BOTH, pady=10, padx=10)

    # Configurar larguras das colunas para melhor visualização
    tree_agend.column("nome", width=100)
    tree_agend.column("atendente", width=80)
    tree_agend.column("horario", width=100)
    tree_agend.column("servico", width=150)
    tree_agend.column("valor_horario", width=120)
    tree_agend.column("valor_total", width=120)

    # Scrollbar
    scrollbar = ttk.Scrollbar(janela_agendamentos, orient="vertical", command=tree_agend.yview)
    tree_agend.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Ler arquivo CSV e inserir dados
    try:
        with open(ARQUIVO_AGENDAMENTOS, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # pular cabeçalho
            for row in reader:
                if len(row) >= 6:
                    nome, atendente, horario, servico, valor_horario, valor_total = row
                    valor_horario_formatado = f"R$ {float(valor_horario):.2f}"
                    valor_total_formatado = f"R$ {float(valor_total):.2f}"
                    tree_agend.insert("", tk.END, values=(nome, atendente, horario, servico, valor_horario_formatado, valor_total_formatado))
                # Ignora linhas inválidas
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar agendamentos na janela: {str(e)}")

    def cancelar():
        selected = tree_agend.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um agendamento para cancelar.")
            return

        item = tree_agend.item(selected[0])
        nome, atendente, horario, servico, valor_horario_str, valor_total_str = item["values"]
        valor_horario_num = float(valor_horario_str.replace("R$ ", "").replace(",", "."))
        valor_total_num = float(valor_total_str.replace("R$ ", "").replace(",", "."))

        resposta = messagebox.askyesno(
            "Cancelar Agendamento",
            f"Tem certeza que deseja cancelar o agendamento de {nome} com {atendente} às {horario} para {servico}?\n"
            f"Valor total: R$ {valor_total_num:.2f}",
        )
        if not resposta:
            return

        # Remover do arquivo CSV
        agendamentos_restantes = []
        try:
            with open(ARQUIVO_AGENDAMENTOS, mode="r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if len(row) >= 6 and not (row[0] == nome and row[1] == atendente and row[2] == horario and row[3] == servico):
                        agendamentos_restantes.append(row)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler CSV para cancelar: {str(e)}")
            return

        sobrescrever_agendamentos(agendamentos_restantes)

        # Atualizar interface da janela atual
        tree_agend.delete(selected[0])

        # Recarregar a tree principal (para adicionar o horário de volta se disponível para a atendente selecionada)
        root.after(0, atualizar_tree)

        messagebox.showinfo("Cancelado", f"Agendamento de {nome} com {atendente} às {horario} para {servico} foi cancelado.")

    btn_cancelar = ttk.Button(janela_agendamentos, text="Cancelar Agendamento", command=cancelar)
    btn_cancelar.pack(pady=5)

# Criar janela principal
root = tk.Tk()
root.title("Horários e Valores da Manicure")
root.geometry("600x600")  # Aumentado para melhor acomodar as informações

# Migração automática ao iniciar
migrar_csv_antigo()

# Frame para seleção de atendente
frame_atendente = ttk.Frame(root)
frame_atendente.pack(pady=10)

ttk.Label(frame_atendente, text="Selecione a Atendente:").pack(side=tk.LEFT, padx=5)
combo_atendente = ttk.Combobox(frame_atendente, values=ATENDENTES, state="readonly", width=10)
combo_atendente.set(ATENDENTES[0])  # Default: Allany
combo_atendente.pack(side=tk.LEFT, padx=5)

# Evento para atualizar tree ao mudar atendente
def on_atendente_change(event):
    atualizar_tree()

combo_atendente.bind("<<ComboboxSelected>>", on_atendente_change)

tree = ttk.Treeview(root, columns=("horario", "descricao"), show="headings", height=10)  # Aumentado height para mais espaço
tree.heading("horario", text="Horário")
tree.heading("descricao", text="Vibe do Horário")

# Configurar larguras das colunas para melhor visualização (aumentado para descricao)
tree.column("horario", width=120)
tree.column("descricao", width=450)  # Largura aumentada para descrições

# Carregar horários iniciais para a atendente default
atualizar_tree()

tree.pack(pady=10, expand=True, fill=tk.BOTH)

btn_agendar = ttk.Button(root, text="Agendar Horário", command=agendar)
btn_agendar.pack(pady=5)

btn_ver_agendamentos = ttk.Button(root, text="Ver Agendamentos", command=mostrar_agendamentos)
btn_ver_agendamentos.pack(pady=5)

root.mainloop()
