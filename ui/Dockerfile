FROM node:18.17 as build

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH

COPY package.json .
COPY yarn.lock .yarnrc.yml ./
COPY .yarn ./.yarn
RUN yarn install
COPY . /app/
RUN yarn dev --host