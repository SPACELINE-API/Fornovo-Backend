## Fornovo Backend - Documentação Técnica

Estrutura de Pastas:
🔹 core/
Contém as configurações globais do Django.

settings.py: Configurações de banco de dados, middlewares e registro de apps.
urls.py: O "porteiro" principal que delega as rotas para as aplicações específicas.

🔹 apps/
Diretório onde reside toda a lógica de negócio do sistema:

projetos/: Gestão do ciclo de vida das obras (Cadastro, listagem e status).

usuarios/: Autenticação e níveis de acesso (Admin, Engenheiro, Projetista).

calculos/: Motores de cálculo para memoriais técnicos e levantamento de campo.

🔹 utils/
Scripts auxiliares, validadores e funções matemáticas globais.

Como criar novas Apps
Para manter a organização e evitar erros, pfv siga este padrão ao criar novas funcionalidades:

1. Comando de Criação
Execute a partir da pasta raiz (ForBack/):

python manage.py startapp nome_da_app ./apps/nome_da_app

2. Ajuste Obrigatório no apps.py
Vá até apps/nome_da_app/apps.py e configure o caminho:

class NomeDaAppConfig(AppConfig):
    name = 'apps.nome_da_app' 

3. Registro no settings.py
Adicione a nova aplicação na lista INSTALLED_APPS em core/settings.py:

Python

INSTALLED_APPS = [
    ...
    'apps.nome_da_app',
]

4. Configuração de Rotas (URLs)
Crie um arquivo urls.py dentro da pasta da sua nova app.

Registre esse arquivo no core/urls.py usando a função include().

Como executar o projeto
Certifique-se de que o ambiente virtual está ativo: .\.venv\Scripts\Activate.ps1

Navegue até a pasta do projeto: cd ForBack

Inicie o servidor: python manage.py runserver

--------------------------------------------------------------------------

## Guia de Banco de Dados (Migrations)
Para quem for responsável pela modelagem do banco de dados, favor seguir este fluxo para garantir que as tabelas sejam criadas corretamente dentro da estrutura modular:

1. Criando as Migrações
Sempre que alterar um arquivo models.py, rode o comando na raiz (ForBack/):

python manage.py makemigrations

O Django detectará automaticamente os modelos dentro de apps/ graças à configuração do apps.py e do settings.py.

2. Aplicando as Mudanças
Para refletir as alterações no banco de dados:

python manage.py migrate

3. Atenção com as Apps
Certifique-se de que a App está registrada em INSTALLED_APPS no core/settings.py antes de rodar os comandos, caso contrário, o Django ignorará os modelos daquela pasta.