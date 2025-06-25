# 🚀 AI-Powered Multi-Modal Assistant - End-to-End AI Solution

## Capstone Project - Tech Titanians

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/mooncakeSG/AI-Based-Task-TT-)
[![License](https://img.shields.io/badge/license-Academic%20Use-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/react-19.0+-blue.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104+-green.svg)](https://fastapi.tiangolo.com)

> **An end-to-end AI application designed to process and analyze text, image, and audio inputs. Integrates multiple open-source and free-tier AI technologies to demonstrate a cohesive, scalable, and accessible solution for real-world use cases such as academic assistance, accessibility support, and content analysis.**

## 📋 **Project Overview**

This project is an end-to-end AI application designed to process and analyze text, image, and audio inputs. It integrates multiple open-source and free-tier AI technologies to demonstrate a cohesive, scalable, and accessible solution for real-world use cases such as academic assistance, accessibility support, and content analysis.

## ✨ **Features**

- ✅ **Multi-Modal Input Processing**: Accepts text, image, and audio inputs from users
- 🧠 **Advanced Text Processing**: Processes text with Groq API using Meta's LLaMA 3 model
- 👁️ **Intelligent Image Analysis**: Analyzes images using Hugging Face's Donut or BLIP model
- 🎤 **Speech-to-Text Conversion**: Converts speech to text using Hugging Face's Whisper
- 🔐 **Secure Data Handling**: JWT-based authentication for secure user sessions
- 💾 **Persistent Storage**: Reliable data storage using Supabase PostgreSQL
- 🛡️ **Robust Error Handling**: Comprehensive error handling and performance logging
- 📊 **Real-time Monitoring**: Performance tracking and system health monitoring

## 🛠️ **Technologies Used**

### **Frontend**
- **ReactJS** - Modern web application framework
- **HTML5 & CSS3** - Structure and styling
- **Framer Motion** - Smooth animations and transitions
- **Tailwind CSS** - Utility-first CSS framework

### **Backend**
- **FastAPI (Python)** - High-performance web framework
- **Uvicorn** - ASGI server for production deployment

### **AI & Machine Learning**
- **Language AI**: Groq API (LLaMA 3) - Advanced natural language processing
- **Vision AI**: Hugging Face Donut/BLIP - Image analysis and understanding
- **Speech-to-Text**: Hugging Face Whisper - High-accuracy audio transcription

### **Database & Storage**
- **Supabase (PostgreSQL)** - Managed database with real-time capabilities
- **JWT Authentication** - Secure token-based authentication

### **Monitoring & Logging**
- **Loguru** - Advanced Python logging
- **Custom Monitoring** - API performance and health tracking
- **Prometheus & Grafana** (Optional) - Advanced metrics and visualization
- **Sentry** (Optional) - Error tracking and monitoring
- **MLflow** (Optional) - Machine learning model tracking

## 🏗️ **System Architecture**

The frontend communicates with the FastAPI backend, which handles authentication and routes requests to appropriate AI APIs. All responses are stored in Supabase and returned to the frontend for a seamless user experience.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Services   │
│   (ReactJS)     │◄──►│   (FastAPI)     │◄──►│   - Groq LLaMA  │
│                 │    │                 │    │   - HF Whisper  │
│   - User Input  │    │   - Auth (JWT)  │    │   - HF BLIP     │
│   - File Upload │    │   - Routing     │    │                 │
│   - Results     │    │   - Processing  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (Supabase)    │
                       │                 │
                       │   - User Data   │
                       │   - File Store  │
                       │   - Responses   │
                       └─────────────────┘
```

## 🚀 **Setup Instructions**

### **Prerequisites**
- **Python 3.9+** - Backend development
- **Git** - Version control
- **API keys** for Groq and Hugging Face
- **Supabase project** setup

### **Installation Steps**

#### 1. Clone the repository:
```bash
git clone https://github.com/mooncakeSG/AI-Based-Task-TT-.git
cd AI-Based-Task-TT-
```

#### 2. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate        # Linux/Mac
# OR
venv\Scripts\activate          # Windows
```

#### 3. Install dependencies:
```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../react-app
npm install
```

#### 4. Create a .env file and add your credentials:
```bash
# backend/.env
GROQ_API_KEY=your_groq_api_key_here
HF_API_KEY=your_huggingface_api_key_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Optional: Database URL if using direct PostgreSQL
DATABASE_URL=postgresql://user:password@host:port/database
```

#### 5. Set up your Supabase tables based on the provided schema:
```sql
-- See SUPABASE_SETUP.md for complete database schema
-- Tables: tasks, chat_messages, uploaded_files
```

#### 6. Run the backend:
```bash
cd backend
uvicorn main:app --reload
```

#### 7. Run the frontend:
```bash
cd react-app
npm run dev
```

#### 8. Open your browser and navigate to:
```
Frontend: http://localhost:5173
Backend API: http://localhost:8000
API Documentation: http://localhost:8000/docs
```

## 🧪 **Testing Strategy**

The system has been comprehensively tested using various input scenarios to ensure reliability and robustness:

### **Test Scenarios Covered:**
- ✅ **Valid and Invalid Inputs**: Text, image, and audio input validation
- ✅ **JWT-Secured Routes**: Authentication and authorization testing
- ✅ **API Timeout Handling**: Graceful handling of AI service timeouts
- ✅ **Data Persistence Verification**: Database operations and data integrity
- ✅ **UI Feedback Systems**: Loading states and error message display
- ✅ **File Upload Validation**: Size limits, format verification, malicious file detection
- ✅ **Cross-browser Compatibility**: Testing across modern web browsers

### **Running Tests:**
```bash
# Backend tests
cd backend
pytest tests/ -v --cov=. --cov-report=html

# Frontend tests (if available)
cd react-app
npm test
```

## 📊 **Monitoring and Logging**

### **Real-time Monitoring:**
- **API Usage Tracking**: Monitor request/response patterns and usage statistics
- **Performance Metrics**: Track response times, error rates, and system performance
- **Resource Utilization**: Monitor CPU, memory, and network usage

### **Logging Infrastructure:**
- **Loguru Integration**: Advanced Python logging with structured output
- **Error Tracking**: Comprehensive error logging and debugging information
- **Request Tracing**: Track requests through the entire system pipeline

### **Optional Advanced Monitoring:**
- **Prometheus & Grafana**: Advanced metrics collection and visualization dashboards
- **Sentry Integration**: Real-time error tracking and performance monitoring
- **MLflow Tracking**: Machine learning model performance and experiment tracking

### **Health Check Endpoints:**
```bash
# System health
GET /ping

# AI services health
GET /api/v1/ai/health

# Database health
GET /api/v1/database/health
```

## 🔮 **Future Roadmap**

### **Phase 1: Enhanced User Experience**
- ✨ **Enhanced User Interface**: Improved accessibility features and responsive design
- 👤 **Role-based User Profiles**: User-specific preferences and history tracking
- 📱 **Mobile Application**: Native iOS and Android applications
- 🌍 **Multi-language Support**: Support for multiple languages and localization

### **Phase 2: Advanced Features**
- 📊 **Advanced Analytics**: Detailed usage analytics and insights dashboards
- 🔧 **Custom Model Fine-tuning**: Domain-specific model training and optimization
- 🤖 **Advanced AI Workflows**: Complex multi-step AI processing pipelines
- 🔗 **Third-party Integrations**: API integrations with popular productivity tools

### **Phase 3: Enterprise & Scale**
- ☁️ **Cloud-Native Architecture**: Microservices and containerized deployments
- 🔄 **CI/CD Pipeline**: Automated testing, building, and deployment
- 📈 **Scalability Improvements**: Load balancing and horizontal scaling
- 🛡️ **Enterprise Security**: Advanced security features and compliance

## 🚀 **Deployment Options**

### **Quick Cloud Deployment (Recommended)**
- **Backend**: Deploy to Render using the included `render.yaml`
- **Frontend**: Deploy to Vercel using the included `vercel.json`
- **Database**: PostgreSQL on Render (free tier available)

### **Manual Deployment**
- **Docker**: Containerized deployment with Docker Compose
- **Traditional Server**: Manual server setup and configuration
- **Cloud Providers**: AWS, Google Cloud, Azure deployment guides

📖 **See `DEPLOYMENT_GUIDE.md` for detailed deployment instructions**

## 📄 **License**

This project is developed for **academic use** under the **CAPACITI IT Support Capstone Project**.

### **Academic License Terms:**
- ✅ Educational and research purposes
- ✅ Non-commercial academic use
- ✅ Open source contribution and learning
- ❌ Commercial redistribution without permission

---

## 👥 **Team - Tech Titanians**

This capstone project represents the culmination of our learning journey in AI development and demonstrates practical application of cutting-edge technologies in a real-world scenario.

### **Project Contributors:**
- **Project Type**: End-to-End AI Solution Capstone Project
- **Institution**: CAPACITI IT Support Program
- **Team**: Tech Titanians
- **Focus**: Multi-modal AI application development

---

## 📞 **Support & Contact**

For questions, issues, or contributions:

- **📧 Issues**: Create an issue on GitHub
- **💬 Discussions**: Use GitHub Discussions for questions
- **📖 Documentation**: Check our comprehensive guides in `/docs`
- **🚀 Deployment**: Follow `DEPLOYMENT_GUIDE.md`

---

**⭐ If you find this project helpful, please consider giving it a star on GitHub!** 