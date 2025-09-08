FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY ./frontend/package*.json ./

# Expose port 3000
EXPOSE 3000

# Install dependencies and start the development server
CMD ["sh", "-c", "npm install && npm run dev"]
