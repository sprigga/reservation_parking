FROM node:20-alpine

WORKDIR /app

# Install deps first (use cache when possible)
COPY package.json ./
# If you add a lockfile later, uncomment the next line to use it
# COPY package-lock.json ./
RUN npm install

# Copy the rest of the app
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
