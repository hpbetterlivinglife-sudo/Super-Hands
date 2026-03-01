# Use official Node.js image
FROM node:20-alpine

# Set the working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy all UI files
COPY . .

# Build the Next.js app for production
RUN npm run build

# Start the UI
CMD ["npm", "start"]
