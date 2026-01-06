# CodeYogi Frontend

Modern, AI-powered GitHub repository management dashboard built with React, TypeScript, and Firebase.

## Features

- 🔐 **GitHub Authentication**: Secure login with GitHub OAuth
- 📊 **Repository Dashboard**: Visualize and manage your repositories
- 🤖 **AI Analysis**: Multiple AI-powered analysis tools:
  - Repository Structure Analysis
  - Code Quality Analysis
  - Workflow Optimization
  - SEO Optimization
  - README Generation
- 💬 **Interactive Chat**: AI assistant for repository management
- 📈 **Analytics**: Track repository metrics and optimizations
- 🎨 **Modern UI**: Beautiful, responsive design with Tailwind CSS

## Prerequisites

- Node.js 16.x or higher
- npm or yarn
- Firebase project set up
- CodeYogi Backend running (see backend README)

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd CodeYogi_Frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```
   
   Or with yarn:
   ```bash
   yarn install
   ```

3. **Set up environment variables**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   The `.env` file should contain:
   ```env
   # Firebase Configuration
   VITE_FIREBASE_API_KEY="your_firebase_api_key"
   VITE_FIREBASE_AUTH_DOMAIN="your_project.firebaseapp.com"
   VITE_FIREBASE_PROJECT_ID="your_project_id"
   VITE_FIREBASE_STORAGE_BUCKET="your_project.firebasestorage.app"
   VITE_FIREBASE_MESSAGING_SENDER_ID="your_sender_id"
   VITE_FIREBASE_APP_ID="your_app_id"
   VITE_FIREBASE_MEASUREMENT_ID="your_measurement_id"
   
   # API Configuration
   VITE_API_BASE_URL="http://localhost:8000"
   ```

   **Firebase Setup:**
   1. Go to [Firebase Console](https://console.firebase.google.com/)
   2. Create a new project or use existing one
   3. Enable Authentication > GitHub provider
   4. Copy your Firebase config values to `.env`

## Running the Application

### Development Mode
```bash
npm run dev
```

Or with yarn:
```bash
yarn dev
```

The application will be available at: `http://localhost:5173`

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## Project Structure

```
CodeYogi_Frontend/
├── src/
│   ├── components/        # React components
│   │   ├── Dashboard.tsx
│   │   ├── ProjectView.tsx
│   │   ├── ChatInterface.tsx
│   │   └── views/        # Analysis view components
│   ├── contexts/         # React context providers
│   │   ├── AuthContext.tsx
│   │   ├── ChatContext.tsx
│   │   └── ThemeContext.tsx
│   ├── services/         # API services
│   │   ├── githubService.ts
│   │   └── analyticsService.ts
│   ├── config/          # Configuration files
│   │   ├── firebase.ts
│   │   └── api.ts
│   ├── types/           # TypeScript type definitions
│   ├── hooks/           # Custom React hooks
│   ├── App.tsx          # Main application component
│   └── main.tsx         # Application entry point
├── public/              # Static assets
├── index.html          # HTML template
├── vite.config.ts      # Vite configuration
├── tailwind.config.js  # Tailwind CSS configuration
└── tsconfig.json       # TypeScript configuration
```

## Key Components

### Authentication
- GitHub OAuth integration via Firebase
- Automatic token management
- Repository access control

### Dashboard
- Repository overview
- Quick actions
- Recent activity

### Analysis Views
- **Structure Analysis**: Visualize repository structure
- **Code Analysis**: Deep code quality insights
- **Workflow Optimization**: GitHub Actions optimization
- **SEO Optimization**: Repository discoverability
- **README Generator**: AI-powered documentation

### Chat Interface
- Natural language interaction
- Context-aware responses
- Command execution

## Configuration

### API Configuration
Edit [src/config/api.ts](src/config/api.ts) to configure backend endpoints:

```typescript
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  ENDPOINTS: {
    ANALYZE_GITHUB_STRUCTURE: "/analyze-github-structure/",
    ANALYZE_GITHUB_CODE: "/analyze-github-code/",
    // ... other endpoints
  },
};
```

### Firebase Configuration
Firebase is configured in [src/config/firebase.ts](src/config/firebase.ts) using environment variables.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_FIREBASE_API_KEY` | Firebase API Key | Yes |
| `VITE_FIREBASE_AUTH_DOMAIN` | Firebase Auth Domain | Yes |
| `VITE_FIREBASE_PROJECT_ID` | Firebase Project ID | Yes |
| `VITE_FIREBASE_STORAGE_BUCKET` | Firebase Storage Bucket | Yes |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | Firebase Messaging Sender ID | Yes |
| `VITE_FIREBASE_APP_ID` | Firebase App ID | Yes |
| `VITE_FIREBASE_MEASUREMENT_ID` | Firebase Measurement ID | No |
| `VITE_API_BASE_URL` | Backend API URL | Yes |

## Troubleshooting

### Common Issues

1. **Firebase Authentication Error**
   - Verify Firebase configuration in `.env`
   - Ensure GitHub OAuth is enabled in Firebase Console
   - Check Firebase project settings

2. **API Connection Error**
   - Ensure backend is running on `http://localhost:8000`
   - Check CORS settings in backend
   - Verify `VITE_API_BASE_URL` in `.env`

3. **Build Errors**
   - Clear node_modules: `rm -rf node_modules package-lock.json`
   - Reinstall dependencies: `npm install`
   - Clear Vite cache: `rm -rf .vite`

4. **GitHub Authentication Not Working**
   - Add authorized redirect URI in GitHub OAuth app settings:
     - Development: `http://localhost:5173`
     - Production: Your deployed URL
   - Verify GitHub OAuth app credentials in Firebase

## Deployment

### Vercel (Recommended)
1. Push code to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Other Platforms
The app is built with Vite and can be deployed to:
- Netlify
- Firebase Hosting
- AWS S3 + CloudFront
- Any static hosting service

Build command: `npm run build`
Output directory: `dist`

## Technologies Used

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Firebase** - Authentication & Database
- **Framer Motion** - Animations
- **Lucide React** - Icons
- **Mermaid** - Diagrams
- **Recharts** - Charts
- **Axios** - HTTP client

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
