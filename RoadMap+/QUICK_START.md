# ⚡ ASURA QUICK START GUIDE

## 🚀 Immediate Next Steps (Week 1)

### Day 1-2: Backend Foundation

#### 1. Create Project Structure
```bash
cd c:\Users\parth\OneDrive\Desktop\Asura

# Create backend structure
mkdir backend
cd backend

python -m venv venv
.\venv\Scripts\activate

mkdir app
cd app
mkdir api core models schemas services utils
cd ..

mkdir tests
```

#### 2. Install Core Dependencies
```bash
pip install fastapi uvicorn[standard] sqlalchemy alembic pydantic python-dotenv pytest pytest-asyncio
```

#### 3. Create `backend/requirements.txt`
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
```

#### 4. Create Basic FastAPI App (`backend/app/main.py`)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Asura API",
    description="AI SecureLab - Security & Mutation Testing Tool",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Asura API is running", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

#### 5. Test Backend
```bash
cd backend
uvicorn app.main:app --reload
# Visit http://localhost:8000/docs
```

---

### Day 3-4: Frontend Foundation

#### 1. Create React Project
```bash
cd c:\Users\parth\OneDrive\Desktop\Asura
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

#### 2. Install Dependencies
```bash
npm install axios zustand react-router-dom lucide-react
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

#### 3. Configure TailwindCSS (`frontend/tailwind.config.js`)
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

#### 4. Update `frontend/src/index.css`
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

#### 5. Create Basic Layout (`frontend/src/App.jsx`)
```jsx
import { useState } from 'react'
import { Shield, Activity, FileSearch, Settings } from 'lucide-react'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-4 shadow-lg">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield size={32} />
            <h1 className="text-2xl font-bold">ASURA</h1>
          </div>
          <span className="text-sm opacity-90">AI SecureLab v0.1</span>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto p-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-3xl font-bold mb-2">Welcome to Asura</h2>
          <p className="text-gray-600">Your local security & mutation testing companion</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="p-6 border-2 border-purple-200 rounded-lg hover:border-purple-400 transition cursor-pointer">
              <Activity className="text-purple-600 mb-2" size={32} />
              <h3 className="font-bold text-lg">Security Scan</h3>
              <p className="text-sm text-gray-600">Find vulnerabilities in your code</p>
            </div>
            
            <div className="p-6 border-2 border-indigo-200 rounded-lg hover:border-indigo-400 transition cursor-pointer">
              <FileSearch className="text-indigo-600 mb-2" size={32} />
              <h3 className="font-bold text-lg">Mutation Testing</h3>
              <p className="text-sm text-gray-600">Test your test suite strength</p>
            </div>
            
            <div className="p-6 border-2 border-blue-200 rounded-lg hover:border-blue-400 transition cursor-pointer">
              <Settings className="text-blue-600 mb-2" size={32} />
              <h3 className="font-bold text-lg">Configuration</h3>
              <p className="text-sm text-gray-600">Set up your projects</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
```

#### 6. Test Frontend
```bash
cd frontend
npm run dev
# Visit http://localhost:5173
```

---

### Day 5: Database Setup

#### 1. Install Alembic
```bash
cd backend
pip install alembic
alembic init alembic
```

#### 2. Create Database Models (`backend/app/models/models.py`)
```python
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class SeverityEnum(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    scans = relationship("Scan", back_populates="project")

class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    scan_type = Column(String)  # "security" or "mutation"
    status = Column(String)  # "running", "completed", "failed"
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    project = relationship("Project", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan")

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    tool = Column(String)  # "bandit", "safety", "semgrep"
    severity = Column(Enum(SeverityEnum))
    file_path = Column(String)
    line_number = Column(Integer)
    vulnerability_type = Column(String)
    description = Column(Text)
    code_snippet = Column(Text, nullable=True)
    cwe_id = Column(String, nullable=True)
    
    scan = relationship("Scan", back_populates="vulnerabilities")
```

#### 3. Configure Database (`backend/app/core/database.py`)
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./asura.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
```

#### 4. Update `main.py` to Initialize DB
```python
from app.core.database import init_db

@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Database initialized")
```

---

### Day 6-7: First API Endpoint

#### 1. Create Project Schema (`backend/app/schemas/project.py`)
```python
from pydantic import BaseModel
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    path: str

class ProjectResponse(BaseModel):
    id: int
    name: str
    path: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

#### 2. Create Project Service (`backend/app/services/project_service.py`)
```python
from sqlalchemy.orm import Session
from app.models.models import Project
from app.schemas.project import ProjectCreate

class ProjectService:
    @staticmethod
    def create_project(db: Session, project: ProjectCreate):
        db_project = Project(name=project.name, path=project.path)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def get_projects(db: Session):
        return db.query(Project).all()
    
    @staticmethod
    def get_project(db: Session, project_id: int):
        return db.query(Project).filter(Project.id == project_id).first()
```

#### 3. Create API Router (`backend/app/api/projects.py`)
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    return ProjectService.create_project(db, project)

@router.get("/", response_model=list[ProjectResponse])
async def list_projects(db: Session = Depends(get_db)):
    return ProjectService.get_projects(db)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    project = ProjectService.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
```

#### 4. Register Router in `main.py`
```python
from app.api import projects

app.include_router(projects.router)
```

---

## 📋 Week 1 Checklist

- [ ] Backend FastAPI server running on :8000
- [ ] Frontend React app running on :5173
- [ ] SQLite database created with tables
- [ ] `/api/projects` endpoint working
- [ ] Frontend can create and list projects
- [ ] Tests written for project API
- [ ] Git repository initialized
- [ ] README.md with setup instructions

---

## 🧪 Testing Your Setup

### Backend Test
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### Create Project
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "test-project", "path": "/path/to/project"}'
```

---

## 🎯 Week 2 Preview

Next week you'll:
1. Install Bandit, Safety, Semgrep
2. Create scanner wrapper module
3. Implement `/api/scan/security` endpoint
4. Parse and store vulnerability results
5. Display results in frontend

---

## 📚 Essential Reading

Before coding:
- [ ] Read FastAPI tutorial (https://fastapi.tiangolo.com/tutorial/)
- [ ] Skim Bandit docs (understand output format)
- [ ] Review Semgrep rules (https://semgrep.dev/explore)

---

## 🆘 Troubleshooting

### Backend won't start
- Check if port 8000 is free: `netstat -ano | findstr :8000`
- Ensure venv is activated: `.\venv\Scripts\activate`

### Frontend build errors
- Delete `node_modules` and run `npm install` again
- Check Node.js version: `node --version` (need v18+)

### Database errors
- Delete `asura.db` and restart server to recreate

---

## 💡 Pro Tips

1. **Use VS Code extensions:**
   - Python extension
   - ESLint
   - Tailwind CSS IntelliSense

2. **Git workflow:**
   ```bash
   git init
   git add .
   git commit -m "feat: initial project setup"
   ```

3. **Keep both servers running:**
   - Terminal 1: `cd backend && uvicorn app.main:app --reload`
   - Terminal 2: `cd frontend && npm run dev`

---

**Ready to build Asura? Let's go! 🔥**

Questions? Check ROADMAP.md for full details.
