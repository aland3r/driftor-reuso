-- Banco do Driftor (Reuso): 6 tabelas no schema driftor_reuso. O app roda este arquivo ao subir.

create table if not exists processos (
    id            uuid primary key,
    nome          text not null,
    arquivo       text,
    total_traces  integer not null default 0,
    total_eventos integer not null default 0
);

create table if not exists atividades (
    id        uuid primary key,
    nome text not null unique
);

create table if not exists eventos (
    id           bigserial primary key,
    processo_id  uuid not null references processos(id) on delete cascade,
    atividade_id uuid not null references atividades(id) on delete cascade,
    case_id      text not null,
    ordem        integer not null,
    inicio       timestamptz not null,
    duracao      double precision not null
);

create table if not exists analises (
    id                uuid primary key,
    processo_id       uuid not null references processos(id) on delete cascade,
    nome              text not null,
    atividade         text,
    delta             double precision not null,
    total_observacoes integer not null,
    serie             text not null
);

create table if not exists drifts (
    id           uuid primary key,
    analise_id   uuid not null references analises(id) on delete cascade,
    posicao      integer not null,
    inicio       integer not null,
    media_antes  double precision not null,
    media_depois double precision not null
);

create table if not exists manutencoes (
    id          uuid primary key,
    analise_id  uuid not null references analises(id) on delete cascade,
    drift_id    uuid not null references drifts(id) on delete cascade,
    descricao   text not null,
    status      text not null default 'pendente',
    observacoes text not null default ''
);
