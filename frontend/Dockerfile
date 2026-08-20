# ── Frontend Dockerfile ────────────────────────────────────────────────────
# Multi-stage: deps → build → runtime (Next.js standalone).
# Target: Cloud Run. Puerto configurado por env $PORT (default 3000).
# ──────────────────────────────────────────────────────────────────────────

# ── Stage 1: deps ─────────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev


# ── Stage 2: build ────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

# Copiar deps instaladas
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# NEXT_PUBLIC_API_URL se inyecta en build time desde el secreto de Cloud Build
# Si no se define, los componentes usan el fallback http://localhost:8000
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Habilitar output standalone (reduce tamaño imagen final a ~50 MB)
RUN npm run build


# ── Stage 3: runtime ──────────────────────────────────────────────────────
FROM node:20-alpine AS runtime

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

WORKDIR /app

# Solo el output standalone + static assets
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

ENV PORT=3000
ENV NODE_ENV=production

EXPOSE $PORT

CMD ["node", "server.js"]
