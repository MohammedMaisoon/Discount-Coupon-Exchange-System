from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateField, DecimalField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, URL, Optional, NumberRange, ValidationError
from datetime import datetime, timedelta


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    terms = BooleanField('I agree to the Terms and Conditions', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        from models import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')

    def validate_email(self, email):
        from models import User
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')


class CouponForm(FlaskForm):
    title = StringField('Coupon Title', validators=[DataRequired(), Length(min=5, max=100)])
    store = StringField('Store Name', validators=[DataRequired(), Length(min=2, max=50)])
    code = StringField('Coupon Code', validators=[DataRequired(), Length(min=2, max=30)])
    discount_type = SelectField('Discount Type', choices=[
        ('percentage', 'Percentage (%)'),
        ('fixed', 'Fixed Amount'),
        ('freebie', 'Free Item/Gift'),
        ('shipping', 'Free Shipping')
    ], validators=[DataRequired()])
    discount_value = StringField('Discount Value', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=1000)])
    terms = TextAreaField('Terms & Conditions', validators=[Optional(), Length(max=2000)])
    category = SelectField('Category', choices=[
        ('fashion', 'Fashion & Apparel'),
        ('electronics', 'Electronics & Gadgets'),
        ('home', 'Home & Furniture'),
        ('beauty', 'Beauty & Health'),
        ('food', 'Food & Dining'),
        ('travel', 'Travel & Hotels'),
        ('entertainment', 'Entertainment'),
        ('services', 'Services'),
        ('software', 'Software & Apps'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    expiry_date = DateField('Expiry Date', format='%Y-%m-%d', validators=[DataRequired()])
    store_url = StringField('Store Website', validators=[Optional(), URL()])
    store_logo = FileField('Store Logo', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Submit Coupon')

    def validate_expiry_date(self, expiry_date):
        # Check if expiry date is in the past
        if expiry_date.data < datetime.now().date():
            raise ValidationError('Expiry date cannot be in the past.')
        
        # Check if expiry date is too far in the future
        from flask import current_app
        max_days = current_app.config['MAX_EXPIRY_DAYS']
        if expiry_date.data > (datetime.now() + timedelta(days=max_days)).date():
            raise ValidationError(f'Expiry date cannot be more than {max_days} days in the future.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    avatar = FileField('Update Profile Picture', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    website = StringField('Website', validators=[Optional(), URL()])
    social_links = TextAreaField('Social Media Links', validators=[Optional()])
    submit = SubmitField('Update Profile')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('all', 'All Categories'),
        ('fashion', 'Fashion & Apparel'),
        ('electronics', 'Electronics & Gadgets'),
        ('home', 'Home & Furniture'),
        ('beauty', 'Beauty & Health'),
        ('food', 'Food & Dining'),
        ('travel', 'Travel & Hotels'),
        ('entertainment', 'Entertainment'),
        ('services', 'Services'),
        ('software', 'Software & Apps'),
        ('other', 'Other')
    ], default='all')
    submit = SubmitField('Search')


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=5, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField('Send Message')


class AdminSettingsForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired(), Length(max=100)])
    site_description = TextAreaField('Site Description', validators=[Optional(), Length(max=500)])
    contact_email = StringField('Contact Email', validators=[DataRequired(), Email()])
    items_per_page = IntegerField('Items Per Page', validators=[
        DataRequired(),
        NumberRange(min=5, max=100, message='Value must be between 5 and 100')
    ])
    max_upload_size = IntegerField('Max Upload Size (KB)', validators=[
        DataRequired(),
        NumberRange(min=100, max=5000, message='Value must be between 100KB and 5000KB')
    ])
    max_expiry_days = IntegerField('Maximum Coupon Expiry Days', validators=[
        DataRequired(),
        NumberRange(min=1, max=365, message='Value must be between 1 and 365 days')
    ])
    maintenance_mode = BooleanField('Maintenance Mode')
    analytics_code = TextAreaField('Analytics Code', validators=[Optional()])
    submit = SubmitField('Save Settings')


class ReportCouponForm(FlaskForm):
    reason = SelectField('Reason', choices=[
        ('expired', 'Coupon is Expired'),
        ('invalid', 'Coupon Code is Invalid'),
        ('misleading', 'Misleading Information'),
        ('duplicate', 'Duplicate Coupon'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Submit Report')


class NewsletterForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    subscribe = SubmitField('Subscribe')


class CouponVerificationForm(FlaskForm):
    verified = BooleanField('Mark as Verified')
    notes = TextAreaField('Admin Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Verification Status')


class FeedbackForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        ('5', '5 - Excellent'),
        ('4', '4 - Very Good'),
        ('3', '3 - Good'),
        ('2', '2 - Fair'),
        ('1', '1 - Poor')
    ], validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Feedback')