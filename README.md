# AgriTwin

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-316192)
![License](https://img.shields.io/badge/License-MIT-green)
![Hackathon](https://img.shields.io/badge/AI%20in%20Agriculture-Hackathon-orange)

A multilingual AI-powered digital memory bank for precision farm management, designed to preserve the knowledge of experienced farmers and help future farmers make better decisions with the support of Artificial Intelligence.

## 🌾 Project Overview

AgriTwin is an AI in Agriculture hackathon project focused on solving a critical problem in farming communities: the loss of valuable field-specific knowledge when land ownership changes or farmers retire. Traditional land records such as Field Measurement Book (FMB) maps often do not reflect the real physical condition of farms because farmers continuously modify field boundaries, irrigation channels, and land elevations over time.

In many cases, this knowledge disappears when it is needed most. AgriTwin addresses this by creating a digital memory bank of farm experience that can be recorded, stored, and reused later through voice, structured records, and AI-powered analysis.

### Why this matters

- Farmers often lose practical wisdom when land is sold or inherited.
- Generic agricultural apps provide broad advice, not plot-specific recommendations.
- Local farming knowledge is highly valuable but remains scattered and informal.
- Voice-based memory capture makes it easy for farmers to document experience in their native language.

---

## 🎯 Problem Statement

Official land records often fail to represent the real agricultural conditions of a field because:

- Field boundaries change over time.
- Irrigation channels are modified.
- Soil and elevation conditions evolve.
- Traditional experience is not preserved when ownership changes.

This creates a gap between the physical field and the information available for decision making.

---

## 💡 Solution

AgriTwin is designed as a multilingual digital memory bank that stores a farmer’s practical experience as voice memories and uses that history to provide personalized recommendations.

The system combines:

- Farmer-entered field information
- Plot-specific area calculations
- Crop and fertilizer recommendations based on trusted agricultural guidance
- Voice-to-text processing using Whisper
- Retrieval of historical farm memories for AI-based advice

---

## 🧩 Core Modules

### 1. Plot Area Module

Farmers can manually enter field dimensions or acreage. The backend calculates the actual plot area, which is later used for fertilizer and seed recommendations.

Future enhancement:
- Interactive mapping using Leaflet.js and OpenStreetMap
- Manual boundary drawing on a map

### 2. Fertilizer Recommendation Module

Recommendations are generated using trusted TNAU (Tamil Nadu Agricultural University) guidelines rather than AI-generated assumptions.

Supported crops include:
- Paddy
- Groundnut
- Sugarcane
- Maize

### 3. AI Farm Memory Module

Senior farmers can record farm experiences in their native language using voice. These recordings are converted to text, stored in PostgreSQL, and later retrieved to assist future decision-making.

---

## 🔄 End-to-End Project Workflow

Farmer Login
→ Register/Login
→ Add Farm Information
→ Enter Plot Area
→ Record Voice Memory
→ Whisper converts speech to text
→ Store text in PostgreSQL
→ Retrieve previous memories
→ Local LLM analyzes memories
→ AI generates personalized farming advice
→ Display results on the dashboard

### Workflow Diagram

```mermaid
flowchart TD
    A[Farmer Login] --> B[Register or Login]
    B --> C[Add Farm Information]
    C --> D[Enter Plot Area]
    D --> E[Record Voice Memory]
    E --> F[Whisper Speech-to-Text]
    F --> G[Store Text in PostgreSQL]
    G --> H[Retrieve Previous Memories]
    H --> I[Local LLM Analysis]
    I --> J[Personalized Farming Advice]
    J --> K[Dashboard Display]
```

---

## ✨ Features

### Implemented

- ✔ FastAPI backend setup
- ✔ PostgreSQL database connection
- ✔ SQLAlchemy ORM
- ✔ User Registration API
- ✔ User Login API
- ✔ Password hashing with bcrypt
- ✔ JWT authentication
- ✔ Whisper speech-to-text integration
- ✔ Voice recording workflow
- ✔ PostgreSQL schema design
- ✔ Swagger API documentation
- ✔ Postman API testing

### Under Development

- Farm Memory Storage
- Memory Retrieval APIs
- Plot Area Calculator
- Fertilizer Recommendation Engine
- Weather API Integration
- AI Chat Assistant
- Dashboard
- Interactive Farm Mapping
- Local LLM Integration
- Farmer Profile Management

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Frontend | HTML, CSS, JavaScript, Bootstrap (planned), Leaflet.js (future) |
| Backend | FastAPI, Python, SQLAlchemy, Pydantic, JWT Authentication, Passlib, Uvicorn |
| Database | PostgreSQL |
| AI | OpenAI Whisper (local speech-to-text), Local LLM (TinyLlama / Phi-3 Mini / Gemma 2B – planned) |
| Development Tools | VS Code, Git, GitHub, Postman, pgAdmin |

---

## 🏗️ Architecture Overview

```mermaid
flowchart LR
    A[Farmer App / Web UI] --> B[FastAPI Backend]
    B --> C[Authentication Layer]
    B --> D[Voice Processing Module]
    B --> E[Memory Storage Module]
    B --> F[Fertilizer Recommendation Module]
    C --> G[PostgreSQL Database]
    D --> H[Whisper STT]
    E --> G
    F --> G
    H --> E
```

---

## 📂 Project Structure

```text
AgriTwin/
├── Backend/
│   ├── app/
│   │   ├── router/
│   │   ├── utils/
│   │   ├── uploads/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   └── app.py
│   ├── requirements.txt
│   └── README.md
├── client/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
└── LICENSE
```

---

## 🔐 Authentication Flow

The authentication system provides secure access to protected APIs.

```mermaid
flowchart TD
    A[Register User] --> B[Hash Password]
    B --> C[Store User in Database]
    C --> D[Login Request]
    D --> E[Verify Password]
    E --> F[Generate JWT Token]
    F --> G[Access Protected APIs]
```

### Authentication Process

1. User registers with name, email, and password.
2. Password is hashed using bcrypt.
3. User data is stored in PostgreSQL.
4. During login, the password is verified.
5. A JWT is issued for authorized access.

---

## 🎤 Speech-to-Text Workflow

Farmers can record their experiences in their own language, and the backend converts the audio into text for storage.

```mermaid
flowchart LR
    A[Farmer Speaks] --> B[Audio Upload]
    B --> C[Whisper Speech-to-Text]
    C --> D[Extracted Text]
    D --> E[Store in PostgreSQL]
```

### Workflow Summary

- Audio is received through the backend API.
- Whisper processes the file locally.
- The recognized text is saved as a memory record.
- These memories become the basis for future AI advice.

---

## 🤖 AI Workflow

The AI component uses past farm memories to generate contextual advice rather than generic recommendations.

```mermaid
flowchart TD
    A[User Question] --> B[Retrieve Previous Memories]
    B --> C[Local LLM Processing]
    C --> D[Personalized Answer]
    D --> E[Dashboard / Chat Response]
```

### AI Workflow Summary

1. A farmer asks a question related to the farm.
2. Relevant historical memories are retrieved.
3. The local LLM analyzes them.
4. An answer is generated using the farmer’s prior knowledge as context.

---

## 🗄️ Database Workflow

The database layer connects the API layer with persistent farm and user records.

```mermaid
flowchart LR
    A[FastAPI App] --> B[SQLAlchemy ORM]
    B --> C[PostgreSQL Database]
    C --> D[Retrieve / Store Farm Data]
```

### Database Workflow Summary

- FastAPI receives requests.
- SQLAlchemy maps Python objects to database tables.
- PostgreSQL stores user records, farm records, and memories.
- Data can be retrieved for reporting, recommendations, and AI context.

---

## 🚀 Installation

Follow the steps below to run the backend locally.

### 1. Clone the repository

```bash
git clone https://github.com/your-username/AgriTwin.git
cd AgriTwin
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
cd Backend
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database and user, then set the connection string:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/agritwin
```

### 5. Run the backend

```bash
uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
```

### 6. Open API documentation

Once the server is running, visit:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## 📡 API Endpoints

### Available Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /register | Register a new user |
| POST | /login | Authenticate a user |
| GET | / | Health check |

### Planned Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /memory | Store a farm memory |
| GET | /memory | Retrieve farm memories |
| POST | /speech-to-text | Convert speech to text |
| POST | /farm | Save farm profile information |
| GET | /fertilizer | Get fertilizer recommendations |
| POST | /ask-ai | Ask the AI assistant a question |

---

## 🧪 Usage Guide

### User Journey

1. Register an account.
2. Log in securely.
3. Add farm details and plot area.
4. Record a voice memory describing a farming practice.
5. View the AI-assisted recommendation generated from past experiences.

### Example Flow

- Farmer enters plot size
- System computes the related area
- Voice memory is transcribed
- Previous memories are retrieved
- AI provides personalized guidance

---

## 🧭 Project Roadmap

### Short-Term Goals

- Complete farm memory storage APIs
- Build memory retrieval logic
- Develop plot area calculator
- Add fertilizer recommendation engine

### Mid-Term Goals

- Integrate weather APIs
- Build AI chat assistant
- Create dashboard UI
- Add local LLM support

### Long-Term Goals

- Interactive GIS mapping
- Satellite image analysis
- AI-based farm boundary detection
- Crop disease detection
- Yield prediction
- Mobile application
- Offline AI support
- Multilingual voice assistant
- Text-to-speech responses
- Smart notifications
- IoT integration
- Digital twin visualization

---

## 📸 Screenshots

> Screenshot placeholder – Add dashboard, voice upload, and recommendation screens here.

- Dashboard Overview
- Voice Memory Recording
- Fertilizer Recommendation Result
- AI Assistant Response

---

## 🤝 Contributing

Contributions are welcome.

### How to contribute

1. Fork the repository.
2. Create a new feature branch.
3. Commit your changes.
4. Open a pull request with a clear description.

Please make sure your changes are documented and tested where possible.

---

## 📜 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgements

We thank the following communities and technologies for supporting this project:

- Tamil Nadu Agricultural University (TNAU) for trusted agricultural recommendations
- OpenAI Whisper for local speech-to-text capabilities
- FastAPI and SQLAlchemy for rapid backend development
- The open-source AI and agriculture communities

---

## ✅ Conclusion

AgriTwin is a practical and forward-looking solution that combines farming knowledge, voice-based memory capture, and AI to create a personalized digital companion for farmers. By preserving field-specific knowledge and making it accessible over time, the project aims to support better cultivation decisions, improve farm productivity, and bridge the gap between traditional experience and modern technology.

This project represents a strong foundation for a national-level AI in Agriculture initiative and demonstrates how intelligent systems can be built to serve real-world farming communities.
