FROM node:21-alpine AS development

RUN mkdir /project
WORKDIR /project

COPY . .

RUN yarn global add @vue/cli
RUN yarn install

RUN yarn run build
CMD ["yarn", "preview", "--host"]
EXPOSE 4173