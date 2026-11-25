# Sistema de Gestão para Salão de Beleza

Aplicação web interna desenvolvida em Python com Streamlit e Supabase para gerenciamento completo de agenda, atendimentos, clientes, financeiro, comissões e comunicação via WhatsApp.

## Funcionalidades

* **Dashboard:** Visão geral mensal com métricas de faturamento, atendimentos, ticket médio, comissões e lucro líquido, além de gráficos de desempenho por profissional.
* **Gestão de Clientes (CRM):** Cadastro, busca, edição e exclusão de clientes, com registro automático de última visita e cálculo de próxima manutenção.
* **Agenda:** Agendamento de procedimentos por profissional, controle de status (`agendado`, `confirmado`, `concluido`, `cancelado`, `faltou`) e disparo rápido de confirmação via WhatsApp.
* **Central de Mensagens:** Envio em um clique de lembretes para atendimentos do dia, sugestões automáticas de retorno com base no prazo de manutenção de cada serviço e histórico de envios.
* **Checkout e Vendas:** Registro de atendimentos finalizados, cálculo automático de comissão por serviço/profissional, atualização de retorno do cliente e mensagem pós-atendimento.
* **Controle de Gastos:** Lançamento, categorização, edição e exclusão de despesas operacionais.
* **Relatórios e Exportação:** Análise de faturamento por profissional e serviço, com suporte opcional para exportação direta de planilhas no Google Sheets.
* **Backup:** Download de cópias de segurança em formato CSV para agenda, vendas e gastos.

## Tecnologias Utilizadas

* **Frontend e Interface:** Streamlit (com CSS customizado)
* **Banco de Dados:** Supabase (PostgreSQL)
* **Manipulação de Dados e Gráficos:** Pandas e Plotly Express
* **Integrações:** API do WhatsApp (`wa.me`) e Google Sheets (`gspread` / `google-auth`)

## Estrutura do Banco de Dados (Supabase)

O sistema espera as seguintes tabelas configuradas no projeto Supabase:

* `profissionais` (`id`, `nome`, `ativo`)
* `servicos` (`id`, `nome`, `comissao_evelyn`, `retorno_dias`)
* `clientes` (`id`, `nome`, `whatsapp`, `aniversario`, `observacao`, `ultima_visita`, `proxima_manutencao`)
* `agenda` (`id`, `cliente_id`, `data`, `hora`, `cliente`, `telefone`, `servico`, `profissional`, `status`, `observacao`, `lembrete_enviado`, `confirmacao_enviada`)
* `vendas` (`id`, `cliente_id`, `data`, `cliente`, `valor`, `servico`, `profissional`, `comissao`, `forma_pagamento`, `observacao`)
* `gastos` (`id`, `data`, `descricao`, `valor`, `categoria`, `observacao`)
* `mensagens` (`id`, `cliente_id`, `cliente`, `whatsapp`, `tipo`, `mensagem`, `status`, `data_referencia`)

## Como Executar Localmente

1. **Clone o repositório e acesse a pasta do projeto:**
   ```bash
   git clone <url-do-repositorio>
   cd <pasta-do-projeto>
Crie e ative um ambiente virtual:

Bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
Instale as dependências:

Bash
pip install streamlit pandas plotly supabase gspread google-auth
Configure as credenciais:

Crie um arquivo config.py na raiz do projeto contendo:

Python
APP_NAME = "Nome do Salão"
LOGIN_USER = "usuario"
LOGIN_PASSWORD = "senha"
Crie o arquivo .streamlit/secrets.toml com as chaves do Supabase (e credenciais do Google Cloud, caso utilize a exportação para Sheets):

Ini, TOML
SUPABASE_URL = "[https://seu-projeto.supabase.co](https://seu-projeto.supabase.co)"
SUPABASE_KEY = "sua-chave-anon-ou-service-role"

# Opcional para exportação Google Sheets
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
auth_uri = "[https://accounts.google.com/o/oauth2/auth](https://accounts.google.com/o/oauth2/auth)"
token_uri = "[https://oauth2.googleapis.com/token](https://oauth2.googleapis.com/token)"
auth_provider_x509_cert_url = "[https://www.googleapis.com/oauth2/v1/certs](https://www.googleapis.com/oauth2/v1/certs)"
client_x509_cert_url = "..."
Inicie a aplicação:

Bash
streamlit run app.py
