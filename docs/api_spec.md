# EduLeap API Specification

## Authentication
### POST /api/auth/guest
Request: `{ "name": "Student Name" }`
Response: `{ "access_token": "...", "student_id": 1, "name": "..." }`

## Tutoring
### POST /api/tutoring/start
Request: `{ "student_id": 1, "topic": "fraction addition", "name": "..." }`
Response: `{ "type": "diagnostic", "content": "...", "options": [...], "progress": {...} }`

### POST /api/tutoring/answer
Request: `{ "session_id": 1, "answer": "A) 1/2" }`
Response: `{ "type": "explanation|question", "content": "...", "progress": {...} }`

### GET /api/tutoring/session/{id}/history
Response: `{ "interactions": [...] }`

## Student
### GET /api/students/{id}
Response: `{ "id", "name", "current_level", "gaps": [...] }`

### GET /api/students/{id}/gaps
Response: `{ "gaps": [...] }`

## Analytics
### GET /api/analytics/session/{id}
Response: `{ "total_interactions", "correct_answers", "accuracy" }`

### GET /api/analytics/student/{id}/progress
Response: `{ "current_level", "total_sessions", "topics_covered" }`