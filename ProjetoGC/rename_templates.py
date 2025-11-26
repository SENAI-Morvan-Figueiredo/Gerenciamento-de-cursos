import os
import shutil

# Lista de apps para processar
apps = [
    "aluno",
    "atividades",
    "avaliacoes_anexos",
    "calendario",
    "cursos",
    "diario",
    "gerenciamento_cursos",
    "login",
    "professor",
    "secretaria",
    "solicitacao"
]

base_dir = "/home/GustavoDutra237/Gerenciamento-de-cursos/ProjetoGC"

def merge_and_rename(old_path, new_path):
    if not os.path.exists(old_path):
        return
    if os.path.exists(new_path):
        # Move arquivos individuais
        for item in os.listdir(old_path):
            s = os.path.join(old_path, item)
            d = os.path.join(new_path, item)
            if os.path.isdir(s):
                merge_and_rename(s, d)
            else:
                if os.path.exists(d):
                    print(f"Arquivo já existe, sobrescrevendo: {d}")
                shutil.move(s, d)
        os.rmdir(old_path)
        print(f"Merged e removida: {old_path} -> {new_path}")
    else:
        os.rename(old_path, new_path)
        print(f"Renomeada: {old_path} -> {new_path}")

for app in apps:
    for folder_type in ["templates", "static"]:
        folder_path = os.path.join(base_dir, app, folder_type)
        if os.path.exists(folder_path):
            for subfolder in os.listdir(folder_path):
                old_subfolder = os.path.join(folder_path, subfolder)
                new_subfolder = os.path.join(folder_path, subfolder.lower())
                if old_subfolder != new_subfolder:
                    merge_and_rename(old_subfolder, new_subfolder)


# import os
# import re

# # Caminho da raiz do seu projeto
# project_root = '/home/GustavoDutra237/Gerenciamento-de-cursos/ProjetoGC'

# # Expressão regular para imports com letra maiúscula no início
# import_pattern = re.compile(r'^\s*(from|import)\s+([A-Z][A-Za-z0-9_]*)')

# for dirpath, dirnames, filenames in os.walk(project_root):
#     for filename in filenames:
#         if filename.endswith('.py'):
#             filepath = os.path.join(dirpath, filename)
#             with open(filepath, 'r', encoding='utf-8') as f:
#                 for i, line in enumerate(f, start=1):
#                     match = import_pattern.match(line)
#                     if match:
#                         print(f'{filepath} (linha {i}): {line.strip()}')
