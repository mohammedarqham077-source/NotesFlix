Build a modern Netflix-style EdTech platform called NotesFlix for Computer Science students.

The platform should allow students to login with separate accounts and manage their own study subjects and notes.

Main Features Required:

1. User Authentication (College Style Login)

- Students can Sign Up with Name, Email, Student ID and Password
- Login and Logout system
- Each student should have a separate dashboard
- Use Flask sessions for authentication

2. Home Page

- Netflix-style homepage with course rows
- Sections like:
  - Trending Subjects
  - Core CSE Subjects
  - AI & Future Tech
  - Beginner Friendly
- Each subject displayed as a card layout
- Card should show:
  - Subject Name
  - Rating
  - Difficulty Level
  - Professor Verified Badge
  - Add to My List button

3. Subjects Page

- Display all available subjects
- Each subject card opens a Notes page
- Include search functionality to find subjects

4. My List Page

- Students can add subjects to My List
- Shows saved subjects for that specific user
- Data stored in database linked to the logged-in user

5. Notes System

- Each subject should allow students to:
  - Add personal notes
  - View saved notes
  - Edit notes
  - Delete notes
- Notes stored in database

6. AI Study Assistant

- AI summarizer that generates key points from notes
- Button: "Generate AI Summary"

7. Study Modes
   Include study modes:

- Relax Mode
- Deep Learning Mode
- Exam Mode

Each mode changes UI color and reading layout.

8. UI / UX

- Netflix-style card layout
- Smooth hover animations
- Gradient cards
- Dark mode / Night mode toggle
- Responsive design for mobile and desktop

9. Backend
   Use:

- Flask (Python)
- SQLite database

Database Tables:

- users (id, name, email, student_id, password)
- subjects (id, title, rating, difficulty)
- user_list (user_id, subject_id)
- notes (id, user_id, subject_id, content)

10. Pages Required
    Create these pages:

- Home Page
- Login Page
- Signup Page
- Subjects Page
- My List Page
- Notes Page
- Dashboard Page

Provide:

- Full project folder structure
- Flask backend code
- HTML templates
- CSS styling for Netflix UI
- JavaScript for interactivity
- Database schema and logic.