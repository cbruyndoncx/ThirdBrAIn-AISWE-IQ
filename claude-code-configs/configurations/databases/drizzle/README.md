# Drizzle ORM Claude Code Configuration 🗃️

A comprehensive Claude Code configuration for building type-safe, performant database applications with Drizzle ORM, schema management, migrations, and modern database patterns.

## ✨ Features

This configuration provides:

- **Type-safe database operations** with full TypeScript inference
- **Schema management patterns** for scalable database design
- **Migration strategies** with versioning and rollback support
- **Query optimization** with prepared statements and indexing
- **Multi-database support** for PostgreSQL, MySQL, and SQLite
- **Testing approaches** with in-memory databases
- **Performance patterns** for production applications
- **Repository and service patterns** for clean architecture

## 📦 Installation

1. Copy the `.claude` directory to your project root:

```bash
cp -r drizzle/.claude your-project/
cp drizzle/CLAUDE.md your-project/
```

2. Install Drizzle ORM in your project:

```bash
# For PostgreSQL
npm install drizzle-orm @neondatabase/serverless
npm install -D drizzle-kit

# For MySQL
npm install drizzle-orm mysql2
npm install -D drizzle-kit @types/mysql

# For SQLite
npm install drizzle-orm better-sqlite3
npm install -D drizzle-kit @types/better-sqlite3
```

3. The configuration will be automatically loaded when you start Claude Code in your project.

## 🎯 What You Get

### Database Expertise

- **Schema Design** - Proper table definitions, relationships, and constraints
- **Migration Management** - Automatic generation, versioning, and deployment
- **Query Optimization** - Efficient queries with proper indexing strategies
- **Type Safety** - Full TypeScript inference from schema to queries
- **Multi-Database Support** - PostgreSQL, MySQL, SQLite configurations
- **Performance Patterns** - Prepared statements, connection pooling, caching

### Key Development Areas

| Area | Coverage |
|------|----------|
| **Schema Design** | Table definitions, relationships, constraints, indexes |
| **Migrations** | Generation, versioning, rollback, seeding |
| **Queries** | CRUD operations, joins, aggregations, pagination |
| **Type Safety** | Full TypeScript inference, compile-time validation |
| **Performance** | Prepared statements, indexes, connection pooling |
| **Testing** | In-memory testing, query mocking, integration tests |
| **Patterns** | Repository pattern, service layer, transaction handling |
| **Deployment** | Environment configuration, production optimizations |

## 🚀 Quick Start Examples

### Schema Definition

```typescript
// schema/users.ts
import { pgTable, serial, text, timestamp, boolean } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name').notNull(),
  emailVerified: boolean('email_verified').default(false),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
});

export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
```

### Database Connection

```typescript
// lib/db.ts
import { drizzle } from 'drizzle-orm/neon-http';
import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL!);
export const db = drizzle(sql);
```

### Basic Queries

```typescript
// lib/queries/users.ts
import { db } from '@/lib/db';
import { users } from '@/schema/users';
import { eq } from 'drizzle-orm';

export async function createUser(userData: NewUser) {
  const [user] = await db.insert(users).values(userData).returning();
  return user;
}

export async function getUserById(id: number) {
  const user = await db.select().from(users).where(eq(users.id, id));
  return user[0];
}
```

### Relations and Joins

```typescript
// schema/posts.ts
import { pgTable, serial, text, integer } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  content: text('content').notNull(),
  authorId: integer('author_id').references(() => users.id),
});

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
}));
```

## 🔧 Configuration Setup

### Drizzle Config

```typescript
// drizzle.config.ts
import type { Config } from 'drizzle-kit';

export default {
  schema: './src/schema/*',
  out: './drizzle',
  driver: 'pg',
  dbCredentials: {
    connectionString: process.env.DATABASE_URL!,
  },
  verbose: true,
  strict: true,
} satisfies Config;
```

### Environment Variables

```env
# PostgreSQL (Neon, Railway, Supabase)
DATABASE_URL=postgresql://username:password@host:5432/database

# MySQL (PlanetScale, Railway)
DATABASE_URL=mysql://username:password@host:3306/database

# SQLite (Local development)
DATABASE_URL=file:./dev.db
```

## 🛠️ Migration Commands

```bash
# Generate migration from schema changes
npx drizzle-kit generate:pg

# Push schema changes to database
npx drizzle-kit push:pg

# Introspect existing database
npx drizzle-kit introspect:pg

# Open Drizzle Studio (database browser)
npx drizzle-kit studio
```

## 🏗️ Schema Patterns

### E-commerce Schema

```typescript
// Complete e-commerce database schema
export const products = pgTable('products', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  price: decimal('price', { precision: 10, scale: 2 }).notNull(),
  stock: integer('stock').default(0),
  categoryId: integer('category_id').references(() => categories.id),
});

export const orders = pgTable('orders', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').references(() => users.id),
  total: decimal('total', { precision: 10, scale: 2 }).notNull(),
  status: text('status', { 
    enum: ['pending', 'processing', 'shipped', 'delivered'] 
  }).default('pending'),
});
```

### Content Management

```typescript
// Blog/CMS schema with full-text search
export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  content: text('content').notNull(),
  slug: text('slug').notNull().unique(),
  published: boolean('published').default(false),
  tags: text('tags').array(),
  searchVector: vector('search_vector'), // For full-text search
}, (table) => ({
  slugIdx: uniqueIndex('posts_slug_idx').on(table.slug),
  searchIdx: index('posts_search_idx').using('gin', table.searchVector),
}));
```

## 🚀 Performance Features

### Prepared Statements

```typescript
// High-performance prepared queries
export const getUserByIdPrepared = db
  .select()
  .from(users)
  .where(eq(users.id, placeholder('id')))
  .prepare();

// Usage with full type safety
const user = await getUserByIdPrepared.execute({ id: 123 });
```

### Query Optimization

```typescript
// Optimized pagination with count
export async function getPaginatedPosts(page = 1, limit = 10) {
  const offset = (page - 1) * limit;
  
  const [posts, totalCount] = await Promise.all([
    db.select().from(posts).limit(limit).offset(offset),
    db.select({ count: count() }).from(posts),
  ]);
  
  return { posts, total: totalCount[0].count };
}
```

### Connection Pooling

```typescript
// Production-ready connection pooling
const poolConnection = mysql.createPool({
  connectionLimit: 10,
  queueLimit: 0,
  acquireTimeout: 60000,
  timeout: 60000,
});

export const db = drizzle(poolConnection);
```

## 🧪 Testing Support

### Test Database Setup

```typescript
// In-memory testing database
import { drizzle } from 'drizzle-orm/better-sqlite3';
import Database from 'better-sqlite3';

export function createTestDb() {
  const sqlite = new Database(':memory:');
  const db = drizzle(sqlite);
  migrate(db, { migrationsFolder: 'drizzle' });
  return db;
}
```

### Query Testing

```typescript
// Comprehensive query testing
describe('User Queries', () => {
  let testDb: ReturnType<typeof createTestDb>;
  
  beforeEach(() => {
    testDb = createTestDb();
  });
  
  it('should create and retrieve user', async () => {
    const user = await createUser({ email: 'test@example.com' });
    const retrieved = await getUserById(user.id);
    expect(retrieved).toEqual(user);
  });
});
```

## 🌐 Multi-Database Support

### PostgreSQL with Neon

```typescript
import { drizzle } from 'drizzle-orm/neon-http';
import { neon, neonConfig } from '@neondatabase/serverless';

neonConfig.fetchConnectionCache = true;
export const db = drizzle(neon(process.env.DATABASE_URL!));
```

### MySQL with PlanetScale

```typescript
import { drizzle } from 'drizzle-orm/mysql2';
import { connect } from '@planetscale/database';

const connection = connect({
  url: process.env.DATABASE_URL
});

export const db = drizzle(connection);
```

### SQLite for Local Development

```typescript
import { drizzle } from 'drizzle-orm/better-sqlite3';
import Database from 'better-sqlite3';

const sqlite = new Database('./dev.db');
export const db = drizzle(sqlite);
```

## 📊 Advanced Features

### Transaction Handling

```typescript
// Safe transaction management
export async function transferFunds(fromId: number, toId: number, amount: number) {
  return await db.transaction(async (tx) => {
    await tx.update(accounts)
      .set({ balance: sql`${accounts.balance} - ${amount}` })
      .where(eq(accounts.id, fromId));
      
    await tx.update(accounts)
      .set({ balance: sql`${accounts.balance} + ${amount}` })
      .where(eq(accounts.id, toId));
  });
}
```

### Analytics Queries

```typescript
// Complex analytical queries
export async function getSalesAnalytics() {
  return await db
    .select({
      month: sql`DATE_TRUNC('month', ${orders.createdAt})`,
      revenue: sum(orders.total),
      orderCount: count(orders.id),
    })
    .from(orders)
    .groupBy(sql`DATE_TRUNC('month', ${orders.createdAt})`)
    .orderBy(sql`DATE_TRUNC('month', ${orders.createdAt})`);
}
```

## 🔗 Integration

This configuration works excellently with:

- **Next.js 15** - API routes and Server Components
- **Vercel AI SDK** - Chat history and user management
- **shadcn/ui** - Data tables and forms
- **Neon/PlanetScale** - Serverless database platforms
- **Prisma Studio alternative** - Drizzle Studio for database browsing

## 📚 Resources

- [Drizzle ORM Documentation](https://orm.drizzle.team)
- [Drizzle Kit CLI Reference](https://orm.drizzle.team/kit-docs/overview)
- [Schema Declaration Guide](https://orm.drizzle.team/docs/sql-schema-declaration)
- [Query Builder Reference](https://orm.drizzle.team/docs/rqb)
- [Migration Documentation](https://orm.drizzle.team/docs/migrations)
- [Community Discord](https://discord.gg/yfjTbVXMW4)

---

**Ready to build type-safe, performant database applications with Claude Code and Drizzle ORM!**

🌟 **Star this configuration** if it accelerates your database development workflow!
