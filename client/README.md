# DevOps Farm - React Frontend

A modern React frontend for the DevOps Farm management system built with Create React App.

## Features

- **User Management**: Create, read, update, delete users
- **Blog Management**: Create, read, update, delete blog posts
- **Responsive Design**: Modern UI with mobile-first approach
- **API Integration**: Seamless connection with FastAPI backend
- **Error Handling**: Comprehensive error states and loading indicators
- **Modern React**: Uses hooks and functional components

## Technology Stack

- **React 18** - Latest React with Concurrent Features
- **Axios** - HTTP client for API requests
- **CSS3** - Modern styling with Flexbox and Grid
- **Create React App** - Build tooling and development server

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- FastAPI backend running on port 8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

### Building for Production

```bash
npm run build
```

This builds the app for production and moves it to `../client_build` folder, which is served by the FastAPI backend.

## API Integration

The frontend connects to the FastAPI backend at:
- **Development**: `http://localhost:8000`
- **Production**: Same domain as the app

### API Endpoints Used

- `GET /user` - Fetch all users
- `POST /user` - Create new user
- `PUT /user/{id}` - Update user
- `DELETE /user/{id}` - Delete user
- `GET /blog` - Fetch all blogs
- `POST /blog` - Create new blog
- `PUT /blog/{id}` - Update blog
- `DELETE /blog/{id}` - Delete blog

## Project Structure

```
client/
├── public/
│   ├── index.html
│   ├── manifest.json
│   └── robots.txt
├── src/
│   ├── App.js          # Main application component
│   ├── App.css         # Application styles
│   ├── index.js        # React entry point
│   └── index.css       # Global styles
├── package.json        # Dependencies and scripts
└── README.md          # This file
```

## Development

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### Code Style

- Uses modern React hooks (useState, useEffect)
- Functional components only
- Responsive design principles
- Error handling and loading states
- Clean, maintainable code structure

## Deployment

The frontend is automatically built and served by the FastAPI backend in production. The GitHub Actions workflow handles:

1. Building the React app
2. Moving build files to `client_build/`
3. Including in Docker image
4. Deploying to AWS ECS

## Contributing

1. Make changes to components in `src/`
2. Test locally with `npm start`
3. Build with `npm run build`
4. Commit and push - GitHub Actions handles deployment

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
