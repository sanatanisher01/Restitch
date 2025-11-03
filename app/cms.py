from app import db
from datetime import datetime
from sqlalchemy import Text, Boolean, DateTime

# Add these models to your models.py file
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(Text, nullable=False)
    excerpt = db.Column(db.String(500))
    featured_image = db.Column(db.String(500))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(100))
    tags = db.Column(db.String(500))
    is_published = db.Column(Boolean, default=False)
    published_at = db.Column(DateTime)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    author = db.relationship('User', backref='blog_posts')
    
    def get_tags(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()] if self.tags else []

class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(Text, nullable=False)
    category = db.Column(db.String(100))
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    link_url = db.Column(db.String(500))
    button_text = db.Column(db.String(100))
    position = db.Column(db.String(50), default='hero')  # hero, sidebar, footer
    is_active = db.Column(Boolean, default=True)
    start_date = db.Column(DateTime)
    end_date = db.Column(DateTime)
    created_at = db.Column(DateTime, default=datetime.utcnow)

class CMSManager:
    @staticmethod
    def get_published_posts(limit=None):
        query = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.published_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_post_by_slug(slug):
        return BlogPost.query.filter_by(slug=slug, is_published=True).first()
    
    @staticmethod
    def get_faqs_by_category(category=None):
        query = FAQ.query.filter_by(is_active=True).order_by(FAQ.order)
        if category:
            query = query.filter_by(category=category)
        return query.all()
    
    @staticmethod
    def get_active_banners(position='hero'):
        now = datetime.utcnow()
        from sqlalchemy import or_
        return Banner.query.filter(
            Banner.is_active == True,
            Banner.position == position,
            or_(Banner.start_date.is_(None), Banner.start_date <= now),
            or_(Banner.end_date.is_(None), Banner.end_date >= now)
        ).all()
    
    @staticmethod
    def create_blog_post(title, content, author_id, **kwargs):
        slug = title.lower().replace(' ', '-').replace('/', '-')
        
        post = BlogPost(
            title=title,
            slug=slug,
            content=content,
            author_id=author_id,
            **kwargs
        )
        
        db.session.add(post)
        db.session.commit()
        return post
    
    @staticmethod
    def create_faq(question, answer, category=None):
        faq = FAQ(
            question=question,
            answer=answer,
            category=category
        )
        
        db.session.add(faq)
        db.session.commit()
        return faq