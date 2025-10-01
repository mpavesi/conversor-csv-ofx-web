Conversor de CSV para OFX
Este é um projeto de uma aplicação web simples, desenvolvida em Python com Flask e conteinerizada com Docker, que converte extratos bancários do formato CSV para o formato OFX. O formato OFX (Open Financial Exchange) é amplamente utilizado por softwares de gestão financeira para importar transações.

✨ Funcionalidades
Interface Web Simples: Faça o upload do seu ficheiro CSV diretamente no navegador.

Suporte a Múltiplos Delimitadores: Aceita ficheiros CSV delimitados por ponto e vírgula (;), vírgula (,) ou ponto (.).

Mapeamento Inteligente de Colunas: Identifica automaticamente as colunas de data, descrição e valor, mesmo que tenham nomes diferentes (ex: historico, description, amount).

Tipos de Conta: Permite especificar se o extrato é de uma conta corrente (débito) ou de um cartão de crédito.

Filtro de Transações: Opção para ignorar transações que contenham palavras-chave específicas (ex: "juros", "taxa").

Ambiente Dockerizado: A aplicação é totalmente conteinerizada, garantindo um ambiente de execução consistente e facilitando a sua utilização sem a necessidade de instalar Python ou Flask localmente.

🛠️ Tecnologias Utilizadas
Backend: Python 3.11

Framework Web: Flask

Containerização: Docker & Docker Compose

🚀 Como Executar o Projeto
Para executar esta aplicação, você só precisa ter o Docker e o Docker Compose instalados na sua máquina.

Clone o repositório:

git clone [https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git](https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git)
cd SEU-REPOSITORIO

Construa a imagem e inicie o container:
Na pasta principal do projeto, execute o seguinte comando. Ele irá ler o ficheiro docker-compose.yml, construir a imagem Docker e iniciar a aplicação.

docker-compose up --build

A aplicação estará a ser executada em segundo plano.

Aceda à aplicação:
Abra o seu navegador e aceda a:
http://localhost:5000

📋 Como Utilizar a Interface
Escolha o Ficheiro: Clique em "Escolher ficheiro" e selecione o seu extrato em formato .csv.

Tipo de Conta: Selecione se as transações são de uma "Conta Corrente" ou "Cartão de Crédito".

Delimitador: Escolha o caractere que separa as colunas no seu ficheiro CSV.

Ignorar Palavras (Opcional): Se desejar omitir certas transações, digite as palavras-chave separadas por vírgula (ex: rendimento, iof).

Converter: Clique no botão "Converter" para iniciar o processo. O download do ficheiro convertido.ofx começará automaticamente.

Formato do Ficheiro CSV
Para que a conversão funcione corretamente, o seu ficheiro CSV deve conter, no mínimo, as seguintes colunas:

Uma coluna para a data (ex: Data, Date). Formato esperado: DD/MM/AAAA.

Uma coluna para a descrição (ex: Descrição, Histórico, Description).

Uma coluna para o valor (ex: Valor, Amount).

Projeto desenvolvido para simplificar a importação de extratos bancários em gestores financeiros.