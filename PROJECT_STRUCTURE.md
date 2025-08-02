# Project Structure

This document provides a comprehensive overview of the Wikipedia Path Finder project structure and architecture.

## 📁 Root Directory Structure

```
WikipediaGame/
├── 📄 README.md              # Main project documentation
├── 📄 LICENSE                # MIT License
├── 📄 requirements.txt       # Python dependencies
├── 📄 DEPLOYMENT.md          # Deployment guide
├── 📄 PROJECT_STRUCTURE.md   # This file
├── 📄 .gitignore            # Git ignore patterns
├── 🔧 setup-dev.sh          # Development environment setup script
├── 🧪 test_simple.py        # Basic test suite
├── 🧪 test_main.py          # Comprehensive test suite
├── 📄 answers.txt           # Sample pathfinding results
├── 📄 path.json             # Path data storage
├── 📄 simple_main.py        # Simple CLI interface
├── 🐳 docker-compose.yml    # Multi-container orchestration
├── 📁 .github/              # GitHub workflows and templates
├── 📁 bot/                  # Backend Python/Node.js services
├── 📁 client/               # Frontend React application
└── 📁 __pycache__/          # Python bytecode cache
```

## 🤖 Backend (`bot/`) Directory

```
bot/
├── 🐍 main.py              # CLI entry point with argparse
├── 🐍 helpers.py           # NLP utilities and Wikipedia processing
├── 🐍 search_functions.py  # Pathfinding algorithms (BFS, DFS)
├── 🐍 wikiapi.py          # Wikipedia API interface
├── 🐍 glove_loader.py     # GloVe embeddings loader
├── 🚀 server.js           # Express.js REST API server
├── 📦 package.json        # Node.js dependencies and scripts
├── 📦 package-lock.json   # Dependency lock file
├── 🔧 ecosystem.config.js # PM2 process configuration
├── 📄 .env               # Environment variables
├── 📁 logs/              # Application logs
└── 📁 __pycache__/       # Python bytecode cache
```

### Backend Architecture

#### Python Modules

1. **`main.py`** - Command Line Interface
   - Argument parsing with `argparse`
   - Search orchestration and coordination
   - Results saving and formatting
   - Error handling and logging

2. **`helpers.py`** - Core Utilities
   - GloVe embeddings management
   - Semantic similarity calculations
   - Wikipedia article processing
   - Goal vector pre-computation

3. **`search_functions.py`** - Pathfinding Algorithms
   - Best-First Search (priority queue based)
   - Depth-First Search (greedy approach)
   - Timeout and memory management
   - Performance tracking

4. **`wikiapi.py`** - Wikipedia Integration
   - HTTP request handling with retries
   - Rate limiting and error handling
   - Concurrent link processing
   - Article validation and parsing

5. **`glove_loader.py`** - Machine Learning
   - Custom GloVe embeddings loader
   - PyTorch tensor operations
   - Caching and optimization
   - Word vector similarity

#### Node.js Server

6. **`server.js`** - REST API
   - Express.js web framework
   - CORS configuration
   - Request validation middleware
   - Health check endpoints
   - Error handling and logging

## ⚛️ Frontend (`client/`) Directory

```
client/
├── 📦 package.json        # Dependencies and build scripts
├── 📦 package-lock.json   # Dependency lock file
├── 🔧 vite.config.js     # Vite build configuration
├── 🔧 vitest.config.js   # Testing configuration
├── 📄 index.html         # Main HTML template
├── 📄 README.md          # Frontend documentation
├── 📄 .env              # Environment variables
├── 📄 test-package.json  # Testing dependencies
├── 📁 public/           # Static assets
│   ├── 🖼️ vite.svg      # Vite logo
│   └── 📁 fonts/        # Custom fonts
│       └── 🔤 LittleCaesar.ttf
├── 📁 src/              # Source code
│   ├── ⚛️ main.jsx      # React entry point
│   ├── ⚛️ App.jsx       # Main App component
│   ├── 📁 assets/       # Images and icons
│   │   └── 🖼️ react.svg
│   ├── 📁 utils/        # Utilities and styles
│   │   └── 🎨 globals.scss
│   ├── 📁 views/        # Page components
│   │   └── 📁 Home/     # Home page
│   │       ├── ⚛️ index.jsx
│   │       └── 🎨 styles.scss
│   └── 📁 test/         # Test files
│       ├── 🔧 setup.js
│       └── 🧪 Home.test.jsx
└── 📁 dist/             # Build output (generated)
```

### Frontend Architecture

#### React Components

1. **`App.jsx`** - Root Component
   - Application shell and routing
   - Global state management
   - Error boundaries
   - Theme and context providers

2. **`views/Home/index.jsx`** - Main Interface
   - Pathfinding form with validation
   - Real-time search functionality
   - Results visualization
   - Loading states and error handling

#### Styling and Assets

3. **`utils/globals.scss`** - Global Styles
   - CSS variables and themes
   - Responsive design utilities
   - Component base styles
   - Typography and spacing

4. **`public/`** - Static Assets
   - Favicon and app icons
   - Custom fonts (LittleCaesar.ttf)
   - Manifest files

## 🧪 Testing Structure

### Python Tests

```
test_simple.py              # Basic functionality tests
test_main.py                # Comprehensive test suite
├── TestProjectStructure    # File existence validation
├── TestPackageConfiguration # package.json validation
├── TestPythonFileStructure # Python module testing
├── TestJavaScriptFiles     # JS/React component testing
├── TestRequirements        # Dependency validation
└── TestBasicFunctionality  # Import and runtime tests
```

### Frontend Tests

```
client/src/test/
├── setup.js               # Test environment setup
└── Home.test.jsx         # React component tests
    ├── Component rendering
    ├── User interactions
    ├── API integration
    ├── Error handling
    └── Loading states
```

## 🐳 DevOps and Deployment

### GitHub Actions (`/.github/workflows/`)

```
ci.yml                     # Continuous Integration Pipeline
├── test-python           # Python backend testing
├── test-frontend         # React frontend testing
├── test-backend-api      # Node.js API testing
├── security-scan         # Security vulnerability scanning
├── integration-test      # End-to-end testing
└── build-and-validate    # Build verification
```

### Docker Configuration

```
docker-compose.yml         # Multi-service orchestration
bot/Dockerfile            # Backend container
client/Dockerfile         # Frontend container
Dockerfile.python         # Python worker container
```

### Configuration Files

```
bot/.env                  # Backend environment variables
.env                      # Python environment variables
.vscode/                  # VS Code IDE configuration
├── launch.json          # Debug configurations
└── settings.json        # Editor settings
```

## 🔧 Build and Development Tools

### Python Tools
- **Virtual Environment**: Isolated dependency management
- **pip**: Package installation and management
- **pytest**: Testing framework
- **flake8**: Code linting and style checking

### Node.js Tools
- **npm**: Package management and script running
- **Vite**: Fast build tool and dev server
- **ESLint**: JavaScript linting
- **Prettier**: Code formatting

### Development Scripts
- **`setup-dev.sh`**: Automated environment setup
- **`npm start`**: Development server startup
- **`npm run build`**: Production build
- **`npm test`**: Test suite execution

## 📊 Data Flow Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Client  │───▶│   Express API    │───▶│  Python Engine  │
│   (Frontend)    │    │   (Backend)      │    │  (Algorithms)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  User Interface │    │  REST Endpoints  │    │ Wikipedia API   │
│  Form Handling  │    │  Validation      │    │ GloVe Vectors   │
│  Results Display│    │  Error Handling  │    │ Search Algos    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🎯 Key Design Patterns

### Backend Patterns
- **Separation of Concerns**: Clear module boundaries
- **Error Handling**: Comprehensive try-catch blocks
- **Caching**: GloVe embeddings and API responses
- **Rate Limiting**: Wikipedia API throttling
- **Async Processing**: Concurrent link fetching

### Frontend Patterns
- **Component Composition**: Modular React components
- **State Management**: React hooks (useState, useEffect)
- **Error Boundaries**: Graceful error handling
- **Loading States**: User feedback during operations
- **Responsive Design**: Mobile-first approach

### Testing Patterns
- **Unit Testing**: Individual function testing
- **Integration Testing**: API endpoint testing
- **Component Testing**: React component behavior
- **Mocking**: External dependency simulation
- **Performance Testing**: Speed and memory benchmarks

## 🔐 Security Considerations

### Input Validation
- API request sanitization
- XSS prevention in React
- SQL injection prevention (if database used)

### Access Control
- CORS configuration
- Rate limiting
- Environment variable security

### Dependency Management
- Regular security audits
- Automated vulnerability scanning
- Version pinning for stability

## 📈 Performance Optimizations

### Backend Optimizations
- GloVe vector caching
- Concurrent API requests
- Memory management for large datasets
- Timeout handling for long searches

### Frontend Optimizations
- Code splitting with Vite
- Component memoization
- Lazy loading for large components
- Bundle size optimization

### Infrastructure Optimizations
- Container optimization
- CDN for static assets
- Gzip compression
- HTTP/2 support

This project structure demonstrates professional software development practices with clear separation of concerns, comprehensive testing, and production-ready deployment configurations.
