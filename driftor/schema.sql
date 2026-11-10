-- Banco do Driftor (Reuso): 7 tabelas no schema driftor_reuso.
-- O app aplica este arquivo ao subir (BancoDeDados.aplicar_schema); "if not exists" deixa rodar de novo sem erro.

-- CRUD de Processo (Alander)
create table if not exists processos (
    id            uuid primary key,
    nome          text not null,
    arquivo       text,
    formato       text,
    status        text not null default 'vazio',   -- vazio | mapeando | pronto
    total_traces  integer not null default 0,
    total_eventos integer not null default 0,
    criado_em     timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);

-- Cada linha do log de eventos carregado no processo
create table if not exists eventos (
    id          bigserial primary key,
    processo_id uuid not null references processos(id) on delete cascade,
    case_id     text not null,
    ordem       integer not null,                  -- posição do evento dentro do trace
    rotulo      text not null,                     -- nome da operação como veio no log
    inicio      timestamptz,
    duracao_s   double precision
);
create index if not exists eventos_processo on eventos(processo_id, case_id, ordem);

-- CRUD de Atividade (Alander): catálogo de atividades
create table if not exists atividades (
    id        uuid primary key,
    nome      text not null,
    descricao text not null default ''
);
create unique index if not exists atividades_nome_unico on atividades (lower(nome));

-- Liga cada operação do log a uma atividade do catálogo (mapeamento)
create table if not exists operacoes (
    processo_id  uuid not null references processos(id) on delete cascade,
    rotulo       text not null,
    ocorrencias  integer not null,
    casos        integer not null,
    atividade_id uuid references atividades(id) on delete restrict,
    primary key (processo_id, rotulo)
);

-- CRUD de Análise (Emanuelle)
create table if not exists analises (
    id                uuid primary key,
    processo_id       uuid not null references processos(id) on delete cascade,
    nome              text not null,
    atividade         text,                        -- série filtrada por uma atividade (ou o trace inteiro)
    delta             double precision not null,
    tratamento        text not null,               -- bruto | tratado
    total_observacoes integer not null,
    total_drifts      integer not null default 0,
    total_notas       integer not null default 0,
    serie             text not null,               -- valores analisados, em JSON, para o gráfico
    criado_em         timestamptz not null default now()
);

-- Desvios que o ADWIN encontrou em cada análise
create table if not exists drifts (
    id              uuid primary key,
    analise_id      uuid not null references analises(id) on delete cascade,
    posicao         integer not null,              -- 1º, 2º, 3º desvio
    indice          integer not null,              -- trace onde o ADWIN detectou
    inicio_anomalia integer not null,              -- trace onde a mudança começou
    media_antes     double precision not null,
    media_depois    double precision not null,
    variacao_pct    double precision not null
);

-- CRUD de Nota de drift (Emanuelle)
create table if not exists notas_drift (
    id            uuid primary key,
    drift_id      uuid not null references drifts(id) on delete cascade,
    texto         text not null,
    criado_em     timestamptz not null default now(),
    atualizado_em timestamptz not null default now()
);
