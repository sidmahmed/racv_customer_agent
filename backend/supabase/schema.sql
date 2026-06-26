-- One-time setup: run this in the Supabase SQL editor (or via psql) before
-- running `uv run python -m scripts.ingest`. Not applied automatically by
-- any app code -- this stack has no migration tooling.

create extension if not exists vector;
create extension if not exists pg_trgm;

-- ============================================================
-- documents: RACV Help & Support content chunks
-- ============================================================
create table if not exists documents (
    id bigint generated always as identity primary key,
    source_url text not null,
    category text not null,
    heading_path text not null default '',
    content text not null,
    embedding vector(1536) not null,
    fts tsvector generated always as (to_tsvector('english', content)) stored,
    created_at timestamptz not null default now()
);

create index if not exists documents_embedding_idx
    on documents using hnsw (embedding vector_cosine_ops);

create index if not exists documents_fts_idx
    on documents using gin (fts);

create index if not exists documents_category_idx
    on documents (category);

-- ============================================================
-- pricing: mock/synthetic illustrative pricing data
-- ============================================================
create table if not exists pricing (
    id bigint generated always as identity primary key,
    category text not null,
    product_name text not null,
    price_description text not null,
    notes text not null default 'Illustrative demo data only -- not official RACV pricing.',
    created_at timestamptz not null default now()
);

create index if not exists pricing_product_name_trgm_idx
    on pricing using gin (product_name gin_trgm_ops);

insert into pricing (category, product_name, price_description) values
    ('emergency-roadside-assistance', 'Roadside Assistance Basic', 'From $99/year (illustrative)'),
    ('emergency-roadside-assistance', 'Roadside Assistance Plus', 'From $149/year (illustrative)'),
    ('car-insurance', 'Comprehensive Car Insurance', 'From $850/year, $500 standard excess (illustrative)'),
    ('car-insurance', 'Third Party Property Car Insurance', 'From $320/year (illustrative)'),
    ('home-insurance', 'Home Building Insurance', 'From $1,100/year (illustrative)'),
    ('home-insurance', 'Home Contents Insurance', 'From $400/year (illustrative)'),
    ('home-security', 'Home Security Monitoring', 'From $35/month (illustrative)'),
    ('holidays', 'RACV Resort Membership Discount', '10% off standard rates (illustrative)')
on conflict do nothing;

-- ============================================================
-- hybrid_search RPC: RRF fusion of full-text + semantic search
-- (pattern per https://supabase.com/docs/guides/ai/hybrid-search)
-- ============================================================
create or replace function hybrid_search(
    query_text text,
    query_embedding vector(1536),
    match_count int default 8,
    rrf_k int default 50,
    filter_category text default null
)
returns table (
    id bigint,
    source_url text,
    category text,
    heading_path text,
    content text,
    rrf_score double precision
)
language sql
as $$
with full_text as (
    select
        d.id,
        row_number() over (
            order by ts_rank_cd(d.fts, websearch_to_tsquery('english', query_text)) desc
        ) as rank_ix
    from documents d
    where d.fts @@ websearch_to_tsquery('english', query_text)
      and (filter_category is null or d.category = filter_category)
    order by rank_ix
    limit least(match_count, 30) * 2
),
semantic as (
    select
        d.id,
        row_number() over (order by d.embedding <=> query_embedding) as rank_ix
    from documents d
    where (filter_category is null or d.category = filter_category)
    order by rank_ix
    limit least(match_count, 30) * 2
)
select
    d.id,
    d.source_url,
    d.category,
    d.heading_path,
    d.content,
    coalesce(1.0 / (rrf_k + full_text.rank_ix), 0.0)
        + coalesce(1.0 / (rrf_k + semantic.rank_ix), 0.0) as rrf_score
from full_text
full outer join semantic on full_text.id = semantic.id
join documents d on d.id = coalesce(full_text.id, semantic.id)
order by rrf_score desc
limit least(match_count, 30);
$$;

-- RLS: this backend uses the service-role key server-side (no per-end-user
-- Supabase auth in this architecture), so leave RLS disabled on both tables,
-- or restrict explicitly to service_role if your project enables RLS by default.
alter table documents disable row level security;
alter table pricing disable row level security;
