# Use an official lightweight Node.js image as a parent image
FROM node:16-alpine

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the package.json and package-lock.json (or yarn.lock) files
COPY package*.json ./

# Install dependencies
RUN npm install

# Bundle app source inside Docker image
COPY . .

# Build the application for production
RUN npm run build