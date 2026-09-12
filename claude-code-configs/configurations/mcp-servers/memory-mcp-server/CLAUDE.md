# Memory MCP Server Development Assistant

You are an expert in building production MCP (Model Context Protocol) servers with memory persistence, vector search capabilities, and AI companion systems. You have deep expertise in PostgreSQL, pgvector, Drizzle ORM, and the MCP SDK.

## Memory Integration

This CLAUDE.md follows official Claude Code patterns for MCP server development:

- **MCP protocol compliance** - Follows @modelcontextprotocol/sdk standards
- **Project memory** - Instructions shared with development team
- **Tool integration** - Works with Claude Code's MCP commands
- **Automated discovery** - Available when MCP server is configured

## MCP Configuration

To use this server with Claude Code:

```bash
# Add local MCP server
claude mcp add memory-server -- npx memory-mcp-server

# Add with environment variables  
claude mcp add memory-server --env DATABASE_URL=your_db_url --env OPENAI_API_KEY=your_key -- npx memory-mcp-server

# Check server status
claude mcp list
```

## Available MCP Tools

When connected, provides these tools to Claude Code:

- `memory.create` - Store new memory with vector embedding
- `memory.search` - Semantic search through stored memories  
- `memory.update` - Update existing memory content
- `memory.delete` - Remove memories by ID
- `memory.list` - List memories for user/companion
- `memory.consolidate` - Merge similar memories

## Project Context

This is a Memory MCP Server project focused on:

- **Persistent memory storage** with PostgreSQL and pgvector
- **Semantic search** using OpenAI embeddings
- **Multi-tenant architecture** for AI companions
- **Production deployment** with monitoring and scaling
- **MCP protocol compliance** using @modelcontextprotocol/sdk

## Technology Stack

### Core Technologies

- **TypeScript** - Type-safe development
- **Node.js** - Runtime environment
- **@modelcontextprotocol/sdk** - MCP implementation
- **PostgreSQL 17** - Primary database
- **Neon** - Serverless PostgreSQL hosting

### Database & ORM

- **Drizzle ORM v0.44.4** - Type-safe database access
- **pgvector v0.8.0** - Vector similarity search
- **@neondatabase/serverless** - Serverless PostgreSQL client

### Vector Search

- **OpenAI Embeddings** - text-embedding-3-small model
- **HNSW Indexes** - High-performance similarity search
- **Hybrid Search** - Combining vector and keyword search

## Architecture Patterns

### Memory System Design

```typescript
// Memory schema with vector embeddings
export const memories = pgTable('memories', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: text('user_id').notNull(),
  companionId: text('companion_id').notNull(),
  content: text('content').notNull(),
  embedding: vector('embedding', { dimensions: 1536 }),
  metadata: jsonb('metadata'),
  importance: real('importance').default(0.5),
  lastAccessed: timestamp('last_accessed'),
  createdAt: timestamp('created_at').defaultNow(),
}, (t) => ({
  embeddingIdx: index().using('hnsw', t.embedding.op('vector_cosine_ops')),
  userCompanionIdx: index().on(t.userId, t.companionId),
}));
```

### MCP Server Implementation

```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server({
  name: 'memory-server',
  version: '1.0.0',
}, {
  capabilities: {
    resources: {},
    tools: {},
  },
});

// Tool handlers
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // Implementation
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

## Critical Implementation Details

### 1. Vector Search Optimization

```typescript
// Efficient similarity search with pgvector
const similar = await db
  .select()
  .from(memories)
  .where(
    and(
      eq(memories.userId, userId),
      sql`${memories.embedding} <=> ${embedding} < 0.5`
    )
  )
  .orderBy(sql`${memories.embedding} <=> ${embedding}`)
  .limit(10);
```

### 2. Memory Lifecycle Management

- **Consolidation**: Merge similar memories periodically
- **Decay**: Reduce importance over time without access
- **Archival**: Move old memories to cold storage
- **Deduplication**: Prevent duplicate memory storage

### 3. Multi-tenant Isolation

```typescript
// Row-level security for tenant isolation
ALTER TABLE memories ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON memories
  FOR ALL
  USING (user_id = current_setting('app.user_id')::text);
```

### 4. Error Handling

```typescript
// Comprehensive error handling
try {
  const result = await operation();
  return { content: [{ type: 'text', text: JSON.stringify(result) }] };
} catch (error) {
  if (error instanceof ZodError) {
    return { error: { code: 'INVALID_PARAMS', message: error.message } };
  }
  logger.error('Operation failed', { error, context });
  return { error: { code: 'INTERNAL_ERROR', message: 'Operation failed' } };
}
```

## Performance Optimization

### Database Indexing

```sql
-- HNSW index for vector search
CREATE INDEX memories_embedding_idx ON memories 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- B-tree indexes for filtering
CREATE INDEX memories_user_companion_idx ON memories(user_id, companion_id);
CREATE INDEX memories_created_at_idx ON memories(created_at DESC);
```

### Connection Pooling

```typescript
// Neon serverless with connection pooling
import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL, {
  poolQueryViaFetch: true,
  fetchConnectionCache: true,
});
```

### Caching Strategy

- **Embedding Cache**: Cache frequently used embeddings
- **Query Cache**: Cache common search results
- **Connection Cache**: Reuse database connections

## Security Best Practices

### Input Validation

```typescript
// Zod schemas for all inputs
const CreateMemorySchema = z.object({
  content: z.string().min(1).max(10000),
  metadata: z.record(z.unknown()).optional(),
  importance: z.number().min(0).max(1).optional(),
});

// Validate before processing
const validated = CreateMemorySchema.parse(input);
```

### Authentication & Authorization

```typescript
// JWT-based authentication
const token = request.headers.authorization?.split(' ')[1];
const payload = jwt.verify(token, process.env.JWT_SECRET);

// Role-based access control
if (!payload.roles.includes('memory:write')) {
  throw new ForbiddenError('Insufficient permissions');
}
```

### Data Encryption

- Encrypt sensitive memory content at rest
- Use TLS for all connections
- Implement field-level encryption for PII

## Testing Strategy

### Unit Tests

```typescript
// Test memory operations
describe('MemoryService', () => {
  it('should create memory with embedding', async () => {
    const memory = await service.create({
      content: 'Test memory',
      userId: 'test-user',
    });
    expect(memory.embedding).toBeDefined();
    expect(memory.embedding.length).toBe(1536);
  });
});
```

### Integration Tests

```typescript
// Test MCP server
describe('MCP Server', () => {
  it('should handle memory.create tool', async () => {
    const response = await server.handleRequest({
      method: 'tools/call',
      params: {
        name: 'memory.create',
        arguments: { content: 'Test' },
      },
    });
    expect(response.content[0].type).toBe('text');
  });
});
```

## Deployment Configuration

### Docker Setup

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
RUN npm run build
CMD ["node", "dist/index.js"]
```

### Environment Variables

```env
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
OPENAI_API_KEY=sk-...
MCP_SERVER_PORT=3000
NODE_ENV=production
LOG_LEVEL=info
```

## Monitoring & Observability

### Structured Logging

```typescript
import pino from 'pino';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ level: label }),
  },
});
```

### Metrics Collection

```typescript
// Prometheus metrics
import { register, Counter, Histogram } from 'prom-client';

const memoryCreated = new Counter({
  name: 'memory_created_total',
  help: 'Total number of memories created',
});

const searchDuration = new Histogram({
  name: 'memory_search_duration_seconds',
  help: 'Duration of memory search operations',
});
```

## Common Commands

```bash
# Development
npm run dev           # Start development server
npm run build         # Build for production
npm run test          # Run tests
npm run lint          # Lint code

# Database
npm run db:migrate    # Run migrations
npm run db:push       # Push schema changes
npm run db:studio     # Open Drizzle Studio

# MCP Testing
npm run mcp:test      # Test MCP server
npm run mcp:debug     # Debug MCP protocol
```

## Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Drizzle ORM Documentation](https://orm.drizzle.team)
- [Neon Documentation](https://neon.tech/docs)

Remember: **Performance, Security, and Reliability** are critical for production MCP servers!
