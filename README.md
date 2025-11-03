# ReStitch - Sustainable Fashion Platform

ReStitch is a modern web application that transforms donated clothes into beautiful upcycled fashion. Built with Flask, it offers a complete platform for clothing donation, redesign services, and sustainable fashion retail.

## Features

### Core Functionality
- **Clothing Donation & Pickup Scheduling** - Users can schedule convenient pickups for their unused clothes
- **Redesign & Upcycling Services** - Professional designers transform old clothes into new fashion pieces
- **Upcycled Fashion Store** - Browse and purchase unique, sustainable fashion items
- **Order Tracking** - Real-time tracking with QR codes and barcodes
- **Impact Dashboard** - Track personal environmental impact and sustainability metrics
- **Reward Points System** - Earn and redeem points for sustainable actions

### Technical Features
- **Modern UI/UX** - Responsive design with Tailwind CSS, glassmorphism effects, and micro-interactions
- **Secure Authentication** - Role-based access control (User, Designer, Admin)
- **Admin Panel** - Complete order management, product catalog, and user administration
- **API Endpoints** - Public tracking API and statistics endpoints
- **Real-time Updates** - WebSocket support for live order status updates
- **SEO Optimized** - Server-side rendering with proper meta tags and structured data

## Tech Stack

### Backend
- **Python 3.10+** with Flask framework
- **SQLAlchemy** ORM with PostgreSQL (production) / SQLite (development)
- **Flask-Login** for authentication
- **Flask-WTF** for forms and CSRF protection
- **Flask-Migrate** for database migrations
- **Flask-Mail** for email notifications
- **Flask-SocketIO** for real-time features

### Frontend
- **Tailwind CSS** for styling with custom design system
- **Vanilla JavaScript** with modern ES6+ features
- **Jinja2** templates for server-side rendering
- **Progressive enhancement** approach

### Infrastructure
- **Docker** containerization
- **Nginx** reverse proxy and static file serving
- **Redis** for caching and session storage
- **Gunicorn** WSGI server for production

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js (for Tailwind CSS development)
- Docker & Docker Compose (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd restitch
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Seed sample data**
   ```bash
   python seed.py
   ```

7. **Run the application**
   ```bash
   flask run
   ```

Visit `http://localhost:5000` to access the application.

### Docker Development

1. **Start services**
   ```bash
   docker-compose up -d
   ```

2. **Initialize database**
   ```bash
   docker-compose exec web flask db upgrade
   docker-compose exec web python seed.py
   ```

## Sample Login Credentials

After running the seed script:

- **Admin**: admin@restitch.com / admin123
- **Designer**: designer@restitch.com / designer123
- **User**: priya@example.com / password123

## Project Structure

```
restitch/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models
│   ├── auth/                # Authentication blueprint
│   ├── main/                # Main pages blueprint
│   ├── store/               # Store functionality blueprint
│   ├── admin/               # Admin panel blueprint
│   ├── api/                 # API endpoints blueprint
│   ├── templates/           # Jinja2 templates
│   └── static/              # Static assets
├── migrations/              # Database migrations
├── uploads/                 # File uploads directory
├── config.py               # Configuration settings
├── restitch.py             # Application entry point
├── seed.py                 # Database seeding script
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── README.md              # This file
```

## Key Pages & Routes

### Public Pages
- `/` - Landing page with hero section and featured products
- `/about` - About ReStitch and sustainability mission
- `/how-it-works` - Step-by-step process explanation
- `/services` - Available services overview
- `/store` - Upcycled fashion catalog
- `/store/<slug>` - Product detail pages
- `/contact` - Contact form

### User Dashboard (Authentication Required)
- `/dashboard` - Personal impact metrics and quick actions
- `/schedule-pickup` - Pickup scheduling form
- `/my-orders` - Order history and tracking
- `/redeem` - Reward points redemption
- `/profile` - User profile management

### Admin Panel (Admin Role Required)
- `/admin` - Admin dashboard with statistics
- `/admin/orders` - Order management
- `/admin/products` - Product catalog management
- `/admin/users` - User administration

### API Endpoints
- `/api/track/<barcode>` - Public order tracking
- `/api/stats` - Public statistics

## Database Models

### Core Models
- **User** - User accounts with role-based permissions
- **Address** - User addresses for pickups and deliveries
- **PickupRequest** - Scheduled clothing pickups
- **Order** - Redesign orders with status tracking
- **Product** - Upcycled items in the store
- **Transaction** - Purchase transactions
- **ActivityLog** - System activity logging

## Features in Detail

### Pickup Scheduling
- Calendar-based date/time selection
- Address management
- Service type selection (donate/redesign/resale)
- Photo upload for item documentation
- Real-time availability checking

### Order Tracking
- QR code generation for each order
- Status timeline visualization
- Email notifications for status updates
- Public tracking pages (no login required)

### Admin Features
- Order status management
- Designer assignment
- Barcode generation
- Points award system
- Product catalog management
- User role management

### Reward Points System
- Points earned for donations and purchases
- Redemption for discounts and services
- Gamification elements
- Impact visualization

## Security Features

- **CSRF Protection** - All forms protected with CSRF tokens
- **Input Validation** - Server-side validation for all user inputs
- **Role-Based Access Control** - Proper permission checking
- **Secure Password Hashing** - bcrypt for password storage
- **Rate Limiting** - Protection against abuse
- **File Upload Security** - Type and size validation

## Performance Optimizations

- **Database Indexing** - Optimized queries with proper indexes
- **Static Asset Caching** - Long-term caching for static files
- **Image Optimization** - Lazy loading and responsive images
- **Gzip Compression** - Reduced bandwidth usage
- **CDN Ready** - Static assets can be served from CDN

## Deployment

### Production Deployment

1. **Build Docker image**
   ```bash
   docker build -t restitch:latest .
   ```

2. **Set up production environment**
   - Configure PostgreSQL database
   - Set up Redis instance
   - Configure Nginx reverse proxy
   - Set up SSL certificates

3. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Environment Variables

Required environment variables for production:

```bash
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://host:port/0
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## Testing

Run tests with pytest:

```bash
pytest
pytest --cov=app  # With coverage
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Email: support@restitch.com
- Documentation: [Link to docs]
- Issues: [GitHub Issues]

---

**ReStitch** - Give old clothes a new life 🌱