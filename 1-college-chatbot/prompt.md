I want to build an AI-Powered College Enquiry Chatbot System as a learning project and would like to create it step by step from planning to deployment.
Project Overview
The application should act as a virtual college assistant that can answer student queries related to:
•	Admissions 
•	Courses and Programs 
•	Fee Structure 
•	Scholarships 
•	Campus Facilities 
•	Placements 
•	Hostel Information 
•	Important Dates 
•	General College Information 
The chatbot should use Natural Language Processing (NLP) and Generative AI to understand user questions and provide accurate, conversational responses.
________________________________________
Technical Requirements
Backend
•	Language: Python 3.x 
•	Framework: Flask 
•	Database: SQLite 
•	ORM: SQLAlchemy 
•	Authentication: Flask-Login or JWT-based authentication 
•	API Design: RESTful APIs 
Frontend
•	HTML5 
•	CSS3 
•	Bootstrap 5 
•	JavaScript 
•	Jinja2 Templates 
AI & NLP
Use free or open-source solutions whenever possible:
•	OpenAI-compatible free models 
•	Hugging Face Inference API 
•	Sentence Transformers 
•	LangChain 
•	ChromaDB or FAISS for vector search 
•	NLTK or spaCy for NLP processing 
Database
SQLite tables should include:
•	Users 
•	Student Queries 
•	Chat History 
•	Knowledge Base 
•	FAQ Categories 
•	System Logs 
________________________________________
Functional Requirements
User Module
•	User Registration 
•	User Login 
•	Password Reset 
•	User Profile Management 
•	Chat History Viewing 
Admin Module
•	Admin Login 
•	Manage FAQs 
•	Manage Knowledge Base 
•	View User Queries 
•	Analytics Dashboard 
•	Manage Users 
Chatbot Module
•	Natural language query processing 
•	Context-aware conversations 
•	FAQ matching 
•	AI-generated responses 
•	Query logging 
•	Conversation history 
•	Feedback collection 
________________________________________
Architecture Requirements
Design the application using a clean and scalable architecture:
college-chatbot/
│
├── app/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── repositories/
│   ├── templates/
│   ├── static/
│   ├── auth/
│   ├── chatbot/
│   ├── utils/
│   └── config/
│
├── database/
├── tests/
├── docs/
├── requirements.txt
├── run.py
└── README.md
Follow:
•	MVC pattern 
•	Service Layer pattern 
•	Repository pattern 
•	Dependency Injection where applicable 
•	Environment-based configuration 
________________________________________
Non-Functional Requirements
•	Secure authentication 
•	Password hashing using bcrypt 
•	Input validation 
•	Error handling 
•	Logging 
•	Rate limiting 
•	Responsive UI 
•	Scalable code structure 
•	Unit testing 
•	API documentation 
________________________________________
AI Chatbot Features
Implement the chatbot in multiple phases:
Phase 1
•	Rule-based FAQ chatbot 
•	Keyword matching 
•	Basic responses 
Phase 2
•	NLP-based intent recognition 
•	Entity extraction 
•	Improved response generation 
Phase 3
•	Retrieval-Augmented Generation (RAG) 
•	Vector database integration 
•	Semantic search 
Phase 4
•	Integration with free LLM APIs 
•	Context-aware conversations 
•	Advanced AI responses 
________________________________________
Learning-Oriented Development
For each step, provide:
1.	Objective 
2.	Architecture explanation 
3.	Folder structure 
4.	Database design 
5.	Code implementation 
6.	File-by-file explanation 
7.	Best practices 
8.	Common mistakes 
9.	Testing approach 
10.	Next steps 
Do not generate the entire application at once.
Start with:
•	Requirement analysis 
•	System architecture 
•	Technology stack justification 
•	Project folder structure 
•	Database schema design 
Then proceed to implementation one module at a time, ensuring every step is fully explained for learning purposes.
Extra requirement:
1.	User the following folder as project folder, ai_projects_30\1_college_chatbot
2.	Use minimum token for this application
