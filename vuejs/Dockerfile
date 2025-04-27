FROM node:22-alpine AS build
RUN mkdir /app
WORKDIR /app

COPY package*.json ./
RUN yarn global add @vue/cli
RUN yarn install

COPY . .
RUN yarn run build


FROM nginx:stable-alpine as production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]