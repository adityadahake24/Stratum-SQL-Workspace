FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --prefer-offline

COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.output ./.output

ENV NODE_ENV=production
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
