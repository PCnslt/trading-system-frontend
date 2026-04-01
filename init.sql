-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create memories table
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding vector(768), -- nomic-embed-text uses 768 dimensions
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding_model TEXT DEFAULT 'nomic-embed-text',
    CONSTRAINT embedding_not_null CHECK (embedding IS NOT NULL)
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS memories_embedding_idx ON memories USING ivfflat (embedding vector_cosine_ops);

-- Create api_usage table for cost tracking
CREATE TABLE IF NOT EXISTS api_usage (
    id SERIAL PRIMARY KEY,
    service TEXT NOT NULL,
    model TEXT NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cost NUMERIC(10, 6) DEFAULT 0,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    request_type TEXT NOT NULL,
    endpoint TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create cache table for embeddings
CREATE TABLE IF NOT EXISTS embedding_cache (
    id SERIAL PRIMARY KEY,
    text_hash TEXT UNIQUE NOT NULL,
    embedding vector(768) NOT NULL,
    model TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for cache lookups
CREATE INDEX IF NOT EXISTS embedding_cache_text_hash_idx ON embedding_cache (text_hash);

-- Create function to update last_accessed timestamp
CREATE OR REPLACE FUNCTION update_last_accessed()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_accessed = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for memories table
CREATE TRIGGER update_memories_last_accessed
    BEFORE UPDATE ON memories
    FOR EACH ROW
    EXECUTE FUNCTION update_last_accessed();

-- Create trigger for cache table
CREATE TRIGGER update_cache_last_accessed
    BEFORE UPDATE ON embedding_cache
    FOR EACH ROW
    EXECUTE FUNCTION update_last_accessed();

-- Create search function for hybrid search (vector + text)
CREATE OR REPLACE FUNCTION search_memories(
    query_embedding vector(768),
    query_text TEXT DEFAULT NULL,
    limit_k INTEGER DEFAULT 5,
    similarity_threshold FLOAT DEFAULT 0.7
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.id,
        m.content,
        m.metadata,
        1 - (m.embedding <=> query_embedding) as similarity,
        m.created_at
    FROM memories m
    WHERE 1 - (m.embedding <=> query_embedding) > similarity_threshold
    ORDER BY m.embedding <=> query_embedding
    LIMIT limit_k;
END;
$$ LANGUAGE plpgsql;