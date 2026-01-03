from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, trip, tripsections
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__, template_folder='../frontend/templates')
app.config['SECRET_KEY'] = 'key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sarvn.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route("/")
def home():
    return render_template("base.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("FORM DATA:", dict(request.form))
        
        firstname = request.form.get('Firstname')
        lastname = request.form.get('Lastname')
        email = request.form.get('Email')
        phone = request.form.get('Phone')
        city = request.form.get('City')
        country = request.form.get('Country')
        password = request.form.get('Password')

        if not all([firstname, lastname, email, phone, city, country, password]):
            flash('All fields required')
            return render_template('register.html')

        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')

        user = User(firstname=firstname, lastname=lastname, email=email,
                    phone=phone, city=city, country=country, password=password_hash)
        db.session.add(user)
        db.session.commit()
        flash('User Registered Successfully!')
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login Successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect or Invalid Credentials')
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']

    # User's trips for calendar and recap
    user_trips = trip.query.filter_by(user_id=user_id).order_by(trip.startdate.asc()).all()
    completed_trips = [t for t in user_trips if (t.status or '').lower() == 'completed']

    # Simple discovery section pulling other users' recent trips
    popular_trips = trip.query.filter(trip.user_id != user_id).order_by(trip.id.desc()).limit(4).all()

    # Events for the calendar widget
    calendar_events = [
        {"title": t.place, "start": t.startdate, "end": t.enddate}
        for t in user_trips
    ]

    return render_template(
        'dashboard.html',
        popular_trips=popular_trips,
        user_trips=completed_trips,
        calendar_events=calendar_events
    )


@app.route('/calendar')
@login_required
def calendar():
    user_id = session['user_id']
    user_trips = trip.query.filter_by(user_id=user_id).order_by(trip.startdate.asc()).all()

    calendar_events = [
        {"title": t.place, "start": t.startdate, "end": t.enddate}
        for t in user_trips
    ]

    return render_template('calendar.html', calendar_events=calendar_events)

@app.route('/create-trip', methods=['GET', 'POST'])  # SINGLE ROUTE
@login_required
def create_trip():
    if request.method == 'POST':
        new_trip = trip(
            startdate=request.form['startdate'],
            enddate=request.form['enddate'],
            place=request.form.get('trip_name', request.form.get('place')),
            description=request.form['description'],
            user_id=session['user_id'],
            status='Planning'
        )
        db.session.add(new_trip)
        db.session.commit()
        flash('Trip created!')
        return redirect(url_for('my_trips'))
    return render_template('create_trip.html')

from datetime import date

@app.route('/my-trips')
@login_required
def my_trips():
    trips = trip.query.filter_by(user_id=session['user_id']).order_by(trip.id.desc()).all()

    today = date.today().isoformat()  # works because your dates are stored as "YYYY-MM-DD" strings
    ongoing, upcoming, completed = [], [], []

    for t in trips:
        status = (t.status or "").lower()

        # If you already set status properly, this is enough
        if status == "completed":
            completed.append(t)
            continue
        if status == "ongoing":
            ongoing.append(t)
            continue
        if status == "upcoming":
            upcoming.append(t)
            continue

        # Otherwise auto-classify using date strings
        # (ISO string compare works: "2026-01-03" etc.)
        if t.startdate <= today <= t.enddate:
            ongoing.append(t)
        elif today < t.startdate:
            upcoming.append(t)
        else:
            completed.append(t)

    return render_template(
        "my_trips.html",
        ongoing_trips=ongoing,
        upcoming_trips=upcoming,
        completed_trips=completed
    )


@app.route('/itinerary-builder/<int:trip_id>')
@login_required
def itinerary_builder(trip_id):
    trip_data = trip.query.get_or_404(trip_id)
    sections = tripsections.query.filter_by(trip_id=trip_id).all()
    return render_template('itinerary_builder.html', trip=trip_data, sections=sections)

@app.route('/trip-budget/<int:trip_id>')
@login_required
def trip_budget(trip_id):
    trip_data = trip.query.get_or_404(trip_id)
    return render_template('trip_budget.html', trip=trip_data)

@app.route('/profile')
@login_required
def profile():
    user = User.query.get_or_404(session['user_id'])

    # Preplanned = upcoming + ongoing (not completed)
    preplanned_trips = trip.query.filter(
        trip.user_id == session['user_id'],
        trip.status != 'Completed'
    ).order_by(trip.id.desc()).all()

    # Previous = completed
    previous_trips = trip.query.filter_by(
        user_id=session['user_id'],
        status='Completed'
    ).order_by(trip.id.desc()).all()

    return render_template(
        'profile.html',
        user=user,
        preplanned_trips=preplanned_trips,
        previous_trips=previous_trips
    )


@app.route('/city-search')
@login_required
def city_search():
    return render_template('city_search.html')

from sqlalchemy import func

@app.route('/activity-search', methods=['GET'])
@login_required
def activity_search():
    q = (request.args.get('q') or '').strip()
    sort_by = (request.args.get('sort_by') or 'recent').strip()

    query = trip.query.filter(trip.user_id != session['user_id'])  # other users only
    query = query.filter(trip.status != 'Completed')              # planned trips

    if q:
        q_lower = q.lower()
        query = query.filter(func.lower(trip.place).contains(q_lower))  # robust search

    if sort_by == 'recent':
        query = query.order_by(trip.id.desc())
    elif sort_by == 'oldest':
        query = query.order_by(trip.id.asc())
    elif sort_by == 'place':
        query = query.order_by(trip.place.asc())

    results = query.all()
    return render_template('activity_search.html', q=q, sort_by=sort_by, results=results)

@app.route('/trip-calendar/<int:trip_id>')
@login_required
def trip_calendar(trip_id):
    trip_data = trip.query.get_or_404(trip_id)
    return render_template('trip_calendar.html', trip=trip_data)

@app.route('/shared/<int:trip_id>')
def shared_itinerary(trip_id):
    trip_data = trip.query.get_or_404(trip_id)
    return render_template('shared_itinerary.html', trip=trip_data)

@app.route('/add-section/<int:trip_id>', methods=['POST'])
@login_required
def add_section(trip_id):
    if request.method == 'POST':
        new_section = tripsections(
            sectionname=request.form['sectionname'],
            description=request.form.get('description', ''),  # NEW FIELD
            startdate=request.form['startdate'],
            enddate=request.form['enddate'],
            budget=float(request.form.get('budget', 0)) if request.form.get('budget') else None,
            trip_id=trip_id
        )
        db.session.add(new_section)
        db.session.commit()
        flash('Section added successfully!')
    return redirect(url_for('itinerary_builder', trip_id=trip_id))


@app.route('/delete-section/<int:section_id>', methods=['DELETE'])
@login_required
def delete_section(section_id):
    section = tripsections.query.get_or_404(section_id)
    if section.trip.user_id != session['user_id']:
        abort(403)
    db.session.delete(section)
    db.session.commit()
    return '', 204

@app.route('/profile-update', methods=['POST'])
@login_required
def profile_update():
    user = User.query.get(session['user_id'])
    user.firstname = request.form['firstname']
    user.email = request.form['email']
    db.session.commit()
    flash('Profile updated!')
    return redirect(url_for('profile'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

