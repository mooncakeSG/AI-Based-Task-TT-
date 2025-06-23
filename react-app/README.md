# AI Task Assistant

A mobile-friendly React application built with Vite and Tailwind CSS for interacting with an AI backend.

## Features

- **Mobile-First Design**: Responsive layout that works seamlessly on all device sizes
- **Modern UI**: Clean, intuitive interface with Tailwind CSS styling
- **Chat Interface**: Interactive chat box for communicating with AI backend
- **Component-Based Architecture**: Well-organized, reusable React components
- **Touch-Friendly**: Optimized for mobile touch interactions

## Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **JavaScript** - ES6+ features

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser and navigate to the provided local URL (typically `http://localhost:5173`)

## Project Structure

```
src/
├── components/
│   ├── Header.jsx      # App header with branding
│   ├── Layout.jsx      # Main layout wrapper
│   └── ChatBox.jsx     # Interactive chat interface
├── App.jsx             # Main application component
├── main.jsx            # Application entry point
└── index.css           # Tailwind CSS imports
```

## Components

### Header
- Displays the app name and tagline
- Responsive design with gradient background
- Mobile-optimized typography

### Layout
- Provides consistent structure across the app
- Includes header, main content area, and footer
- Responsive padding and spacing

### ChatBox
- Interactive chat interface with message history
- Real-time message display with timestamps
- Mobile-friendly input field and send button
- Simulated AI responses (placeholder for backend integration)

## Mobile Responsiveness

The application is built with mobile-first approach:
- Responsive breakpoints (sm, md, lg)
- Touch-friendly button sizes
- Optimized text sizes for mobile screens
- Flexible layouts that adapt to screen size

## Backend Integration

The current implementation includes placeholder functionality for AI interactions. The chat interface is ready for backend integration with:
- Message state management
- API call structure
- Response handling

## Development

To add new features:
1. Create new components in `src/components/`
2. Import and use them in `App.jsx` or other components
3. Follow the existing responsive design patterns
4. Use Tailwind CSS classes for styling

## Build

To build for production:
```bash
npm run build
```

The built files will be in the `dist/` directory.

## License

This project is created as a template for AI-powered task management applications.
