import os

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, User, Subject, Note, UserList

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'notesflix_secret_key_123')

# Connect to Render's Permanent PostgreSQL Database, or fallback to local SQLite
db_url = os.environ.get('DATABASE_URL')
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'notesflix.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# --- Helper Functions ---
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        student_id = request.form.get('student_id')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('signup'))

        new_user = User(name=name, email=email, student_id=student_id)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect(url_for('home'))
        else:
            flash('Invalid login credentials!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    categories = {
        "Trending Subjects": Subject.query.filter_by(category="Trending").all(),
        "Core CSE Subjects": Subject.query.filter_by(category="Core CSE").all(),
        "AI & Future Tech": Subject.query.filter_by(category="AI").all(),
        "Beginner Friendly": Subject.query.filter_by(category="Beginner").all()
    }
    user = User.query.get(session['user_id'])
    my_list_ids = [s.id for s in user.my_list]
    return render_template('index.html', categories=categories, my_list_ids=my_list_ids)

@app.route('/subjects', methods=['GET'])
@login_required
def subjects():
    query = request.args.get('q', '')
    if query:
        all_subjects = Subject.query.filter(Subject.title.contains(query)).all()
    else:
        all_subjects = Subject.query.all()
    user = User.query.get(session['user_id'])
    my_list_ids = [s.id for s in user.my_list]
    return render_template('subjects.html', subjects=all_subjects, query=query, my_list_ids=my_list_ids)

@app.route('/my-list')
@login_required
def my_list():
    user = User.query.get(session['user_id'])
    return render_template('my_list.html', subjects=user.my_list)

@app.route('/add-to-list/<int:subject_id>')
@login_required
def add_to_list(subject_id):
    user = User.query.get(session['user_id'])
    subject = Subject.query.get_or_404(subject_id)
    if subject not in user.my_list:
        user.my_list.append(subject)
        db.session.commit()
    return redirect(request.referrer or url_for('home'))

@app.route('/remove-from-list/<int:subject_id>')
@login_required
def remove_from_list(subject_id):
    user = User.query.get(session['user_id'])
    subject = Subject.query.get_or_404(subject_id)
    if subject in user.my_list:
        user.my_list.remove(subject)
        db.session.commit()
    return redirect(request.referrer or url_for('my_list'))

@app.route('/notes/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def notes(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    user_id = session['user_id']
    note = Note.query.filter_by(user_id=user_id, subject_id=subject_id).first()

    if request.method == 'POST':
        content = request.form.get('content')
        if note:
            note.content = content
        else:
            new_note = Note(user_id=user_id, subject_id=subject_id, content=content)
            db.session.add(new_note)
        db.session.commit()
        flash('Note saved successfully!', 'success')
        return redirect(url_for('notes', subject_id=subject_id))

    return render_template('notes.html', subject=subject, note=note)

@app.route('/delete-note/<int:subject_id>')
@login_required
def delete_note(subject_id):
    user_id = session['user_id']
    note = Note.query.filter_by(user_id=user_id, subject_id=subject_id).first()
    if note:
        db.session.delete(note)
        db.session.commit()
        flash('Note deleted.', 'info')
    return redirect(url_for('notes', subject_id=subject_id))

@app.route('/generate-ai-summary', methods=['POST'])
@login_required
def ai_summary():
    content = request.json.get('content', '')
    subject = request.json.get('subject', 'this subject')
    
    if not content.strip():
        # Fallback detailed summary when no notes exist
        summary = (
            f"🤖 AI OVERVIEW: {subject}\n\n"
            f"📚 Core Fundamentals:\n"
            f"• Master the theoretical foundations and underlying logic of the topic.\n"
            f"• Understand the primary algorithms, frameworks, or methodologies used.\n\n"
            f"⚙️ Practical Applications:\n"
            f"• Focus on real-world implementation in modern tech stacks.\n"
            f"• Review industry best practices and potential pitfalls.\n\n"
            f"🎯 Typical Exam Strategy:\n"
            f"• Prepare for analytical problem-solving and edge-case scenarios.\n"
            f"• Memorize key definitions and performance trade-offs.\n\n"
            f"💡 Tip: Add your own study notes in the editor above. I will analyze your specific text, "
            f"calculate read-times, extract keywords, and build a custom study guide!"
        )
        return jsonify({'summary': summary})
    
    # Mock sophisticated analysis of user's actual notes
    sentences = [s.strip() for s in content.split('.') if s.strip() and len(s) > 5]
    words = content.split()
    word_count = len(words)
    read_time = max(1, word_count // 200) # Assuming ~200 WPM read speed
    
    # Simulate keyword extraction (grab unique long words)
    long_words = [w for w in words if len(w) > 7]
    keywords = list(set([w.lower().strip(""",.()'\"""") for w in long_words]))[:5]
    keyword_str = ", ".join(keywords).title()
    
    # Build the elaborate summary
    summary = f"✨ AI ANALYSIS OF YOUR NOTES\n"
    summary += f"📊 Stats: {word_count} words | ⏱️ Est. Review Time: {read_time} min\n"
    
    if keywords:
        summary += f"🔑 Key Concepts Detected: {keyword_str}\n\n"
    else:
        summary += "\n"
        
    summary += "📝 EXTRACTED STUDY POINTS:\n"
    
    if sentences:
        # Take up to 4 sentences and format them as a study list
        for i, sentence in enumerate(sentences[:4], 1):
            # Capitalize first letter if needed
            sentence = sentence[0].upper() + sentence[1:]
            summary += f"{i}. {sentence}.\n"
            
        if len(sentences) > 4:
            summary += f"\n...and {len(sentences) - 4} more concepts analyzed in the background."
    else:
        summary += "- " + content + "\n"
        
    summary += "\n\n💡 AI Study Tip: Switch your NotesFlix UI to 'Exam Mode' and try to recall these points from memory!"
    
    return jsonify({'summary': summary})

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    total_notes = Note.query.filter_by(user_id=user.id).count()
    return render_template('dashboard.html', user=user, total_notes=total_notes)

# --- Database Initialization ---
def seed_db():
    if Subject.query.first():
        return
    
    subjects_to_add = [
        # Trending
        Subject(title="Deep Learning with PyTorch", rating=4.9, difficulty="Advanced", category="Trending", professor_verified=True),
        Subject(title="MERN Stack Masterclass", rating=4.8, difficulty="Intermediate", category="Trending", professor_verified=True),
        Subject(title="Cybersecurity Fundamentals", rating=4.7, difficulty="Beginner", category="Trending", professor_verified=True),
        
        # Core CSE
        Subject(title="Data Structures & Algorithms", rating=4.9, difficulty="Intermediate", category="Core CSE", professor_verified=True),
        Subject(title="Operating Systems", rating=4.5, difficulty="Intermediate", category="Core CSE", professor_verified=True),
        Subject(title="Database Management (SQL)", rating=4.6, difficulty="Beginner", category="Core CSE", professor_verified=True),
        
        # AI
        Subject(title="Generative AI & LLMs", rating=4.9, difficulty="Advanced", category="AI", professor_verified=True),
        Subject(title="Computer Vision with OpenCV", rating=4.7, difficulty="Intermediate", category="AI", professor_verified=False),
        Subject(title="Natural Language Processing", rating=4.8, difficulty="Advanced", category="AI", professor_verified=True),
        
        # Beginner Friendly
        Subject(title="Python for Absolute Beginners", rating=4.9, difficulty="Beginner", category="Beginner", professor_verified=True),
        Subject(title="Introduction to Web Development", rating=4.8, difficulty="Beginner", category="Beginner", professor_verified=True),
        Subject(title="Discrete Mathematics for CS", rating=4.2, difficulty="Intermediate", category="Beginner", professor_verified=False),
    ]
    
    db.session.bulk_save_objects(subjects_to_add)
    db.session.commit()

# Automatically create tables for production (Render)
with app.app_context():
    db.create_all()
    try:
        seed_db()
    except Exception as e:
        print(f"Error seeding database: {e}")

if __name__ == '__main__':
    app.run(debug=True)
