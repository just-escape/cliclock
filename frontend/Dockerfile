FROM node:18-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app

RUN npm install -g http-server

COPY --from=build-stage /app/dist .

EXPOSE 8080

CMD ["http-server", "-p", "8080"]
