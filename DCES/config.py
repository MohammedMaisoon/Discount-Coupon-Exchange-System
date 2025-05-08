import os
from datetime import timedelta

class Config:
    # Base Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-secure-key-for-couponexchange'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
    
    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    
    # Pagination
    COUPONS_PER_PAGE = 12
    USERS_PER_PAGE = 15
    REPORTS_PER_PAGE = 20
    
    # Admin Settings
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@couponexchange.ai'
    
    # AI Settings
    AI_API_KEY = os.environ.get('AI_API_KEY')
    AI_API_URL = os.environ.get('AI_API_URL') or 'https://api.openai.com/v1/chat/completions'
    AI_MODEL = os.environ.get('AI_MODEL') or 'gpt-4'
    VERIFICATION_THRESHOLD = 80  # Default threshold percentage for AI verification
    
    # System Settings
    ALLOW_REGISTRATION = True
    EMAIL_VERIFICATION = True
    REQUIRE_APPROVAL = True
    MAX_COUPONS_PER_USER = 50
    MAX_EXPIRY_DAYS = 365
    ALLOW_EXTERNAL_LINKS = False
    AUTO_CATEGORIZE = True
    
    # Security
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'security-salt-for-couponexchange'
    
    # Redis Cache (optional)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Content Moderation
    CONTENT_MODERATION_ENABLED = True
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dev.db')
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.db')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'couponexchange.db')
    
    # Production specific settings
    DEBUG = False
    TESTING = False
    
    # Security in production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}