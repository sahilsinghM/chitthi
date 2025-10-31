-- Vector similarity search function for content embeddings
-- Run this in Supabase SQL Editor after creating the schema

CREATE OR REPLACE FUNCTION match_content_embeddings(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id uuid,
  content_id uuid,
  embedding vector(1536),
  similarity float,
  content_summary text,
  content_url text,
  content_tags text[]
)
LANGUAGE sql STABLE
AS $$
  SELECT
    ce.id,
    ce.content_id,
    ce.embedding,
    1 - (ce.embedding <=> query_embedding) AS similarity,
    ci.summary AS content_summary,
    ci.url AS content_url,
    ci.tags AS content_tags
  FROM content_embeddings ce
  JOIN content_items ci ON ce.content_id = ci.id
  WHERE 1 - (ce.embedding <=> query_embedding) > match_threshold
  ORDER BY ce.embedding <=> query_embedding
  LIMIT match_count;
$$;



