# Frontend Dockerfile
# Multi-stage build: compile React/Vite then serve

FROM node:24-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --prefer-offline --no-audit

# Copy application code
COPY public/ public/
COPY src/ src/
COPY index.html vite.config.js ./

# Build argument for backend API URL (used at build time by Vite)
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

# Build with Vite
RUN npm run build

# Production stage: serve built assets
FROM node:24-alpine

WORKDIR /app

# Install a lightweight HTTP server for serving SPA
RUN npm install -g serve

# Copy built application from builder
COPY --from=builder /app/dist /app/dist

# Expose frontend port
EXPOSE 3000

# Set environment for serving
ENV NODE_ENV=production

# Start server on port 3000, serving the dist directory
# The -s flag enables SPA mode (single page application)
CMD ["serve", "-s", "dist", "-l", "3000"]
