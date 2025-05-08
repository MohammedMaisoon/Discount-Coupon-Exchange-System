from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from database import db
from models import User, Coupon, Category, Rating
from flask_wtf.csrf import CSRFProtect
from models import User, Coupon, Category, Rating, SavedCoupon
from datetime import datetime, timedelta
from flask_login import LoginManager, login_user, logout_user, login_required, current_user






# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'discount_coupon_exchange_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coupons.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the app
db.init_app(app)

# Function to create tables and initialize data
def initialize_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default categories if they don't exist
        categories = ["Retail", "Food and Beverage", "Travel", "Electronics", "Entertainment", "Health", "Beauty", "Home"]
        
        for category_name in categories:
            if not Category.query.filter_by(name=category_name).first():
                category = Category(name=category_name)
                db.session.add(category)
        
        # Create admin user if not exists
        if not User.query.filter_by(email="admin@example.com").first():
            admin = User(
                username="admin",
                email="admin@example.com",
                password=generate_password_hash("admin123"),
                is_admin=True
            )
            db.session.add(admin)
        
        db.session.commit()
# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# Routes
@app.route('/')
def index():
    latest_coupons = Coupon.query.filter(Coupon.expiry_date >= datetime.now()).order_by(Coupon.created_at.desc()).limit(8).all()
    categories = Category.query.all()
    return render_template('index.html', coupons=latest_coupons, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    from forms import LoginForm
    
    form = LoginForm()  # Create an instance of the form
    
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)  # Use Flask-Login
            session['user_id'] = user.id  # Keep this for backward compatibility
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)  # Pass the form to the template

@app.route('/register', methods=['GET', 'POST'])
def register():
    from forms import RegistrationForm  # Import at function level to avoid circular imports
    
    form = RegistrationForm()  # Create an instance of the form
    
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=password
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)  # Pass the form to the template

@app.route('/logout')
def logout():
    logout_user()
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access the dashboard', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user_coupons = Coupon.query.filter_by(user_id=user.id).all()
    
    # Create user_stats object
    user_stats = {
        'coupons_shared': len(user_coupons),
        'coupons_active': sum(1 for c in user_coupons if c.expiry_date >= datetime.now()),
        'coupons_expired': sum(1 for c in user_coupons if c.expiry_date < datetime.now()),
        # Add any other stats you need
    }
    
    return render_template('dashboard.html', user=user, coupons=user_coupons, user_stats=user_stats)

@app.route('/coupons')
def coupons():
    category_id = request.args.get('category')
    search_query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Number of coupons per page
    
    # Base query
    coupons_query = Coupon.query.filter(Coupon.expiry_date >= datetime.now())
    
    # Apply filters
    if category_id:
        coupons_query = coupons_query.filter_by(category_id=category_id)
    
    if search_query:
        coupons_query = coupons_query.filter(Coupon.title.contains(search_query) | 
                                             Coupon.description.contains(search_query) |
                                             Coupon.store.contains(search_query))
    
    # Get total count before pagination
    total_coupons = coupons_query.count()
    
    # Apply pagination
    paginated_coupons = coupons_query.order_by(Coupon.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all categories
    categories = Category.query.all()
    
    # Get unique stores for filtering
    stores = db.session.query(Coupon.store).distinct().all()
    stores = [store[0] for store in stores if store[0]]  # Clean up the results
    
    # Get category object if category_id is provided
    category = None
    if category_id:
        category = Category.query.get(category_id)
    
    # Calculate total pages
    total_pages = (total_coupons + per_page - 1) // per_page
    
    # Handle saved coupons for logged-in users
    saved_coupons = []
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        # Assuming you have a saved_coupons relationship, adjust as needed
        # For example, if you have a SavedCoupon model with user_id and coupon_id fields:
        saved_coupons_query = db.session.query(SavedCoupon.coupon_id).filter_by(user_id=session['user_id']).all()
        saved_coupons = [item[0] for item in saved_coupons_query]
    
    return render_template(
        'coupon_listing.html',
        coupons=paginated_coupons.items,  # Use .items to get the actual coupons
        categories=categories,
        stores=stores,
        total_coupons=total_coupons,
        total_pages=total_pages,
        page=page,
        has_next=paginated_coupons.has_next,
        has_prev=paginated_coupons.has_prev,
        search_query=search_query,
        category=category,
        saved_coupons=saved_coupons
    )

@app.route('/coupon/<int:coupon_id>')
def coupon_detail(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    ratings = Rating.query.filter_by(coupon_id=coupon_id).all()
    
    avg_rating = 0
    if ratings:
        avg_rating = sum(r.score for r in ratings) / len(ratings)
    
    return render_template('coupon_detail.html', coupon=coupon, ratings=ratings, avg_rating=avg_rating)

@app.route('/add_coupon', methods=['GET', 'POST'])
def add_coupon():
    if 'user_id' not in session:
        flash('Please login to add coupons', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        code = request.form.get('code')
        discount_value = request.form.get('discount_value')
        store = request.form.get('store')
        category_id = request.form.get('category_id')
        expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d')
        
        new_coupon = Coupon(
            title=title,
            description=description,
            code=code,
            discount_value=discount_value,
            store=store,
            category_id=category_id,
            expiry_date=expiry_date,
            user_id=session['user_id']
        )
        
        db.session.add(new_coupon)
        db.session.commit()
        
        flash('Coupon added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    categories = Category.query.all()
    return render_template('add_coupon.html', categories=categories)

@app.route('/edit_coupon/<int:coupon_id>', methods=['GET', 'POST'])
def edit_coupon(coupon_id):
    if 'user_id' not in session:
        flash('Please login to edit coupons', 'warning')
        return redirect(url_for('login'))
    
    coupon = Coupon.query.get_or_404(coupon_id)
    
    # Ensure the coupon belongs to the logged-in user
    if coupon.user_id != session['user_id']:
        flash('You are not authorized to edit this coupon', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        coupon.title = request.form.get('title')
        coupon.description = request.form.get('description')
        coupon.code = request.form.get('code')
        coupon.discount_value = request.form.get('discount_value')
        coupon.store = request.form.get('store')
        coupon.category_id = request.form.get('category_id')
        coupon.expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d')
        
        db.session.commit()
        
        flash('Coupon updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    categories = Category.query.all()
    return render_template('edit_coupon.html', coupon=coupon, categories=categories)

@app.route('/delete_coupon/<int:coupon_id>')
def delete_coupon(coupon_id):
    if 'user_id' not in session:
        flash('Please login to delete coupons', 'warning')
        return redirect(url_for('login'))
    
    coupon = Coupon.query.get_or_404(coupon_id)
    
    # Ensure the coupon belongs to the logged-in user or is an admin
    user = User.query.get(session['user_id'])
    if coupon.user_id != session['user_id'] and not user.is_admin:
        flash('You are not authorized to delete this coupon', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(coupon)
    db.session.commit()
    
    flash('Coupon deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/rate_coupon/<int:coupon_id>', methods=['POST'])
def rate_coupon(coupon_id):
    if 'user_id' not in session:
        flash('Please login to rate coupons', 'warning')
        return redirect(url_for('login'))
    
    score = int(request.form.get('score'))
    comment = request.form.get('comment')
    
    # Check if user already rated this coupon
    existing_rating = Rating.query.filter_by(user_id=session['user_id'], coupon_id=coupon_id).first()
    
    if existing_rating:
        existing_rating.score = score
        existing_rating.comment = comment
    else:
        new_rating = Rating(
            score=score,
            comment=comment,
            user_id=session['user_id'],
            coupon_id=coupon_id
        )
        db.session.add(new_rating)
    
    db.session.commit()
    
    flash('Rating submitted successfully!', 'success')
    return redirect(url_for('coupon_detail', coupon_id=coupon_id))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please login to view profile', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user_coupons = Coupon.query.filter_by(user_id=user.id).all()
    
    # Calculate user stats
    user_stats = {
        'coupons_count': len(user_coupons),
        'active_coupons': sum(1 for c in user_coupons if c.expiry_date >= datetime.now()),
        'expired_coupons': sum(1 for c in user_coupons if c.expiry_date < datetime.now()),
        'join_date': user.created_at.strftime('%B %d, %Y') if hasattr(user, 'created_at') else 'Unknown',
        # Add any other stats needed
    }
    
    # Add these for the pagination issues
    coupon_pages = 1  # Or calculate based on your pagination logic
    review_pages = 1  # Add this line to fix the error
    
    return render_template('profile.html', user=user, user_stats=user_stats, 
                           coupon_pages=coupon_pages, review_pages=review_pages)

@app.route('/admin')
def admin_panel():
    if 'user_id' not in session:
        flash('Please login to access admin panel', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if not user.is_admin:
        flash('You do not have permission to access the admin panel', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    categories = Category.query.all()
    
    return render_template('admin.html', users=users, coupons=coupons, categories=categories)
@app.route('/reset_password_request')
def reset_password_request():
    flash('Password reset functionality is not available yet.', 'info')
    return redirect(url_for('login'))
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    from forms import ResetPasswordForm
    
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    # Here you would typically:
    # 1. Verify the token
    # 2. Find the associated user
    # For a simple example, we'll just redirect to login with a message
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        # Update the user's password
        flash('Your password has been reset successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('reset_password.html', form=form)
@app.route('/saved_coupons')
def saved_coupons():
    if 'user_id' not in session:
        flash('Please login to view saved coupons', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get the saved coupons for this user
    saved = db.session.query(
        Coupon
    ).join(
        SavedCoupon, SavedCoupon.coupon_id == Coupon.id
    ).filter(
        SavedCoupon.user_id == user.id
    ).all()
    
    # Pass current datetime to template for expiry checking
    now = datetime.now()
    
    return render_template('saved_coupons.html', user=user, saved_coupons=saved, now=now)
@app.route('/save_coupon/<int:coupon_id>')
def save_coupon(coupon_id):
    if 'user_id' not in session:
        flash('Please login to save coupons', 'warning')
        return redirect(url_for('login'))
    
    # Check if already saved
    existing = SavedCoupon.query.filter_by(
        user_id=session['user_id'], 
        coupon_id=coupon_id
    ).first()
    
    if not existing:
        saved_coupon = SavedCoupon(
            user_id=session['user_id'],
            coupon_id=coupon_id
        )
        db.session.add(saved_coupon)
        db.session.commit()
        flash('Coupon saved successfully!', 'success')
    else:
        flash('Coupon already saved', 'info')
    
    # Return to the page the user was on
    return redirect(request.referrer or url_for('coupon_detail', coupon_id=coupon_id))

@app.route('/unsave_coupon/<int:coupon_id>')
def unsave_coupon(coupon_id):
    if 'user_id' not in session:
        flash('Please login to manage saved coupons', 'warning')
        return redirect(url_for('login'))
    
    saved_coupon = SavedCoupon.query.filter_by(
        user_id=session['user_id'], 
        coupon_id=coupon_id
    ).first()
    
    if saved_coupon:
        db.session.delete(saved_coupon)
        db.session.commit()
        flash('Coupon removed from saved list', 'success')
    
    # Return to the page the user was on
    return redirect(request.referrer or url_for('saved_coupons'))
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('Please login to edit your profile', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        
        # Only update password if provided
        password = request.form.get('password')
        if password and password.strip():
            user.password = generate_password_hash(password)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', user=user)
@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        flash('Please login to view notifications', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # In a real application, you would fetch actual notifications here
    # For now, let's create some dummy notifications
    notifications = [
        {"id": 1, "message": "Your coupon for RetailStore was used 5 times!", "is_read": False, "created_at": datetime.now() - timedelta(hours=2)},
        {"id": 2, "message": "Welcome to CouponExchange.AI!", "is_read": True, "created_at": datetime.now() - timedelta(days=1)}
    ]
    
    return render_template('notifications.html', user=user, notifications=notifications)
@app.route('/my_coupons')
def my_coupons():
    if 'user_id' not in session:
        flash('Please login to view your coupons', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user_coupons = Coupon.query.filter_by(user_id=user.id).order_by(Coupon.created_at.desc()).all()
    
    # Get the current date for expiry checking
    now = datetime.now()
    
    return render_template('my_coupons.html', user=user, coupons=user_coupons, now=now)

if __name__ == '__main__':
    # Initialize database before running the app
    initialize_database()
    app.run(debug=True)