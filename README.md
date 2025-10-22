# Resume Automation API

A FastAPI-based resume processing system that uses LangGraph and LangChain to automatically extract skills from job descriptions and resumes, then compute fit scores between them.

## 🚀 Features

- **Job Description Processing**: Upload or create job descriptions with automatic skill extraction
- **Resume Processing**: Upload resume files (.docx) with automatic skill extraction and fit scoring
- **LangGraph Workflows**: Uses LangChain + OpenAI for intelligent skill extraction
- **Fit Score Calculation**: Jaccard similarity-based scoring between job and resume skills
- **RESTful API**: Clean FastAPI endpoints with automatic Swagger documentation
- **PostgreSQL Database**: Persistent storage with proper relationships
- **Error Handling**: Robust error handling with fallback mechanisms
- **File Management**: Secure file upload and storage with timestamped naming

## 🏗️ Architecture

```
app/
├── api/                    # API route handlers
│   ├── job_routes.py      # Job-related endpoints
│   └── resume_routes.py   # Resume-related endpoints
├── db/                    # Database configuration
│   └── database.py        # SQLAlchemy setup
├── graph/                 # LangGraph workflows
│   └── skill_graph.py     # Skill extraction and matching graphs
├── models/                # Data models
│   ├── entities.py        # SQLAlchemy models
│   └── schemas.py         # Pydantic schemas
├── services/              # Business logic
│   ├── job_service.py     # Job processing logic
│   └── resume_service.py  # Resume processing logic
├── utils/                 # Utility functions
│   └── docx_reader.py     # DOCX file processing
└── main.py               # FastAPI application entry point
```

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- OpenAI API key

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd resumeAutomation
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Configure database**
   Update `app/db/database.py` with your PostgreSQL credentials:
   ```python
   username = "your_username"
   password = "your_password"
   host = "localhost"
   port = "5432"
   database = "your_database_name"
   ```

6. **Initialize database**
   ```bash
   python -m app.init_db
   ```

## 🚀 Usage

### Start the server
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
Swagger documentation: `http://localhost:8000/docs`

### API Endpoints

#### Job Management
- `POST /jobs/create` - Create a job from title and description
- `POST /jobs/upload` - Upload a job description file (.docx)
- `GET /jobs/` - List all jobs
- `GET /jobs/{job_id}` - Get specific job details
- `DELETE /jobs/{job_id}` - Delete a job

#### Resume Management
- `POST /resumes/upload` - Upload a resume file (.docx) for a specific job
- `GET /resumes/jobs/{job_id}` - Get all resumes for a job (sorted by fit score)
- `GET /resumes/top?job_id={id}&limit={n}` - Get top N resumes for a job
- `GET /resumes/{resume_id}` - Get specific resume details

### Example Usage

#### 1. Create a Job
```bash
curl -X POST "http://localhost:8000/jobs/create" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "description": "We are looking for a Senior Python Developer with experience in FastAPI, PostgreSQL, and machine learning."
  }'
```

#### 2. Upload a Resume
```bash
curl -X POST "http://localhost:8000/resumes/upload" \
  -F "job_id=1" \
  -F "file=@resume.docx"
```

#### 3. Get Top Resumes
```bash
curl -X GET "http://localhost:8000/resumes/top?job_id=1&limit=5"
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for skill extraction using OpenAI's GPT models

### Database Schema
- **job_descriptions**: Stores job information and extracted skills
- **resumes**: Stores resume information, extracted skills, and fit scores

### File Storage
- Job files: `uploads/jobs/`
- Resume files: `uploads/resumes/`
- Files are timestamped for uniqueness

## 🧠 LangGraph Workflows

### Job Skill Extraction
1. Takes job description text
2. Uses OpenAI to extract key skills
3. Returns structured skill list

### Resume Evaluation
1. Extracts skills from resume text
2. Compares against job skills using Jaccard similarity
3. Calculates fit score (0.0 to 1.0)
4. Returns resume skills and fit score

### Fallback Mechanisms
- If OpenAI API fails, uses keyword-based skill extraction
- Comprehensive skill keyword database for fallback matching
- Graceful error handling throughout the pipeline

## 📊 Fit Score Calculation

The fit score is calculated using Jaccard similarity:
```
fit_score = |job_skills ∩ resume_skills| / |job_skills ∪ resume_skills|
```

- **1.0**: Perfect match (all job skills found in resume)
- **0.5**: Moderate match (half of job skills found)
- **0.0**: No match (no common skills)

## 🛡️ Error Handling

- **File Validation**: Only .docx files accepted
- **Database Errors**: Proper rollback and cleanup
- **API Failures**: Fallback to keyword-based extraction
- **File Operations**: Atomic operations with cleanup on failure
- **HTTP Exceptions**: Proper status codes and error messages

## 📝 Logging

Comprehensive logging throughout the application:
- File upload operations
- LangGraph workflow execution
- Skill extraction results
- Fit score calculations
- Error conditions

## 🔮 Future Enhancements

- **Semantic Matching**: Replace Jaccard similarity with embedding-based similarity
- **Caching**: Implement caching for frequent resume-job matches
- **RBAC**: Add role-based access control (HR vs. applicant)
- **Chat Interface**: Integrate conversational resume review
- **Batch Processing**: Support bulk resume uploads
- **Advanced Analytics**: Detailed matching analytics and insights

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the Swagger documentation at `/docs`
2. Review the logs for error details
3. Ensure all environment variables are set correctly
4. Verify database connectivity and schema

---

**Built with ❤️ using FastAPI, LangGraph, LangChain, and OpenAI**
