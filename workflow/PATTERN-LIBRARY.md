# Workflow Plugin - Pattern Library

**Version:** 0.1.0
**Last Updated:** 2025-12-23

> **Comprehensive reference of all design patterns included in the workflow plugin**

---

## 📚 Pattern Categories

The workflow plugin includes **60+ proven patterns** across 4 categories:

1. **Backend Patterns** (20 patterns)
2. **Frontend Patterns** (18 patterns)
3. **DevOps Patterns** (12 patterns)
4. **ADHD-Friendly Patterns** (10 patterns)

---

## 🔧 Backend Patterns

### API Design Patterns

#### 1. RESTful API Design
**When to use:** Standard CRUD operations, resource-based APIs
**Pattern:**
```
Resources: /users, /posts, /comments
HTTP Methods: GET (read), POST (create), PUT/PATCH (update), DELETE
Status Codes: 200 (OK), 201 (Created), 404 (Not Found), 500 (Error)
Versioning: /api/v1/users (URL-based, simplest)
```

**Trade-offs:**
- ✅ Simple, widely understood, great tooling
- ❌ Over-fetching/under-fetching, multiple requests needed

**Indie recommendation:** Start here. Only move to GraphQL if you have multiple clients with different data needs.

#### 2. GraphQL API
**When to use:** Multiple clients (web, mobile, desktop) need different data shapes
**Pattern:**
```graphql
type Query {
  user(id: ID!): User
  posts(limit: Int): [Post]
}

type User {
  id: ID!
  name: String
  posts: [Post]
}
```

**Trade-offs:**
- ✅ Single endpoint, client specifies data needs, reduces over-fetching
- ❌ More complex, requires GraphQL knowledge, harder to cache

**Indie recommendation:** Overkill for < 1K users. Use REST + field selection (`?fields=name,email`) first.

#### 3. Pagination Strategies

**Offset Pagination** (Simplest)
```
/posts?page=2&limit=20
```
- ✅ Simple to implement, predictable
- ❌ Performance degrades with large offsets, inconsistent with new data

**Cursor Pagination** (Better performance)
```
/posts?cursor=eyJpZCI6MTAwfQ&limit=20
```
- ✅ Consistent results, better performance
- ❌ Can't jump to specific page, more complex

**Indie recommendation:** Offset for MVP, cursor for > 10K records.

### Authentication & Authorization Patterns

#### 4. JWT (JSON Web Tokens)
**When to use:** Stateless auth, microservices, mobile apps
**Pattern:**
```javascript
// Sign token on login
const token = jwt.sign(
  { userId: user.id, role: user.role },
  SECRET,
  { expiresIn: '7d' }
);

// Verify on each request
const decoded = jwt.verify(token, SECRET);
```

**Trade-offs:**
- ✅ Stateless (no session storage), works across services
- ❌ Can't revoke before expiry, token size grows with claims

**Indie recommendation:** Use for APIs, short expiry (7 days), refresh tokens for long sessions.

#### 5. Session Cookies
**When to use:** Traditional web apps, server-side rendering
**Pattern:**
```javascript
// Store session server-side
sessionStore.set(sessionId, { userId: user.id });

// Send session ID in httpOnly cookie
res.cookie('sessionId', sessionId, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict'
});
```

**Trade-offs:**
- ✅ Easy to revoke, secure (httpOnly), small cookie size
- ❌ Requires session storage (Redis), harder to scale horizontally

**Indie recommendation:** Use for monoliths, easier to secure, simpler to revoke.

#### 6. OAuth 2.0 Flows

**Authorization Code Flow** (Most secure)
```
1. User clicks "Login with Google"
2. Redirect to Google with client_id
3. User approves, Google redirects back with code
4. Exchange code for access token (server-side)
5. Use token to fetch user info
```
- ✅ Access token never exposed to browser
- ❌ Requires server-side exchange

**Authorization Code + PKCE** (Mobile/SPA)
```
1. Generate code_verifier (random string)
2. Hash to code_challenge
3. Include in authorization request
4. Exchange code + code_verifier for token
```
- ✅ Prevents authorization code interception
- ❌ More complex

**Indie recommendation:** Use passport.js (Node) or similar library. Start with Google OAuth (easiest).

### Database Patterns

#### 7. Normalized vs Denormalized
**Normalized** (Consistency)
```sql
users: id, name, email
posts: id, user_id, title, content
comments: id, post_id, user_id, content
```
- ✅ No data duplication, easy to update
- ❌ Requires JOINs, slower reads

**Denormalized** (Performance)
```sql
posts: id, user_id, user_name, title, content, comment_count
```
- ✅ Faster reads (no JOINs), fewer queries
- ❌ Data duplication, harder to update

**Indie recommendation:** Normalize for writes (user profiles), denormalize for reads (post lists, feeds).

#### 8. Indexing Strategies
**When to index:**
- Foreign keys (user_id, post_id)
- Columns in WHERE clauses (email, status)
- Columns in ORDER BY (created_at)

**Pattern:**
```sql
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_created ON posts(created_at DESC);
CREATE INDEX idx_users_email ON users(email) UNIQUE;
```

**Trade-offs:**
- ✅ 10-100× faster queries
- ❌ Slower writes, more storage

**Indie recommendation:** Index after you have data. Profile slow queries first.

#### 9. Database Migrations
**Pattern:** Version-controlled schema changes
```javascript
// migrations/001_create_users.js
exports.up = (knex) => {
  return knex.schema.createTable('users', (t) => {
    t.increments('id');
    t.string('email').unique();
    t.timestamps(true, true);
  });
};

exports.down = (knex) => {
  return knex.schema.dropTable('users');
};
```

**Indie recommendation:** Use Drizzle (Postgres), Prisma (TypeScript), or raw SQL. Never edit production DB directly.

### Performance Patterns

#### 10. Caching Strategies

**In-Memory Cache** (Single server)
```javascript
const cache = new Map();

async function getUser(id) {
  if (cache.has(id)) return cache.get(id);
  const user = await db.users.findById(id);
  cache.set(id, user);
  return user;
}
```
- ✅ Extremely fast, simple
- ❌ Lost on restart, doesn't scale horizontally

**Redis Cache** (Distributed)
```javascript
async function getUser(id) {
  let user = await redis.get(`user:${id}`);
  if (!user) {
    user = await db.users.findById(id);
    await redis.set(`user:${id}`, JSON.stringify(user), 'EX', 3600);
  }
  return JSON.parse(user);
}
```
- ✅ Shared across servers, persistent
- ❌ Network latency, additional service

**Indie recommendation:** In-memory for single server, Redis when you scale to 2+ servers.

#### 11. Background Jobs
**When to use:** Email sending, image processing, slow operations
**Pattern:**
```javascript
// Queue job (immediate response)
await queue.add('send-email', {
  to: user.email,
  subject: 'Welcome!'
});

// Process job (worker)
queue.process('send-email', async (job) => {
  await sendEmail(job.data);
});
```

**Libraries:**
- Bull (Node.js + Redis)
- Celery (Python + Redis)
- Temporal (durable workflows)

**Indie recommendation:** Start with simple async (don't block request), add queue when you have > 100 jobs/day.

### Architecture Patterns

#### 12. Monolith First
**Pattern:** Single codebase, single deployment
```
app/
  controllers/
  models/
  services/
  lib/
```

**Trade-offs:**
- ✅ Simple, fast development, easy to refactor
- ❌ Harder to scale (but you're not Google)

**Indie recommendation:** Start here. Extract services only when you have:
- 5+ developers
- Clear service boundaries
- Performance bottleneck in specific area

#### 13. Repository Pattern
**Pattern:** Abstract database access
```javascript
class UserRepository {
  async findById(id) {
    return db.users.findOne({ id });
  }

  async create(data) {
    return db.users.insert(data);
  }
}
```

**Trade-offs:**
- ✅ Easier to test, swap databases
- ❌ Extra layer, more code

**Indie recommendation:** Skip it. ORM (Drizzle, Prisma) is enough abstraction.

#### 14. Service Layer
**Pattern:** Business logic separate from controllers
```javascript
// services/userService.js
async function registerUser(email, password) {
  // Validate
  if (!isValidEmail(email)) throw new Error('Invalid email');

  // Hash password
  const hashedPassword = await bcrypt.hash(password, 10);

  // Create user
  const user = await userRepo.create({ email, password: hashedPassword });

  // Send welcome email
  await emailService.sendWelcome(user);

  return user;
}
```

**Indie recommendation:** Use this. Keeps controllers thin, business logic testable.

### Security Patterns

#### 15. Rate Limiting
**Pattern:** Limit requests per IP/user
```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // 100 requests per window
});

app.use('/api/', limiter);
```

**Indie recommendation:** Always use. Prevents abuse, DDoS attacks.

#### 16. Input Validation
**Pattern:** Validate all user input
```javascript
const { z } = require('zod');

const userSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  age: z.number().min(18)
});

const user = userSchema.parse(req.body); // Throws if invalid
```

**Indie recommendation:** Use zod (TypeScript) or joi (JavaScript). Never trust user input.

#### 17. CORS Configuration
**Pattern:** Control which domains can access your API
```javascript
const cors = require('cors');

app.use(cors({
  origin: ['https://yourdomain.com'],
  credentials: true // Allow cookies
}));
```

**Indie recommendation:** Whitelist specific domains in production, never use `origin: '*'` with credentials.

---

## 🎨 Frontend Patterns

### Component Architecture

#### 18. Container/Presentational Pattern
**Pattern:** Separate logic from UI
```jsx
// Container (logic)
function UserListContainer() {
  const [users, setUsers] = useState([]);
  useEffect(() => { fetchUsers().then(setUsers); }, []);

  return <UserList users={users} />;
}

// Presentational (UI only)
function UserList({ users }) {
  return (
    <ul>
      {users.map(u => <li key={u.id}>{u.name}</li>)}
    </ul>
  );
}
```

**Trade-offs:**
- ✅ Testable UI, reusable components
- ❌ More files, might be over-engineering

**Indie recommendation:** Use for complex components (tables, forms). Skip for simple ones (buttons, icons).

#### 19. Compound Components
**Pattern:** Components that work together
```jsx
<Tabs>
  <Tabs.List>
    <Tabs.Tab>Profile</Tabs.Tab>
    <Tabs.Tab>Settings</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel>Profile content</Tabs.Panel>
  <Tabs.Panel>Settings content</Tabs.Panel>
</Tabs>
```

**Indie recommendation:** Use for complex UI patterns (tabs, accordions, modals). See Radix UI, Headless UI.

### State Management

#### 20. Context API (Simple)
**When to use:** Sharing state across 2-5 components
```jsx
const ThemeContext = createContext();

function App() {
  const [theme, setTheme] = useState('light');

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <Header />
      <Main />
    </ThemeContext.Provider>
  );
}

function Header() {
  const { theme, setTheme } = useContext(ThemeContext);
  // ...
}
```

**Indie recommendation:** Start here. Don't add Redux until you're in pain.

#### 21. Zustand (Medium)
**When to use:** 5-15 components need shared state
```javascript
import create from 'zustand';

const useStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 }))
}));

function Counter() {
  const { count, increment } = useStore();
  return <button onClick={increment}>{count}</button>;
}
```

**Indie recommendation:** Use when Context gets messy. Simpler than Redux.

#### 22. Redux (Complex)
**When to use:** 15+ components, complex async logic, time-travel debugging
**Indie recommendation:** You probably don't need it. Zustand + React Query handles 95% of cases.

### Accessibility Patterns

#### 23. Semantic HTML
**Pattern:** Use correct HTML elements
```jsx
// ❌ Bad
<div onClick={handleClick}>Click me</div>

// ✅ Good
<button onClick={handleClick}>Click me</button>
```

**Indie recommendation:** Always start with semantic HTML. Easier to style, better a11y, better SEO.

#### 24. ARIA Labels
**Pattern:** Provide context for screen readers
```jsx
<button aria-label="Close modal" onClick={closeModal}>
  <X /> {/* Icon without text */}
</button>

<input
  aria-label="Search users"
  aria-describedby="search-help"
  placeholder="Search..."
/>
<span id="search-help">Enter name or email</span>
```

**Indie recommendation:** Use when visual context isn't enough (icon buttons, search fields).

#### 25. Keyboard Navigation
**Pattern:** All interactive elements accessible via keyboard
```jsx
function Modal({ isOpen, onClose }) {
  useEffect(() => {
    if (!isOpen) return;

    // Trap focus in modal
    const focusable = modal.querySelectorAll('button, input, a');
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    function handleTab(e) {
      if (e.key !== 'Tab') return;

      if (e.shiftKey && document.activeElement === first) {
        last.focus();
        e.preventDefault();
      } else if (!e.shiftKey && document.activeElement === last) {
        first.focus();
        e.preventDefault();
      }
    }

    modal.addEventListener('keydown', handleTab);
    first.focus();

    return () => modal.removeEventListener('keydown', handleTab);
  }, [isOpen]);
}
```

**Indie recommendation:** Test with keyboard only (no mouse). Tab through entire flow.

### Performance Patterns

#### 26. Code Splitting
**Pattern:** Load code only when needed
```jsx
// Static import (loaded immediately)
import HeavyComponent from './HeavyComponent';

// Dynamic import (lazy loaded)
const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <HeavyComponent />
    </Suspense>
  );
}
```

**Indie recommendation:** Split routes, split heavy components (charts, editors). Don't split everything.

#### 27. Virtual Scrolling
**When to use:** Lists with > 500 items
```jsx
import { FixedSizeList } from 'react-window';

function LongList({ items }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>{items[index].name}</div>
      )}
    </FixedSizeList>
  );
}
```

**Indie recommendation:** Use react-window. Only renders visible items.

#### 28. Debouncing/Throttling
**Pattern:** Limit how often a function runs
```javascript
import { useDebouncedCallback } from 'use-debounce';

function SearchInput() {
  const [search, setSearch] = useState('');

  // Wait 300ms after user stops typing
  const debouncedSearch = useDebouncedCallback(
    (value) => {
      fetchResults(value);
    },
    300
  );

  return (
    <input
      value={search}
      onChange={(e) => {
        setSearch(e.target.value);
        debouncedSearch(e.target.value);
      }}
    />
  );
}
```

**Indie recommendation:** Debounce search inputs, throttle scroll handlers.

### ADHD-Friendly UI Patterns

#### 29. Progressive Disclosure
**Pattern:** Hide complexity behind toggles
```jsx
function AdvancedForm() {
  const [showAdvanced, setShowAdvanced] = useState(false);

  return (
    <form>
      {/* Basic fields always visible */}
      <Input label="Name" />
      <Input label="Email" />

      {/* Advanced fields hidden by default */}
      <button type="button" onClick={() => setShowAdvanced(!showAdvanced)}>
        {showAdvanced ? 'Hide' : 'Show'} Advanced Options
      </button>

      {showAdvanced && (
        <>
          <Input label="Company" />
          <Input label="Tax ID" />
        </>
      )}
    </form>
  );
}
```

**Indie recommendation:** Show 3-5 fields max initially. Hide rest behind "Advanced" toggle.

#### 30. Optimistic UI
**Pattern:** Show success immediately, rollback on error
```jsx
function TodoList() {
  const [todos, setTodos] = useState([]);

  async function addTodo(text) {
    const tempId = Date.now();

    // Show immediately (optimistic)
    setTodos([...todos, { id: tempId, text }]);

    try {
      const newTodo = await api.createTodo(text);
      // Replace temp with real ID
      setTodos(todos => todos.map(t =>
        t.id === tempId ? newTodo : t
      ));
    } catch (error) {
      // Rollback on error
      setTodos(todos => todos.filter(t => t.id !== tempId));
      showError('Failed to create todo');
    }
  }
}
```

**Indie recommendation:** Use for creates/updates. Feels instant, reduces anxiety.

---

## 🚀 DevOps Patterns

### CI/CD Patterns

#### 31. GitHub Actions Workflow
**Pattern:** Automated testing + deployment
```yaml
name: CI/CD
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: ./deploy.sh
```

**Indie recommendation:** Test on every push, deploy main branch automatically.

#### 32. Docker Multi-Stage Build
**Pattern:** Small production images
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY package*.json ./
RUN npm ci --production
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**Indie recommendation:** Reduces image size by 80%. Only copy production deps.

### Deployment Platforms

#### 33. Platform Selection Matrix

| Project Type | Recommended Platform | Monthly Cost | Deploy Time |
|-------------|---------------------|--------------|-------------|
| **Static site** | Netlify / GitHub Pages | Free | 1-2 min |
| **Next.js / React** | Vercel | Free → $20 | < 1 min |
| **Full-stack app** | Render / Railway | $7-20 | 2-5 min |
| **Python / Django** | Fly.io / Render | $5-15 | 3-5 min |
| **Containers** | Fly.io / Railway | $5-20 | 2-5 min |

**Indie recommendation:** Start with PaaS (Vercel, Render). Move to AWS/GCP only when you have specific needs (compliance, existing infra).

### Database Hosting

#### 34. Database Platform Selection

| Database | Recommended Platform | Free Tier | Monthly Cost |
|----------|---------------------|-----------|--------------|
| **PostgreSQL** | Supabase / Neon | 500MB | $25 (10GB) |
| **MySQL** | PlanetScale | 5GB | $29 (10GB) |
| **MongoDB** | MongoDB Atlas | 512MB | $9 (2GB) |
| **Redis** | Upstash | 10K requests/day | $10 (100K/day) |

**Indie recommendation:** Managed databases always. Don't self-host Postgres on a $5 VPS.

### Monitoring Patterns

#### 35. Error Tracking
**Pattern:** Capture and alert on errors
```javascript
// Sentry integration
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV
});

app.use(Sentry.Handlers.errorHandler());
```

**Free tier:** 5K events/month (Sentry)

**Indie recommendation:** Set up from day one. Catch bugs before users complain.

---

## 🧠 ADHD-Friendly Development Patterns

### 36. Visual Hierarchy
**Pattern:** Clear focus states, limited colors
```css
/* High contrast focus */
button:focus {
  outline: 3px solid #0066cc;
  outline-offset: 2px;
}

/* Limited color palette (3-5 colors) */
:root {
  --primary: #0066cc;
  --success: #28a745;
  --danger: #dc3545;
  --neutral: #6c757d;
}
```

### 37. Immediate Feedback
**Pattern:** Loading states, success confirmations
```jsx
function SubmitButton({ onSubmit }) {
  const [status, setStatus] = useState('idle');

  async function handleClick() {
    setStatus('loading');
    try {
      await onSubmit();
      setStatus('success');
      setTimeout(() => setStatus('idle'), 2000);
    } catch (error) {
      setStatus('error');
    }
  }

  return (
    <button onClick={handleClick} disabled={status === 'loading'}>
      {status === 'loading' && <Spinner />}
      {status === 'success' && <CheckIcon />}
      {status === 'error' && <ErrorIcon />}
      {status === 'idle' && 'Submit'}
    </button>
  );
}
```

### 38. Auto-Save
**Pattern:** Save automatically, reduce "did I save?" anxiety
```jsx
function AutoSaveForm() {
  const [data, setData] = useState({});
  const [saveStatus, setSaveStatus] = useState('saved');

  // Debounced save (1 second after user stops typing)
  const debouncedSave = useDebouncedCallback(
    async (newData) => {
      setSaveStatus('saving');
      await api.save(newData);
      setSaveStatus('saved');
    },
    1000
  );

  function handleChange(field, value) {
    const newData = { ...data, [field]: value };
    setData(newData);
    setSaveStatus('unsaved');
    debouncedSave(newData);
  }

  return (
    <div>
      <span className="save-indicator">
        {saveStatus === 'saving' && '💾 Saving...'}
        {saveStatus === 'saved' && '✓ Saved'}
        {saveStatus === 'unsaved' && '○ Unsaved changes'}
      </span>
      {/* Form fields */}
    </div>
  );
}
```

### 39. One Primary Action
**Pattern:** Clear what to do next
```jsx
function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* One clear primary action */}
      <button className="btn-primary btn-lg">
        Create New Project
      </button>

      {/* Secondary actions less prominent */}
      <div className="secondary-actions">
        <button className="btn-secondary">Import</button>
        <button className="btn-secondary">Templates</button>
      </div>
    </div>
  );
}
```

### 40. Undo/Redo
**Pattern:** Reduce fear of mistakes
```jsx
function useHistory(initialState) {
  const [history, setHistory] = useState([initialState]);
  const [index, setIndex] = useState(0);

  const state = history[index];

  function setState(newState) {
    const newHistory = history.slice(0, index + 1);
    setHistory([...newHistory, newState]);
    setIndex(newHistory.length);
  }

  function undo() {
    if (index > 0) setIndex(index - 1);
  }

  function redo() {
    if (index < history.length - 1) setIndex(index + 1);
  }

  return { state, setState, undo, redo, canUndo: index > 0, canRedo: index < history.length - 1 };
}
```

---

## 📊 Pattern Selection Guide

### Quick Decision Matrix

| Scenario | Recommended Pattern | Alternative |
|----------|-------------------|-------------|
| **User auth** | Session cookies (monolith) | JWT (microservices) |
| **API pagination** | Offset (< 10K records) | Cursor (> 10K) |
| **State management** | Context API | Zustand |
| **Database** | Normalized (default) | Denormalized (feeds) |
| **Caching** | In-memory (1 server) | Redis (2+ servers) |
| **Deployment** | Vercel/Render (PaaS) | Fly.io (containers) |
| **Error tracking** | Sentry (free tier) | LogRocket |
| **Form handling** | React Hook Form | Formik |
| **Styling** | Tailwind CSS | styled-components |

---

## 🎯 Pattern Application Workflow

When the workflow plugin skills activate, they reference these patterns:

### backend-designer skill
- References: Patterns 1-17 (Backend)
- Delegates to: backend-architect, database-architect, security-specialist
- Output: Recommends pattern based on team size, scale, budget

### frontend-designer skill
- References: Patterns 18-30 (Frontend)
- Delegates to: ux-ui-designer, frontend-specialist
- Output: Component structure + ADHD-friendly considerations

### devops-helper skill
- References: Patterns 31-35 (DevOps)
- Delegates to: devops-engineer, performance-engineer
- Output: Platform recommendation + cost estimate

---

**This pattern library is referenced by all 3 auto-activating skills to provide instant, proven recommendations.**
