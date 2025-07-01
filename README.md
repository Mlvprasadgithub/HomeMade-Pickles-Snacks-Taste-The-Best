# HomeMade Pickles & Snacks - E-commerce Platform

A comprehensive e-commerce platform for authentic homemade pickles and traditional snacks, built with Flask backend and modern frontend technologies.

## 🌟 Features

### Core Functionality
- **User Authentication**: Secure login/signup system
- **Product Catalog**: Browse vegetarian pickles, non-veg pickles, and traditional snacks
- **Shopping Cart**: Add, update, and remove items
- **Order Management**: Complete checkout process with order confirmation
- **Responsive Design**: Mobile-first approach with beautiful UI

### Technical Features
- **Flask Backend**: RESTful API with session management
- **Real-time Updates**: Dynamic cart count and inventory tracking
- **Modern CSS**: Gradient designs, animations, and micro-interactions
- **Production Ready**: Scalable architecture for cloud deployment

## 🚀 Local Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step-by-Step Installation

1. **Clone or Download the Project**
   ```bash
   # If using git
   git clone <repository-url>
   cd homemade-pickles-platform
   
   # Or download and extract the ZIP file
   ```

2. **Create Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Application**
   - Open your browser and go to: `http://localhost:5000`
   - The application will be running on port 5000

### Project Structure
```
homemade-pickles-platform/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── login.html        # Login page
│   ├── signup.html       # Registration page
│   ├── cart.html         # Shopping cart
│   ├── checkout.html     # Checkout page
│   ├── success.html      # Order success
│   ├── about.html        # About page
│   ├── contact_us.html   # Contact page
│   ├── veg_pickles.html  # Vegetarian pickles
│   ├── non_veg_pickles.html # Non-veg pickles
│   └── snacks.html       # Traditional snacks
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   └── js/
│       └── main.js       # JavaScript functionality
└── README.md            # This file
```

## 🎯 Usage Guide

### For Users
1. **Browse Products**: Visit different categories (Veg Pickles, Non-Veg Pickles, Snacks)
2. **Create Account**: Sign up with email and password
3. **Add to Cart**: Click "Add to Cart" on any product
4. **Checkout**: Review cart and place order with shipping details
5. **Order Confirmation**: Receive order confirmation with details

### For Developers
1. **Database**: Currently uses in-memory storage (replace with DynamoDB for production)
2. **Authentication**: Session-based authentication (can be enhanced with JWT)
3. **API Endpoints**: RESTful endpoints for cart management and product data
4. **Responsive Design**: Mobile-first CSS with Flexbox and Grid

## 🛠 AWS Cloud Deployment Steps

### Milestone 1: Web Application Development ✅
- [x] Flask backend with all routes
- [x] HTML templates with responsive design
- [x] CSS styling with modern aesthetics
- [x] JavaScript for interactivity
- [x] Local testing and validation

### Milestone 2: AWS Account Setup
1. Create AWS account
2. Set up billing alerts
3. Configure IAM users and roles
4. Set up AWS CLI

### Milestone 3: DynamoDB Database Setup
1. Create DynamoDB tables:
   - Users table
   - Products table
   - Orders table
   - Cart table
2. Configure indexes and relationships
3. Update Flask app to use DynamoDB

### Milestone 4: IAM Role Setup
1. Create EC2 instance role
2. Attach DynamoDB access policies
3. Configure security groups

### Milestone 5: EC2 Instance Setup
1. Launch EC2 instance (t2.micro for free tier)
2. Configure security groups (HTTP, HTTPS, SSH)
3. Install Python, pip, and dependencies
4. Set up application environment

### Milestone 6: Deployment on EC2
1. Transfer application files to EC2
2. Install and configure web server (Nginx/Apache)
3. Set up WSGI server (Gunicorn)
4. Configure domain and SSL

### Milestone 7: Testing and Optimization
1. Load testing
2. Performance optimization
3. Security hardening
4. Monitoring setup

## 🔧 Configuration

### Environment Variables (for production)
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export AWS_REGION=us-east-1
export DYNAMODB_TABLE_PREFIX=homemade-pickles
```

### Database Schema (DynamoDB)
- **Users**: user_id, email, name, phone, password_hash, created_at
- **Products**: product_id, name, category, price, description, stock, image_url
- **Orders**: order_id, user_id, items, total, status, shipping_address, created_at
- **Cart**: user_id, product_id, quantity, updated_at

## 🎨 Design Features

- **Color Scheme**: Orange gradient (#ff6b35 to #f7931e) with professional aesthetics
- **Typography**: Clean, readable fonts with proper hierarchy
- **Animations**: Smooth transitions and hover effects
- **Responsive**: Mobile-first design with breakpoints
- **Accessibility**: Proper contrast ratios and semantic HTML

## 🔒 Security Features

- Session management for user authentication
- CSRF protection (can be enhanced)
- Input validation and sanitization
- Secure password handling (to be enhanced with hashing)

## 📱 Mobile Responsiveness

- Mobile-first CSS approach
- Responsive navigation with hamburger menu
- Touch-friendly buttons and interactions
- Optimized images and performance

## 🚀 Performance Optimizations

- Lazy loading for images
- Minified CSS and JavaScript
- Efficient database queries
- Caching strategies (to be implemented)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support and questions:
- Email: info@homemadepickles.com
- Phone: +91 9876543210

---

**"Preserving Traditions, One Jar at a Time"** 🥒✨