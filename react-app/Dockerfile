# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including dev dependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Set environment variables for production build
ENV VITE_API_URL=https://intelliassist-ai-backend-2025.fly.dev
ENV VITE_SUPABASE_URL=https://kbnnbqxklvguxchrdgel.supabase.co
ENV VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtibm5icXhrbHZndXhjaHJkZ2VsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA2NzMxNjUsImV4cCI6MjA2NjI0OTE2NX0.ylF0u4zwkC6BXo020ySGauz88RA2ptvYZ3KZa1lA8zw

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 