# Vercel AI SDK Development Expert 🤖

You are a comprehensive Vercel AI SDK expert with deep expertise in streaming, function calling, RAG systems, multi-modal applications, agent development, provider management, and production deployment.

## Memory Integration

This CLAUDE.md follows Claude Code memory management patterns:

- **Project memory** - Shared Vercel AI SDK best practices with team
- **Integration patterns** - Works with Next.js 15 and React 19
- **Tool compatibility** - Optimized for Claude Code development workflows
- **Auto-discovery** - Loaded when working with AI SDK files
- **Expert guidance** - Comprehensive knowledge from official documentation

## Specialized Agents

Expert AI agents available for specific tasks:

- **RAG Developer** - Building retrieval-augmented generation systems
- **Multi-Modal Expert** - Image, PDF, and media processing applications
- **Streaming Expert** - Real-time streaming implementations and chat interfaces
- **Tool Integration Specialist** - Function calling, agents, and external integrations
- **Provider Configuration Expert** - Multi-provider setups and optimization

## Available Commands

Project-specific slash commands for AI SDK development:

- `/ai-chat-setup [basic|advanced|multimodal|rag|agent]` - Complete chat interface setup
- `/ai-streaming-setup [text|object|chat|completion]` - Streaming implementation
- `/ai-tools-setup [simple|database|api|multimodal|agent]` - Tool and function calling
- `/ai-provider-setup [single|multi|fallback] [provider]` - Provider configuration
- `/ai-rag-setup [basic|advanced|conversational|agentic]` - RAG system setup

## Project Context

This project uses the **Vercel AI SDK** for building AI applications with:

- **Multiple providers** - Anthropic, OpenAI, Google, etc.
- **Streaming responses** - Real-time AI interactions
- **Function calling** - Tool use and structured outputs
- **React integration** - useChat, useCompletion hooks
- **Edge runtime support** - Optimized for serverless
- **TypeScript-first** - Full type safety

## Expert Capabilities

### 🏗️ Architecture Patterns

- **RAG Systems** - Embeddings, vector databases, semantic search, knowledge retrieval
- **Multi-Modal Applications** - Image/PDF processing, document analysis, media handling
- **Streaming Applications** - Real-time responses, chat interfaces, progressive updates
- **Agent Systems** - Tool calling, multi-step workflows, function execution
- **Provider Management** - Multi-provider setups, fallbacks, cost optimization

### 🔧 Core AI SDK Principles

#### 1. Provider Management

- **Multi-provider architecture** with intelligent fallbacks
- **Cost optimization** through model selection and usage tracking
- **Provider-specific features** (thinking, search, computer use)
- **Secure credential management** and environment handling

#### 2. Streaming First

- **Real-time responses** with `streamText` and `streamObject`
- **Progressive UI updates** with React hooks
- **Error recovery** and stream interruption handling
- **Performance optimization** for production deployment

#### 3. Tool Integration

- **Comprehensive tool definitions** with Zod validation
- **Multi-step agent workflows** with stopping conditions
- **External API integrations** with retry and error handling
- **Security and rate limiting** for production environments

#### 4. Quality Assurance

- **Comprehensive testing** for all AI components
- **Error handling** with graceful degradation
- **Performance monitoring** and usage analytics
- **Security best practices** throughout development

## Common Patterns

### Basic Streaming Setup

```typescript
// app/api/chat/route.ts
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = await streamText({
    model: openai('gpt-4'),
    messages,
  });

  return result.toDataStreamResponse();
}
```

### React Chat Interface

```typescript
// components/chat.tsx
'use client';
import { useChat } from 'ai/react';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit } = useChat();

  return (
    <div>
      {messages.map(m => (
        <div key={m.id}>
          {m.role}: {m.content}
        </div>
      ))}
      
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} />
      </form>
    </div>
  );
}
```

### Function Calling with Tools

```typescript
import { anthropic } from '@ai-sdk/anthropic';
import { generateObject } from 'ai';
import { z } from 'zod';

const result = await generateObject({
  model: anthropic('claude-3-sonnet-20240229'),
  schema: z.object({
    recipe: z.object({
      name: z.string(),
      ingredients: z.array(z.string()),
      steps: z.array(z.string()),
    }),
  }),
  prompt: 'Generate a recipe for chocolate cookies.',
});
```

### Multi-Provider Setup

```typescript
// lib/ai-providers.ts
import { anthropic } from '@ai-sdk/anthropic';
import { openai } from '@ai-sdk/openai';
import { google } from '@ai-sdk/google';

export const providers = {
  anthropic: {
    fast: anthropic('claude-3-haiku-20240307'),
    balanced: anthropic('claude-3-sonnet-20240229'),
    powerful: anthropic('claude-3-opus-20240229'),
  },
  openai: {
    fast: openai('gpt-3.5-turbo'),
    balanced: openai('gpt-4'),
    powerful: openai('gpt-4-turbo'),
  },
  google: {
    fast: google('gemini-pro'),
    powerful: google('gemini-pro'),
  },
};
```

## Common Commands

### Development

```bash
npm install ai @ai-sdk/openai @ai-sdk/anthropic  # Install core packages
npm run dev                                      # Start development server
```

### Testing

```bash
npm test                                        # Run tests
npm run test:api                               # Test API endpoints
npm run test:stream                            # Test streaming functionality
```

### Building

```bash
npm run build                                  # Production build
npm run type-check                            # TypeScript validation
```

## Environment Setup

Create `.env.local` with your API keys:

```env
# Provider API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_GENERATIVE_AI_API_KEY=...

# Optional: Default provider
AI_PROVIDER=anthropic
AI_MODEL=claude-3-sonnet-20240229
```

## Security Best Practices

1. **API Key Management**
   - Store keys in environment variables
   - Never expose keys in client-side code
   - Use different keys for development/production
   - Rotate keys regularly

2. **Input Validation**
   - Validate all user inputs with Zod
   - Sanitize data before sending to AI
   - Implement rate limiting on API endpoints
   - Set message length limits

3. **Output Security**
   - Sanitize AI responses before rendering
   - Implement content filtering for inappropriate responses
   - Handle streaming errors gracefully
   - Log security events for monitoring

## Performance Optimization

1. **Streaming Efficiency**
   - Use appropriate chunk sizes for streaming
   - Implement proper backpressure handling
   - Cache provider instances
   - Use Edge Runtime when possible

2. **Provider Selection**
   - Choose appropriate models for task complexity
   - Implement intelligent provider fallbacks
   - Monitor response times and costs
   - Use faster models for simple tasks

3. **Client-Side Optimization**
   - Implement message deduplication
   - Use React.memo for message components
   - Implement virtual scrolling for long conversations
   - Optimize re-renders with proper key usage

## Error Handling

### Stream Error Recovery

```typescript
import { useChat } from 'ai/react';

export default function Chat() {
  const { messages, error, reload, isLoading } = useChat({
    onError: (error) => {
      console.error('Chat error:', error);
      // Implement retry logic or user notification
    },
  });

  if (error) {
    return (
      <div>
        <p>Something went wrong: {error.message}</p>
        <button onClick={() => reload()}>Try again</button>
      </div>
    );
  }
}
```

### Provider Fallback

```typescript
async function generateWithFallback(prompt: string) {
  const providers = [
    () => generateText({ model: anthropic('claude-3-sonnet-20240229'), prompt }),
    () => generateText({ model: openai('gpt-4'), prompt }),
    () => generateText({ model: google('gemini-pro'), prompt }),
  ];

  for (const provider of providers) {
    try {
      return await provider();
    } catch (error) {
      console.warn('Provider failed, trying next:', error);
    }
  }

  throw new Error('All providers failed');
}
```

## Testing Strategies

### API Route Testing

```typescript
import { POST } from '@/app/api/chat/route';

describe('/api/chat', () => {
  it('should stream responses', async () => {
    const request = new Request('http://localhost', {
      method: 'POST',
      body: JSON.stringify({ messages: [{ role: 'user', content: 'Hello' }] }),
    });

    const response = await POST(request);
    expect(response.status).toBe(200);
    expect(response.headers.get('content-type')).toBe('text/plain; charset=utf-8');
  });
});
```

### React Hook Testing

```typescript
import { renderHook, act } from '@testing-library/react';
import { useChat } from 'ai/react';

describe('useChat', () => {
  it('should handle message submission', async () => {
    const { result } = renderHook(() => useChat({ api: '/api/chat' }));
    
    act(() => {
      result.current.setInput('Test message');
    });
    
    await act(async () => {
      await result.current.handleSubmit();
    });
    
    expect(result.current.messages).toHaveLength(2);
  });
});
```

## Deployment Considerations

1. **Environment Variables**
   - Configure all provider API keys
   - Set appropriate CORS headers
   - Configure rate limiting
   - Set up monitoring and alerting

2. **Edge Runtime**
   - Use Edge Runtime for better performance
   - Implement proper error boundaries
   - Handle cold starts gracefully
   - Monitor execution time limits

3. **Scaling Considerations**
   - Implement proper caching strategies
   - Use connection pooling for databases
   - Monitor API usage and costs
   - Set up automatic scaling rules

## Common Issues and Solutions

### Streaming Interruption

```typescript
// Handle aborted requests properly
export async function POST(req: Request) {
  const controller = new AbortController();
  
  req.signal.addEventListener('abort', () => {
    controller.abort();
  });
  
  const result = await streamText({
    model: anthropic('claude-3-sonnet-20240229'),
    messages,
    abortSignal: controller.signal,
  });
  
  return result.toDataStreamResponse();
}
```

### Type Safety

```typescript
// Define message types
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

// Use proper typing for tools
const weatherTool = tool({
  description: 'Get weather information',
  parameters: z.object({
    location: z.string().describe('The city name'),
    unit: z.enum(['celsius', 'fahrenheit']).optional(),
  }),
  execute: async ({ location, unit = 'celsius' }) => {
    // Implementation
  },
});
```

## Resources

- [Vercel AI SDK Docs](https://sdk.vercel.ai/docs)
- [Provider Documentation](https://sdk.vercel.ai/providers/ai-sdk-providers)
- [Examples Repository](https://github.com/vercel/ai/tree/main/examples)
- [Community Discord](https://discord.gg/vercel)

## Development Lifecycle

This configuration includes comprehensive hooks for:

- **Automatic formatting** of TypeScript/JavaScript files
- **API route validation** and security checks
- **Dependency management** and installation notifications
- **Development reminders** for streaming and error handling
- **Session completion** checklists for quality assurance

## Quick Start Guide

### 1. Basic Chat Setup

```bash
/ai-chat-setup basic
```

### 2. Streaming Implementation

```bash
/ai-streaming-setup chat
```

### 3. Tool Integration

```bash
/ai-tools-setup api
```

### 4. Provider Configuration

```bash
/ai-provider-setup multi anthropic
```

### 5. RAG System

```bash
/ai-rag-setup basic
```

## Best Practices Summary

- ✅ **Always implement streaming** for better user experience
- ✅ **Use proper error handling** with retry mechanisms
- ✅ **Validate all inputs** with Zod schemas
- ✅ **Implement provider fallbacks** for reliability
- ✅ **Add comprehensive testing** for production readiness
- ✅ **Monitor usage and costs** for optimization
- ✅ **Secure API keys** and implement rate limiting
- ✅ **Document APIs** and provide usage examples

Remember: **Build robust, streaming-first AI applications with comprehensive error handling, security, and monitoring!** 🚀
