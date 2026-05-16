FROM node:24.13.1

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install npm packages
RUN npm install

# Copy frontend source
COPY . .

# Expose Vite port
EXPOSE 5173

# Start Vue dev server
CMD ["npm", "run", "dev", "--", "--host"]