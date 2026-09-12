# Memory MCP Server Claude Code Configuration 🧠

A production-grade Claude Code configuration specialized for building MCP servers with memory persistence, vector search, and AI companion systems.

## ✨ Features

This configuration provides comprehensive support for:

- **Memory Systems** - Vector-indexed persistence with pgvector
- **MCP Protocol** - Complete server implementation toolkit
- **Database Architecture** - PostgreSQL 17 with Neon serverless
- **AI Companions** - Multi-tenant architecture patterns
- **Production Deployment** - Docker, Kubernetes, monitoring

## 📦 Installation

1. Copy the `.claude` directory to your MCP server project:

```bash
cp -r memory-mcp-server/.claude your-mcp-project/
cp memory-mcp-server/CLAUDE.md your-mcp-project/
```

2. The configuration will be automatically loaded when you start Claude Code.

## 🤖 Specialized Agents (15 total)

### MCP Protocol Experts

| Agent | Description | Use Cases |
|-------|-------------|-----------|
| `mcp-protocol-expert` | Protocol debugging and compliance | Connection issues, protocol validation |
| `mcp-sdk-builder` | SDK implementation patterns | Building new MCP servers |
| `mcp-transport-expert` | Transport layers (stdio, HTTP, SSE) | Session management, optimization |
| `mcp-types-expert` | TypeScript and Zod schemas | Type safety, JSON-RPC formats |

### Database & Vector Search

| Agent | Description | Use Cases |
|-------|-------------|-----------|
| `neon-drizzle-expert` | Neon PostgreSQL with Drizzle ORM | Database setup, migrations |
| `pgvector-advanced` | Advanced pgvector v0.8.0 features | Binary vectors, HNSW indexes |
| `vector-search-expert` | Semantic search and embeddings | OpenAI embeddings, similarity search |

### Memory & Architecture

| Agent | Description | Use Cases |
|-------|-------------|-----------|
| `memory-architecture` | Database design and indexing | Schema design, retrieval optimization |
| `memory-lifecycle` | Consolidation and expiration | Memory decay models, deduplication |
| `memory-validator` | Data integrity and validation | CRUD operations, testing |
| `companion-architecture` | Multi-tenant AI systems | Isolation strategies, scaling |

### Development & Operations

| Agent | Description | Use Cases |
|-------|-------------|-----------|
| `code-reviewer` | Comprehensive code review | Security focus, best practices |
| `debugger` | Systematic debugging | Root cause analysis |
| `test-runner` | Automated testing | MCP protocol validation |
| `production-deployment` | HTTPS deployment | Containerization, monitoring |

## 🛠️ Commands (7 total)

### Development Workflow

```bash
/setup quick       # Quick project setup with essentials
/setup full        # Complete environment with all dependencies
/setup database    # Database-focused initialization
```

### Testing & Review

```bash
/test             # Generate comprehensive test suites
/review           # Security-focused code review
/explain          # Context-aware code explanation
```

### MCP Operations

```bash
/mcp-debug        # Debug MCP protocol issues
/memory-ops       # Test memory CRUD operations
/perf-monitor     # Performance profiling
```

## 🪝 Automation Hooks

### TypeScript Development Hook

Automatically triggered on file modifications:

- ✅ Type checking with `tsc --noEmit`
- ✨ Prettier formatting
- 🔧 ESLint fixing
- 🧪 Test execution for test files
- 📁 Smart filtering (skips node_modules, build dirs)

### Command Logging

- 📝 Logs all executed Bash commands
- ⏱️ Timestamps for debugging
- 📊 Audit trail maintenance

## ⚙️ Configuration Details

### Security Permissions

```json
{
  "permissions": {
    "allow": [
      "Read", "Grep", "Glob", "LS",
      "Bash(npm test:*)",
      "Write(**/*.ts)",
      "Bash(npx drizzle-kit:*)",
      "Bash(psql:*)"
    ],
    "deny": [
      "Read(./.env)",
      "Bash(rm -rf:*)",
      "Bash(git push:*)"
    ]
  }
}
```

### Environment Variables

Pre-configured for MCP development:

- `DATABASE_URL` - PostgreSQL connection
- `OPENAI_API_KEY` - For embeddings
- `MCP_SERVER_PORT` - Server configuration
- `NEON_DATABASE_URL` - Serverless PostgreSQL

## 🚀 Usage Examples

### Building an MCP Memory Server

```bash
# 1. Set up the project
> /setup full

# 2. Design memory schema
> Use memory-architecture agent to design the database schema

# 3. Implement MCP server
> Use mcp-sdk-builder agent to create the server

# 4. Add vector search
> Use vector-search-expert to implement semantic search

# 5. Deploy to production
> Use production-deployment agent for containerization
```

### Debugging MCP Connections

```bash
# Debug protocol issues
> /mcp-debug

# The debugger will:
# - Validate protocol compliance
# - Check message formats
# - Test transport layer
# - Identify connection issues
```

## 📊 Technology Stack

Optimized for:

- **TypeScript** & Node.js
- **PostgreSQL 17** with Neon serverless
- **Drizzle ORM v0.44.4** for type-safe database
- **pgvector v0.8.0** for vector similarity
- **@modelcontextprotocol/sdk** for MCP
- **OpenAI embeddings** for semantic search
- **Docker & Kubernetes** for deployment

## 🎯 Key Features

### Memory Persistence

- Vector-indexed storage with pgvector
- Semantic search capabilities
- Memory consolidation and lifecycle
- Multi-tenant isolation

### MCP Protocol Support

- Complete SDK implementation patterns
- Transport layer optimization
- Protocol compliance validation
- Session management

### Production Ready

- Docker containerization
- Kubernetes orchestration
- Prometheus/Grafana monitoring
- Structured logging

## 🔧 Customization

Edit `.claude/settings.json` to customize:

- Permissions for your security needs
- Environment variables for your services
- Hook configurations for your workflow
- Agent selections for your domain

## 📝 Best Practices

This configuration enforces:

1. **Type Safety** - Full TypeScript with Zod validation
2. **Security First** - Input validation, authentication
3. **Performance** - Optimized vector search, caching
4. **Testing** - Comprehensive test coverage
5. **Monitoring** - Structured logging, metrics
6. **Documentation** - Clear code comments, API docs

## 🐛 Troubleshooting

### Common Issues

**Hooks not executing:**

```bash
chmod +x .claude/hooks/*.sh
```

**Database connection issues:**

```bash
# Check environment variables
echo $DATABASE_URL
# Test connection
psql $DATABASE_URL
```

**MCP protocol errors:**

```bash
/mcp-debug
```

## 📚 Resources

- [MCP SDK Documentation](https://modelcontextprotocol.io)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Neon Documentation](https://neon.tech/docs)
- [Drizzle ORM Documentation](https://orm.drizzle.team)

---

**Built for production MCP server development** 🚀

*Transform your MCP server development with specialized AI assistance and automation.*
