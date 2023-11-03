FROM node:18.17 AS builder

WORKDIR /app

COPY package*.json .
COPY yarn.lock .yarnrc.yml ./
COPY .yarn ./.yarn
RUN yarn install
COPY . /app/
RUN yarn build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/build build/
COPY --from=builder /app/node_modules node_modules/
COPY package.json .
EXPOSE 3000
ENV NODE_ENV=production
CMD [ "node", "build" ]