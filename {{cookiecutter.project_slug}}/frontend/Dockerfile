FROM node:20-slim

WORKDIR /app

# Install dependencies strictly from lockfile
COPY package*.json ./
RUN npm ci

# Copy application code (ignoring node_modules/ via .dockerignore)
COPY . .

CMD ["npm", "run", "dev", "--", "--host"]
