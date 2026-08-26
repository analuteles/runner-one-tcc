# Runner One — Backend

Backend do sistema Runner One: uma API REST para apoiar a gestão de
operações de uma transportadora (clientes, motoristas, veículos,
pedidos, cargas, entregas, ocorrências, multas, documentação, férias
e relatórios).

Projeto de TCC — Ensino Médio Técnico em Desenvolvimento de Sistemas.

> Este repositório contém **apenas o backend**. O frontend é
> desenvolvido separadamente e consome esta API.

---

## Tecnologias

- Python 3.12+
- Django 5.2 LTS
- Django REST Framework
- django-filter (filtros simples nos endpoints de listagem)
- SQLite (banco de desenvolvimento — ver seção sobre PostgreSQL abaixo)

## Como rodar o projeto localmente

```bash
# 1. Crie e ative um ambiente virtual
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Gere e aplique as migrações (o repositório não vem com
#    migrações prontas — cada ambiente gera as suas)
python manage.py makemigrations
python manage.py migrate

# 4. Crie um usuário administrador (é ele quem acessa a API e o /admin/)
python manage.py createsuperuser

# 5. Rode o servidor de desenvolvimento
python manage.py runserver
```

A API fica disponível em `http://localhost:8000/api/` e o painel
administrativo em `http://localhost:8000/admin/`.

### Autenticando na API

Não existe cadastro/login de cliente ou de motorista — apenas a
equipe interna (usuários criados via `createsuperuser` ou pelo
`/admin/`) acessa a API. Duas formas de autenticar:

- **Token** (recomendado para o frontend): `POST /api/auth/token/`
  com `username` e `password` devolve um token. Envie esse token nas
  próximas requisições no cabeçalho `Authorization: Token <valor>`.
- **Sessão/navegador**: durante o desenvolvimento, é possível fazer
  login pela própria "Browsable API" do DRF em `/api-auth/login/` e
  navegar pela API direto no navegador.

### Rodando os testes

```bash
python manage.py test
```

Os testes cobrem principalmente as regras de negócio das entregas
(início, finalização, cancelamento, status), conforme pedido na
especificação do projeto.

> **Nota sobre este ambiente de desenvolvimento:** o código foi
> escrito e revisado cuidadosamente (sintaxe validada com
> `py_compile`, além de scripts próprios para checar se todo import
> entre apps e todo campo usado nos serializers realmente existe),
> mas o ambiente onde este projeto foi gerado não tinha acesso à
> internet para instalar o Django e rodar `migrate`/`test` de
> verdade. **Rode `python manage.py test` no seu ambiente antes de
> considerar qualquer parte pronta**, e reporte para o time qualquer
> erro encontrado — não deveria haver nenhum, mas é o tipo de coisa
> que só se confirma executando de verdade.

---

## Estrutura do projeto

```
runner_one/
├── manage.py
├── requirements.txt
├── config/            # settings, urls e configuração geral do projeto
├── clientes/
├── motoristas/
├── veiculos/
├── pedidos/
├── cargas/
├── entregas/
├── ocorrencias/
├── multas/
├── documentos/
├── ferias/
└── relatorios/
```

Cada app segue o mesmo padrão: `models.py`, `serializers.py`,
`views.py`, `urls.py`, `admin.py` e `tests.py`.

Veja **[API.md](API.md)** para a documentação completa de todos os
endpoints (método, URL, parâmetros, exemplos de request/response e
erros possíveis) — pensada para ser usada pelo time do frontend.

## Visão geral dos módulos

| App | Responsabilidade |
|---|---|
| `clientes` | Cadastro de clientes (pessoa física ou jurídica) |
| `motoristas` | Cadastro de motoristas, CNH, histórico e desempenho |
| `veiculos` | Cadastro e situação da frota (disponível/em uso/manutenção) |
| `pedidos` | A **solicitação** de entrega feita pelo cliente |
| `cargas` | Tipo de mercadoria, peso e volume de cada pedido |
| `entregas` | A **execução** do pedido: status, motorista, veículo, saída/chegada |
| `ocorrencias` | Problemas registrados durante uma entrega |
| `multas` | Multas associadas a motoristas/veículos |
| `documentos` | Documentação dos motoristas (CNH, ASO, etc.) e sua validade |
| `ferias` | Períodos de férias dos motoristas |
| `relatorios` | Agregações sobre os dados acima (entregas, desempenho, faturamento) |

**Pedido vs. Entrega**, conforme a especificação: o pedido é o que o
cliente solicita; a entrega é a execução desse pedido. Um pedido pode
ganhar uma nova entrega se a anterior for cancelada.

---

## Decisões de design e pequenos ajustes de escopo

A especificação pede que decisões importantes não previstas sejam
sinalizadas em vez de resolvidas silenciosamente. Aqui estão as que
apareceram durante o desenvolvimento:

1. **Campo `valor_frete` em Pedido.** A especificação pede um
   relatório de faturamento (item 24), mas nenhum campo de valor
   estava definido para pedidos/entregas. Foi adicionado
   `valor_frete` (opcional) em `Pedido`, usado pelo relatório de
   faturamento. Sem algum campo de valor, esse relatório não teria
   como existir.

2. **"Excluir" cliente/motorista/veículo = inativar.** A
   especificação já sugeria as duas palavras ("excluir OU
   inativar"). Optamos por inativar (nunca apagar de verdade), para
   não perder o histórico de pedidos/entregas/multas já vinculado a
   esses registros. O endpoint continua sendo `DELETE`, só que por
   baixo dos panos ele marca `ativo = False` (ou `situação =
   INATIVO`, no caso de veículo).

3. **Entregas nunca são excluídas, apenas canceladas.** Excluir uma
   entrega apagaria o histórico operacional da transportadora.
   `DELETE /api/entregas/{id}/` retorna erro orientando a usar
   `POST /api/entregas/{id}/cancelar/`.

4. **Status ATRASADA é recalculado automaticamente.** Sempre que a
   lista ou o detalhe de uma entrega é consultado, o sistema marca
   como `ATRASADA` toda entrega `AGUARDANDO`/`EM_ROTA` cuja data
   prevista já passou — sem precisar de um processo assíncrono
   rodando em segundo plano (o que a especificação pede para
   evitar). Também existe o comando opcional
   `python manage.py atualizar_atrasadas`, caso o time prefira
   agendar essa atualização via cron no servidor.

5. **Status do pedido é calculado, não armazenado.** `Pedido.status`
   é uma propriedade derivada do status da entrega mais recente
   relacionada a ele (ABERTO / EM_ANDAMENTO / CONCLUIDO / CANCELADO).
   Isso evita ter a mesma informação guardada (e possivelmente
   desatualizada) em dois lugares diferentes.

6. **Motorista e veículo só podem ser alterados enquanto a entrega
   está `AGUARDANDO`.** Depois que ela sai para rota (ou é
   concluída/cancelada), a atribuição fica travada — o que é
   consistente com a regra de não permitir "alterações incoerentes"
   pedida na especificação.

---

## Da SQLite para o PostgreSQL

O projeto usa SQLite por padrão para facilitar o desenvolvimento
(nenhum integrante precisa instalar um servidor de banco só para
rodar o projeto). O PostgreSQL faz parte da arquitetura geral do
projeto, mas configurá-lo não fazia parte do escopo desta etapa.
Quando for a hora, o arquivo `config/settings.py` já tem, comentada,
a configuração pronta para trocar — basta instalar `psycopg2-binary`
(já deixado comentado no `requirements.txt`) e descomentar o bloco
`DATABASES`.
