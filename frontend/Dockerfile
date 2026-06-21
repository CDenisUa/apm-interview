# Dev-oriented image: runs the Vite dev server with HMR.
# The source is bind-mounted by docker-compose, so edits reload live.
FROM node:22-alpine

WORKDIR /app

# Install deps first so this layer is cached unless package files change.
COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

# --host makes the dev server reachable from outside the container.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
