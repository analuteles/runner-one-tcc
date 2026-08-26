# Documentação da API — Runner One

Base URL local: `http://localhost:8000/api/`

Todas as respostas são em JSON. Todos os endpoints (exceto obtenção
de token) exigem autenticação — veja o [README](README.md#autenticando-na-api).

Listagens são paginadas (20 itens por página) no formato padrão do
Django REST Framework:

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/clientes/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

## Sumário

- [Autenticação](#autenticação)
- [Clientes](#clientes)
- [Motoristas](#motoristas)
- [Veículos](#veículos)
- [Pedidos](#pedidos)
- [Cargas](#cargas)
- [Entregas](#entregas)
- [Ocorrências](#ocorrências)
- [Multas](#multas)
- [Documentos](#documentos)
- [Férias](#férias)
- [Relatórios](#relatórios)
- [Formato de erros](#formato-de-erros)

---

## Autenticação

### `POST /api/auth/token/`
**Finalidade:** trocar usuário/senha por um token de acesso.
**Dados enviados:**
```json
{ "username": "admin", "password": "senha123" }
```
**Resposta (200):**
```json
{ "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" }
```
**Erros:** `400` — usuário/senha inválidos.

Use o token nas próximas requisições: `Authorization: Token 9944b09...`

---

## Clientes

Modelo: `tipo_pessoa` (PF/PJ), `nome`, `cpf_cnpj`, `telefone`, `email`,
`endereco`, `cidade`, `estado`, `cep`, `ativo`, `data_cadastro`, `data_atualizacao`.

| Método | URL | Finalidade |
|---|---|---|
| GET | `/api/clientes/` | Listar clientes |
| POST | `/api/clientes/` | Cadastrar cliente |
| GET | `/api/clientes/{id}/` | Consultar um cliente |
| PUT | `/api/clientes/{id}/` | Editar (todos os campos) |
| PATCH | `/api/clientes/{id}/` | Editar (parcial) |
| DELETE | `/api/clientes/{id}/` | Inativar cliente (não apaga do banco) |

**Parâmetros de busca/filtro (GET, query string):**
`?search=` (nome, cpf_cnpj, email) · `?ativo=true|false` ·
`?tipo_pessoa=PF|PJ` · `?cidade=` · `?estado=` · `?ordering=nome`

**Exemplo de request (POST):**
```json
{
  "tipo_pessoa": "PJ",
  "nome": "Comércio ABC LTDA",
  "cpf_cnpj": "11222333000144",
  "telefone": "11966665555",
  "email": "contato@abc.com",
  "endereco": "Av. Principal, 500",
  "cidade": "São Paulo",
  "estado": "SP",
  "cep": "04567000"
}
```
**Erros possíveis:** `400` — CPF/CNPJ com tamanho incompatível com o
`tipo_pessoa`, CPF/CNPJ duplicado, campos obrigatórios ausentes,
telefone/CEP em formato inválido.

---

## Motoristas

Modelo: `nome`, `cpf`, `telefone`, `email`, `cnh_numero`,
`cnh_categoria`, `cnh_validade`, `cnh_vencida` (calculado), `data_admissao`, `ativo`.

| Método | URL | Finalidade |
|---|---|---|
| GET | `/api/motoristas/` | Listar motoristas |
| POST | `/api/motoristas/` | Cadastrar motorista |
| GET | `/api/motoristas/{id}/` | Consultar um motorista |
| PUT / PATCH | `/api/motoristas/{id}/` | Editar |
| DELETE | `/api/motoristas/{id}/` | Inativar motorista |
| GET | `/api/motoristas/{id}/entregas/` | Histórico de entregas |
| GET | `/api/motoristas/{id}/desempenho/` | Indicadores de desempenho |
| GET | `/api/motoristas/{id}/documentos/` | Documentos cadastrados |
| GET | `/api/motoristas/{id}/ferias/` | Períodos de férias |

**Filtros:** `?search=` (nome, cpf, cnh_numero) · `?ativo=` ·
`?cnh_categoria=` · `?ordering=nome`

### `GET /api/motoristas/{id}/entregas/`
**Parâmetros:** `?status=` · `?data_inicio=AAAA-MM-DD` · `?data_fim=AAAA-MM-DD`
**Resposta:** lista paginada de entregas (mesmo formato do endpoint `/api/entregas/`).

### `GET /api/motoristas/{id}/desempenho/`
**Resposta (200):**
```json
{
  "motorista_id": 3,
  "motorista_nome": "Carlos Pereira",
  "total_entregas": 40,
  "entregas_concluidas": 35,
  "entregas_atrasadas": 3,
  "entregas_canceladas": 2,
  "entregas_em_andamento": 0,
  "produtividade_percentual": 87.5
}
```
Indicadores simples calculados em cima das entregas já registradas —
sem inteligência artificial, previsões ou algoritmos avançados.

**Erros possíveis (cadastro):** `400` — CPF/CNH duplicados, formato
de telefone/CPF inválido, categoria de CNH inválida.

---

## Veículos

Modelo: `placa`, `modelo`, `marca`, `ano`, `capacidade_carga_kg`,
`situacao` (DISPONIVEL / EM_USO / MANUTENCAO / INATIVO), `disponivel` (calculado).

| Método | URL | Finalidade |
|---|---|---|
| GET | `/api/veiculos/` | Listar veículos |
| POST | `/api/veiculos/` | Cadastrar veículo |
| GET | `/api/veiculos/{id}/` | Consultar situação de um veículo |
| PUT / PATCH | `/api/veiculos/{id}/` | Editar |
| DELETE | `/api/veiculos/{id}/` | Marcar como inativo |

**Filtros:** `?search=` (placa, modelo, marca) · `?situacao=` · `?ordering=placa`

A situação do veículo também é alterada automaticamente pelo módulo
de **entregas** (fica `EM_USO` quando uma entrega é iniciada e volta
a `DISPONIVEL` quando é finalizada ou cancelada).

**Erros possíveis:** `400` — placa em formato inválido (aceita
`ABC1234` ou o padrão Mercosul `ABC1D23`) ou duplicada.

---

## Pedidos

Modelo: `cliente`, `origem`, `destino`, `tipo_carga`,
`data_pedido` (automático), `data_entrega_prevista`, `valor_frete`
(opcional), `observacoes`, `status` (calculado a partir da entrega mais recente).

| Método | URL | Finalidade |
|---|---|---|
| GET | `/api/pedidos/` | Listar pedidos |
| POST | `/api/pedidos/` | Abrir um novo pedido |
| GET | `/api/pedidos/{id}/` | Consultar um pedido |
| PUT / PATCH | `/api/pedidos/{id}/` | Editar |
| DELETE | `/api/pedidos/{id}/` | Excluir (bloqueado se já houver entrega/carga vinculada) |

**Filtros:** `?cliente=<id>` · `?tipo_carga=` · `?search=` (origem, destino) · `?ordering=data_entrega_prevista`

**Exemplo de request (POST):**
```json
{
  "cliente": 1,
  "origem": "São Paulo - SP",
  "destino": "Rio de Janeiro - RJ",
  "tipo_carga": "GERAL",
  "data_entrega_prevista": "2026-09-02",
  "valor_frete": "850.00",
  "observacoes": "Entregar em horário comercial"
}
```
`tipo_carga` aceita: `GERAL`, `FRAGIL`, `PERECIVEL`, `PERIGOSA`, `REFRIGERADA`.
`status` (somente leitura) retorna: `ABERTO`, `EM_ANDAMENTO`, `CONCLUIDO` ou `CANCELADO`.

**Erros possíveis:** `400` — cliente inativo, cliente/data ausentes.

---

## Cargas

Modelo: `pedido` (1 carga por pedido), `tipo_mercadoria`, `peso_kg`, `volume_m3`, `descricao`.

| Método | URL | Finalidade |
|---|---|---|
| GET | `/api/cargas/` | Listar cargas |
| POST | `/api/cargas/` | Registrar a carga de um pedido |
| GET | `/api/cargas/{id}/` | Consultar |
| PUT / PATCH | `/api/cargas/{id}/` | Editar |
| DELETE | `/api/cargas/{id}/` | Excluir |

**Filtros:** `?pedido=<id>` · `?search=tipo_mercadoria`

**Exemplo de request (POST):**
```json
{ "pedido": 10, "tipo_mercadoria": "Eletrônicos", "peso_kg": "350.50", "volume_m3": "2.400" }
```
**Erros possíveis:** `400` — pedido já possui carga cadastrada, peso/volume menor ou igual a zero.

---

## Entregas

O módulo mais importante do sistema — a **execução** de um pedido.

Modelo: `pedido`, `motorista` (opcional até iniciar), `veiculo`
(opcional até iniciar), `status`, `data_prevista`, `hora_saida`,
`hora_chegada`, `motivo_cancelamento`. Campos somente leitura,
derivados do pedido: `cliente_nome`, `origem`, `destino`,
`tipo_carga`, `tipo_mercadoria`, `motorista_nome`, `veiculo_placa`.

| Método | URL | Finalidade |
|---|---|---|
| GET | `/api/entregas/` | Listar entregas |
| POST | `/api/entregas/` | Criar uma entrega para um pedido (status inicial: `AGUARDANDO`) |
| GET | `/api/entregas/{id}/` | Consultar uma entrega |
| PUT / PATCH | `/api/entregas/{id}/` | Editar (apenas `motorista`/`veiculo`/`data_prevista`, e só enquanto `AGUARDANDO`) |
| DELETE | `/api/entregas/{id}/` | **Não permitido** (405) — use a ação de cancelamento |
| POST | `/api/entregas/{id}/iniciar/` | Iniciar a entrega |
| POST | `/api/entregas/{id}/finalizar/` | Finalizar a entrega |
| POST | `/api/entregas/{id}/cancelar/` | Cancelar a entrega |
| GET | `/api/entregas/{id}/ocorrencias/` | Ocorrências desta entrega |

**Filtros:** `?status=` · `?motorista=<id>` · `?veiculo=<id>` ·
`?pedido=<id>` · `?data_inicio=` · `?data_fim=` (intervalo de `data_prevista`) · `?ordering=data_prevista`

`status` possíveis: `AGUARDANDO`, `EM_ROTA`, `ENTREGUE`, `ATRASADA`, `CANCELADA`.
Uma entrega é marcada `ATRASADA` automaticamente quando sua
`data_prevista` já passou e ela ainda não foi concluída.

### `POST /api/entregas/`
```json
{ "pedido": 10 }
```
`data_prevista` é opcional — se não for enviada, usa a
`data_entrega_prevista` do próprio pedido. `motorista`/`veiculo`
também são opcionais neste momento.
**Erros possíveis:** `400` — pedido já possui entrega ativa,
motorista inativo, veículo indisponível.

### `POST /api/entregas/{id}/iniciar/`
Sem corpo de requisição.
**Resposta (200):**
```json
{
  "message": "Entrega iniciada com sucesso.",
  "data": { "id": 5, "status": "EM_ROTA", "hora_saida": "2026-08-26T13:45:00Z", "...": "..." }
}
```
**Erros possíveis (400):**
```json
{ "detail": "Não é possível iniciar esta entrega." }
```
```json
{ "detail": "É necessário informar motorista e veículo antes de iniciar a entrega." }
```
```json
{ "detail": "O motorista selecionado está inativo." }
```
```json
{ "detail": "O veículo selecionado está indisponível." }
```

### `POST /api/entregas/{id}/finalizar/`
Sem corpo de requisição. Registra `hora_chegada` e muda o status para `ENTREGUE`.
**Resposta (200):** mesmo formato do `iniciar/`, com `"message": "Entrega finalizada com sucesso."`
**Erros possíveis (400):** `{ "detail": "Não é possível finalizar esta entrega." }`
(a entrega precisa estar `EM_ROTA` ou `ATRASADA`)

### `POST /api/entregas/{id}/cancelar/`
```json
{ "motivo": "Cliente desistiu do pedido" }
```
**Resposta (200):** mesmo formato acima, com `"message": "Entrega cancelada com sucesso."`
**Erros possíveis (400):**
```json
{ "detail": "É necessário informar o motivo do cancelamento." }
```
```json
{ "detail": "Não é possível cancelar esta entrega." }
```
(entrega já `ENTREGUE` ou já `CANCELADA`)

---

## Ocorrências

Modelo: `entrega`, `tipo`, `descricao`, `data`, `observacao`.
`tipo` aceita: `ATRASO`, `PROBLEMA_VEICULO`, `PROBLEMA_ENTREGA`, `ENDERECO_INCORRETO`, `OUTROS`.

| Método | URL | Finalidade |
|---|---|---|
| GET | `/api/ocorrencias/` | Listar ocorrências |
| POST | `/api/ocorrencias/` | Registrar uma ocorrência |
| GET | `/api/ocorrencias/{id}/` | Consultar |
| PUT / PATCH | `/api/ocorrencias/{id}/` | Editar |
| DELETE | `/api/ocorrencias/{id}/` | Excluir |

**Filtros:** `?entrega=<id>` · `?tipo=` · `?search=` (descrição, observação)

---

## Multas

Modelo: `motorista`, `veiculo` (opcional), `motivo`, `data`, `valor`, `observacao`.

| Método | URL | Finalidade |
|---|---|---|
| GET | `/api/multas/` | Listar multas |
| POST | `/api/multas/` | Cadastrar multa |
| GET | `/api/multas/{id}/` | Consultar |
| PUT / PATCH | `/api/multas/{id}/` | Editar |
| DELETE | `/api/multas/{id}/` | Excluir |

**Filtros:** `?motorista=<id>` · `?veiculo=<id>` · `?search=motivo` · `?ordering=data`

---

## Documentos

Modelo: `motorista`, `tipo_documento`, `numero`, `data_emissao`,
`data_validade`, `situacao` (calculado: `VALIDO` / `A_VENCER` — até
30 dias do vencimento / `VENCIDO`), `observacao`.
`tipo_documento` aceita: `CNH`, `ASO`, `CERTIDAO_ANTECEDENTES`, `OUTROS`.

| Método | URL | Finalidade |
|---|---|---|
| GET | `/api/documentos/` | Listar documentos |
| POST | `/api/documentos/` | Cadastrar documento |
| GET | `/api/documentos/{id}/` | Consultar |
| PUT / PATCH | `/api/documentos/{id}/` | Editar |
| DELETE | `/api/documentos/{id}/` | Excluir |

**Filtros:** `?motorista=<id>` · `?tipo_documento=` · `?ordering=data_validade`
**Erros possíveis:** `400` — data de validade anterior à data de emissão.

---

## Férias

Modelo: `motorista`, `data_inicio`, `data_fim`, `situacao` (calculado:
`AGENDADA` / `EM_ANDAMENTO` / `CONCLUIDA`), `observacao`.

| Método | URL | Finalidade |
|---|---|---|
| GET | `/api/ferias/` | Listar períodos de férias |
| POST | `/api/ferias/` | Registrar férias |
| GET | `/api/ferias/{id}/` | Consultar |
| PUT / PATCH | `/api/ferias/{id}/` | Editar |
| DELETE | `/api/ferias/{id}/` | Excluir |

**Filtros:** `?motorista=<id>` · `?ordering=data_inicio`
**Erros possíveis:** `400` — data de término anterior à de início,
ou período sobreposto a férias já registradas para o mesmo motorista.

---

## Relatórios

Todos aceitam `?periodo=dia|semana|mes` (padrão: `dia`, ou seja,
hoje) **ou** `?data_inicio=AAAA-MM-DD&data_fim=AAAA-MM-DD` explícitos
(têm prioridade sobre `periodo` quando os dois vierem preenchidos).

### `GET /api/relatorios/entregas/`
**Resposta (200):**
```json
{
  "periodo": { "data_inicio": "2026-08-26", "data_fim": "2026-08-26" },
  "total_entregas": 12,
  "entregas_por_status": {
    "AGUARDANDO": 3, "EM_ROTA": 4, "ENTREGUE": 4, "ATRASADA": 1, "CANCELADA": 0
  },
  "entregas": [ "... lista completa, mesmo formato de /api/entregas/ ..." ]
}
```

### `GET /api/relatorios/desempenho/`
**Resposta (200):**
```json
{
  "total_motoristas": 8,
  "motoristas": [
    { "motorista_id": 1, "motorista_nome": "...", "total_entregas": 40, "...": "..." }
  ]
}
```
Considera apenas motoristas ativos.

### `GET /api/relatorios/faturamento/`
**Resposta (200):**
```json
{
  "periodo": { "data_inicio": "2026-08-01", "data_fim": "2026-08-31" },
  "quantidade_entregas_faturadas": 27,
  "valor_total_faturado": "18450.00"
}
```
Soma o `valor_frete` dos pedidos cuja entrega foi concluída
(`ENTREGUE`) dentro do período, com base na `hora_chegada`.

---

## Formato de erros

Erros de regra de negócio (ex.: ações de entrega) seguem o formato:
```json
{ "detail": "Mensagem explicando o que deu errado." }
```

Erros de validação de campo (ex.: campo obrigatório ausente) seguem o
formato padrão do Django REST Framework, agrupado por campo:
```json
{ "cpf_cnpj": ["CPF deve conter 11 dígitos."] }
```

Códigos HTTP usados: `200` (sucesso), `201` (criado), `204` (excluído
com sucesso, sem corpo de resposta), `400` (erro de validação/regra de
negócio), `401` (não autenticado), `404` (não encontrado), `405`
(método não permitido — ex.: tentar excluir uma entrega).
