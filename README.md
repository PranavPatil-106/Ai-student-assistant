# AI-Powered Student Learning Assistant

An intelligent learning platform that helps students study more effectively using AI-generated content, interactive quizzes, and personalized learning tools.

## Features

- **AI-Powered Content Generation**: Automatically generates MCQs, flashcards, and summaries from study materials
- **Interactive Learning**: Engaging quiz interface with immediate feedback and reattempt options
- **Smart Q&A**: Ask questions about your study materials and get context-aware answers
- **Progress Tracking**: Monitor learning progress with detailed analytics and performance metrics
- **Multi-Format Support**: Upload and process PDF, DOCX, and TXT documents

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Database**: MySQL
- **AI/ML**: Hugging Face Transformers, LangChain, Sentence Transformers
- **Vector Database**: ChromaDB

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up MySQL database
4. Configure environment variables in `.env` file
5. Run the application: `python start_all.bat`

## Usage

1. Faculty users can upload study materials
2. Students can access AI-generated learning content
3. Track progress through the dashboard

## Project Structure

```
├── backend/
│   ├── api/              # API routes
│   ├── services/         # Business logic
│   ├── utils/            # Utility functions
│   └── storage/          # Document storage
├── frontend/
│   └── components/       # Streamlit components
└── storage/              # Subject materials
```

## Contributing

This project was developed as part of an academic project. Contributions are welcome!

## License

MIT License