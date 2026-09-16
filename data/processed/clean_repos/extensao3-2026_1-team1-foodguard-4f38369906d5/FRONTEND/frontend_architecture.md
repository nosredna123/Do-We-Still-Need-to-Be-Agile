# FoodGuard — Frontend Architecture

> **Read this file before any modification or feature addition.**
> It describes the project structure, conventions, and data flow to ensure consistency.

---

## Tech stack

| Technology | Version | Role |
|---|---|---|
| React | 19.2 | UI framework |
| TypeScript | 5.9 | Static typing |
| Vite | 8.0 | Build tool + dev server |
| React Router DOM | 7.13 | Routing |
| TanStack Query | 5.90 | Server state management (not widely used yet — QueryClientProvider already set up) |
| Axios | 1.13 | HTTP client |
| Tailwind CSS | 3.4 | Styling |
| shadcn/ui + Radix UI | — | Accessible UI components |
| lucide-react + react-icons | — | Icons |
| zxing-wasm | 3.0 | Barcode reading (WASM fallback) |
| date-fns | 4.1 | Date utilities |

---

## Directory structure

```
FRONTEND/
├── src/
│   ├── App.tsx                    # App root: providers + routes
│   ├── main.tsx                   # Entry point: ReactDOM.createRoot
│   ├── index.css                  # Global styles / CSS variables
│   │
│   ├── pages/
│   │   └── Index.tsx              # Only page — main chat layout
│   │
│   ├── components/
│   │   ├── navbar/
│   │   │   └── Navbar.tsx         # Header: app name, nav links, profile dropdown
│   │   ├── sideBar/
│   │   │   └── SideBar.tsx        # Conversation list: toggle, new chat, delete
│   │   ├── chatInput/
│   │   │   └── ChatInput.tsx      # Text input + image upload + barcode scan
│   │   ├── chatMessages/
│   │   │   └── ChatMessages.tsx   # Message history rendering (user / assistant)
│   │   ├── emptyChat/
│   │   │   └── EmptyChat.tsx      # Empty state screen (logo + tagline)
│   │   └── ui/                    # shadcn/ui components (CLI-generated — do not edit manually)
│   │       ├── button.tsx
│   │       ├── calendar.tsx
│   │       ├── drawer.tsx
│   │       └── dropdown-menu.tsx
│   │
│   ├── hooks/
│   │   ├── use-chat.ts            # Orchestrator: combines use-chat-list + use-messages, exposes unified API
│   │   ├── use-chat-list.ts       # Chat list state: fetch, addChat, removeChat, activeId, handleSelect/Delete
│   │   ├── use-messages.ts        # Message state: fetch per chat, optimistic send, clearMessages
│   │   ├── use-barcode.ts         # Barcode reading (native BarcodeDetector or zxing-wasm)
│   │   └── use-open-food.ts       # Fetch product data from Open Food Facts
│   │
│   ├── enums/
│   │   └── MessageRole.ts         # MessageRole const + type ("U" = User, "A" = Assistant)
│   │
│   ├── services/
│   │   ├── chat.service.ts        # chatService.listar(), chatService.deletar()
│   │   ├── message.service.ts     # messageService.listar(), messageService.enviar()
│   │   ├── open-food.service.ts   # openFoodService.getProduto()  →  wrapper over openFoodRest
│   │   ├── algo.service.ts        # Example/template service — delete when no longer needed
│   │   └── rest/
│   │       ├── chat.rest.ts       # HTTP calls to /chats/ (getChats, deleteChat)
│   │       ├── message.rest.ts    # HTTP calls to /chats/{id}/messages/ and /chats/message/send/
│   │       ├── open-food.rest.ts  # HTTP calls to Open Food Facts (baseURL: /openfood)
│   │       └── algo.rest.ts       # Example/template REST layer
│   │
│   ├── models/
│   │   ├── chat.model.ts          # Chat, PaginatedResponse<T>
│   │   ├── message.model.ts       # Message, MessageCreateRequest, MessageCreateResponse (imports MessageRole from enums/)
│   │   └── open-food.model.ts     # IOpenFoodProduct, IImageArray, nutrition inner types
│   │
│   ├── config/
│   │   ├── axiosConfig.ts         # Axios instance factory with Basic Auth and interceptors
│   │   └── api.ts                 # HTTP utility functions: get, post, put, patch, delete
│   │
│   ├── lib/
│   │   └── utils.ts               # cn() — Tailwind class merge helper (clsx + tailwind-merge)
│   │
│   ├── router/
│   │   └── router.tsx             # Present but empty — routes are defined in App.tsx
│   │
│   └── workers/
│       └── index.worker.ts        # Present but empty — reserved for future Web Workers
│
├── public/                        # Static assets served directly
├── index.html                     # HTML template (Vite entry)
├── vite.config.ts                 # Vite config: @/ alias, /api and /openfood proxies
├── tailwind.config.js             # foodguard color palette, Sansita font
├── tsconfig.json / tsconfig.app.json / tsconfig.node.json
├── components.json                # shadcn/ui config
├── .env.example                   # Required environment variables
└── package.json
```

---

## Data flow and layered architecture

```
Page (Index.tsx)
  └── Hook (use-chat.ts)  ← orchestrator
        ├── Hook (use-chat-list.ts)  ──→  Service (chat.service.ts)     ──→  REST (chat.rest.ts)     ──→  config/api.ts  ──→  Django backend
        └── Hook (use-messages.ts)  ──→  Service (message.service.ts)  ──→  REST (message.rest.ts)  ──→  config/api.ts  ──→  Django backend

Component (ChatInput.tsx)
  ├── Hook (use-barcode.ts)     ──→  native BarcodeDetector or zxing-wasm
  └── Hook (use-open-food.ts)  ──→  Service (open-food.service.ts)  ──→  REST (open-food.rest.ts)  ──→  Open Food Facts API
```

### Layer rules

1. **Components** — rendering and user interaction only. Delegate logic to hooks.
2. **Hooks** — orchestrate local state and call services. Never make direct HTTP calls.
3. **Services** (`services/*.service.ts`) — business logic, data transformation, REST call composition. Export a named object (e.g. `chatService`), not standalone functions.
4. **REST** (`services/rest/*.rest.ts`) — pure HTTP calls. Only map endpoints to functions. Export a named object (e.g. `chatRest`).
5. **Enums** (`enums/*.ts`) — shared constants using the `as const` + union type pattern. Import the value (const) separately from the type where needed.
6. **Config** — Axios configured once. Do not duplicate instances.
7. **Models** — TypeScript interfaces and types only. No logic. Import enums from `enums/` when needed.

---

## Environment configuration

`.env` file (based on `.env.example`):

```env
VITE_OPENFOOD_URL=https://world.openfoodfacts.org/api/v0/product/
VITE_BASE_URL=http://localhost:8000
```

Vite proxy rewrites:
- `/api/*` → `VITE_BASE_URL` (Django backend)
- `/openfood/*` → `VITE_OPENFOOD_URL` (Open Food Facts)

Backend authentication uses **JWT (access + refresh)** via `djangorestframework-simplejwt`.
Tokens are stored in `localStorage` (`config/tokenStorage.ts`) and injected as
`Authorization: Bearer <access>` by the request interceptor in `axiosConfig.ts`.
On a `401`, the response interceptor transparently refreshes the access token once
(`/auth/token/refresh/`) and retries; if refresh fails, storage is cleared and the
user is sent to `/login`.

### Auth layer

| File | Role |
|---|---|
| `config/tokenStorage.ts` | localStorage helpers for access/refresh/user |
| `context/AuthContext.tsx` | global session state (`user`, `isAuthenticated`, `hasAnamnese`, `login`, `register`, `logout`, `markAnamneseDone`) |
| `hooks/use-auth.ts` | `useAuth()` consumer of `AuthContext` |
| `services/auth.service.ts` + `rest/auth.rest.ts` | register / login / logout / me |
| `services/anamnese.service.ts` + `rest/anamnese.rest.ts` | create / get / update anamnese |
| `models/auth.model.ts`, `models/anamnese.model.ts` | typed payloads mirroring the backend |

---

## Routing

- Defined in `src/router/router.tsx` using `createBrowserRouter`; `App.tsx` wraps it in `<AuthProvider>` + `RouterProvider`.
- Route guards live in `src/router/guards.tsx` (kept separate so `router.tsx` only exports the route object — Fast Refresh rule):
  - `GuestOnlyRoute` — `/login`, `/cadastro`, `/esqueci-senha`; redirects authenticated users to `/chat` (RN007).
  - `ProtectedRoute` — requires an active session; otherwise redirects to `/login` (RN007).
  - `GalleryRoute` — anamnese gate (RN001): `/galeria` requires a completed anamnese, else redirects to `/anamnese`.
  - `ChatRoute` — anamnese gate (RN001): `/chat` and `/chat/:chatId` require a completed anamnese; `:chatId` opens that conversation in `Index` via `initialChatId`.
- Routes: `/` (Landing), `/login`, `/cadastro`, `/esqueci-senha`, `/anamnese` (`AnamneseGate`), `/galeria` (`Galeria` — post-login home), `/chat` + `/chat/:chatId` (`Index`).
- **Post-login landing is `/galeria`** (the chat gallery). `LandingRoute`, `GuestOnlyRoute` and `Login` all redirect authenticated users there.

### Gallery (`/galeria`)

- `pages/Galeria.tsx` — chat gallery grid. A "Criar nova conversa" card (→ `/chat`) plus one `ChatCard` per conversation. Filter tabs by severity (Todos / Seguros / Atenção / Perigosos).
- `components/gallery/ChatCard.tsx` — card: product image (`chat.image_url`) or default `Utensils` icon, severity badge (`VERDICT_META`), title, date (`date-fns` ptBR), and a `...` delete menu.
- `hooks/use-gallery.ts` — fetches chats (`chatService.listar`), holds the severity filter, exposes `filteredChats` and `handleDelete`.
- `lib/verdict.ts` — `SEVERITY_FILTERS` (filter buckets) + `matchesSeverityFilter()` map the 5 verdict levels to the gallery tabs.

---

## Color palette (Tailwind)

Brand primary color: **foodguard**

| Token | Hex |
|---|---|
| `foodguard-50` | `#EDFFF6` |
| `foodguard-100` | `#DAFFED` |
| `foodguard-300` | `#A5E6CC` |
| `foodguard-500` | `#008B5B` (primary) |
| `foodguard-600` | `#00784F` |
| `foodguard-950` | `#001E14` |

Custom font: `font-sansita` (Sansita, sans-serif) — used in headings and logo.

Class utility: always use `cn()` from `@/lib/utils` for conditional Tailwind class merging.

---

## UI components (shadcn/ui)

Located in `src/components/ui/`. shadcn-generated components are updated via `shadcn` CLI — **do not edit those manually** (customizations go in CSS variables in `index.css` or by overriding classes at the usage site).

Available (shadcn): `button`, `calendar`, `drawer`, `dropdown-menu`.

Custom shared primitives (hand-written, safe to edit): `Radio`, `PasswordField`.
- `PasswordField` — password input with show/hide toggle and optional live strength meter + requirements checklist (`showStrength`) and inline `error` message. Strength/criteria logic lives in `src/lib/password.ts` (mirrors `PASSWORD_REGEX`). Used in `CadastroForm` and `EditProfileModal`.

### Notifications (toast / snackbar)

- `context/ToastContext.tsx` — `<ToastProvider>` (mounted in `App.tsx`, inside `AuthProvider`) renders a Radix Toast viewport (bottom-right). Variants: `default` / `success` / `error`; supports optional `action` (e.g. "Desfazer") and `duration`.
- `hooks/use-toast.ts` — `useToast()` → `{ toast({ title?, description, variant?, action?, duration? }) }`.
- **When to use:** transient confirmations of completed async actions or background errors (delete, profile/anamnese update, register, logout). Keep **form validation errors inline** (Login, register, anamnese) — they stay next to the field.

---

## Key data models

### Chat
```ts
interface Chat {
  id: string;
  title: string | null;
  created_at: string;
  is_active: boolean;
  is_open: boolean;
  image_url: string | null;   // product image (OpenFoodFacts), shown on gallery card
  severity: Verdict | null;   // most recent verdict of the chat — drives badge + filter
  messages: string;
}
```

### MessageRole (enum — `src/enums/MessageRole.ts`)
```ts
const MessageRole = { User: "U", Assistant: "A" } as const;
type MessageRole = (typeof MessageRole)[keyof typeof MessageRole];
```
Import the **value** (`import { MessageRole }`) to use `MessageRole.User` in logic.
Import only the **type** (`import type { MessageRole }`) when typing interfaces.

### Message (backend — `src/models/message.model.ts`)
```ts
interface Message { chat_id, role: MessageRole, content, created_at }
interface MessageCreateRequest { role: MessageRole, content, chat_id? }
interface MessageCreateResponse { chat_id, response }
```

### Message (frontend — `src/hooks/use-messages.ts`)
```ts
interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  image?: File;
  imageUrl?: string;
  pending?: boolean; // true while waiting for backend response
}
```

**Note:** backend `MessageRole` (`"U"/"A"`) is mapped to frontend role (`"user"/"assistant"`) in `mapBackendMessages()` inside `use-messages.ts`.

---

## Naming conventions

| Type | Convention | Example |
|---|---|---|
| Components | PascalCase | `ChatInput.tsx` |
| Hooks | kebab-case with `use-` prefix | `use-chat.ts` |
| Services | kebab-case with `.service` suffix | `chat.service.ts` |
| REST | kebab-case with `.rest` suffix | `open-food.rest.ts` |
| Models | kebab-case with `.model` suffix | `chat.model.ts` |
| Enums | PascalCase with no suffix | `MessageRole.ts` |
| Interfaces | PascalCase with `I` prefix (external) | `IOpenFoodProduct` |
| Import alias | `@/` maps to `src/` | `@/hooks/use-chat` |

---

## Feature checklist

- [ ] TypeScript model for the data? Add to `src/models/`.
- [ ] New shared constant with multiple named values? Create an enum in `src/enums/` using the `as const` + union type pattern.
- [ ] New HTTP endpoint needed? Create or update the corresponding `.rest.ts` file.
- [ ] Business logic or data transformation? Encapsulate in a `.service.ts`.
- [ ] State with side-effects? Create a custom hook in `src/hooks/`.
- [ ] Colors from the `foodguard` palette? Use Tailwind tokens, not inline hex values.
- [ ] Conditional classes use `cn()` from `@/lib/utils`?
- [ ] New components go in `src/components/<name>/` subfolders?
- [ ] New base UI component (button, dialog, etc.)? Generate via `shadcn` CLI, not manually.
- [ ] New route? Add in `App.tsx`.
