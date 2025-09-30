# 1. Use uma imagem base oficial e leve
FROM python:3.11-slim

# 2. Defina o diretório de trabalho dentro do container
WORKDIR /app

# 3. Copie APENAS o arquivo de dependências primeiro
# Isso aproveita o cache do Docker. Se o requirements.txt não mudar,
# o Docker não vai reinstalar tudo a cada build.
COPY requirements.txt .

# 4. Instale as dependências dentro do container
# O pip aqui é o do container, não o da sua máquina local.
RUN pip install --no-cache-dir -r requirements.txt

# 5. AGORA, copie o resto do código da sua aplicação
COPY . .

# 6. Exponha a porta que a sua aplicação Flask vai usar
EXPOSE 5000

# 7. Defina o comando para executar a aplicação
# Use a forma de array para evitar problemas com shell
CMD ["python", "app.py"]

