# Build multi-stage: compila o Vite/React e serve os arquivos
# estaticos resultantes via nginx -- a imagem final nao carrega
# node_modules nem o toolchain de build, so o output (Etapa 7,
# secao 7.6).

FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# VITE_API_URL e resolvida em BUILD TIME (convencao do Vite), nao em
# runtime -- e por isso que e um ARG do build, nao uma variavel de
# ambiente do container final. O default aponta para localhost:8000
# porque quem executa o JS e o NAVEGADOR do usuario, fora da rede
# interna do docker-compose: "http://backend:8000" (o hostname
# interno) nao resolveria daí.
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
