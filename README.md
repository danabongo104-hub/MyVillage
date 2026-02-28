# MyVillage API

> *"It takes a village to raise a child."*

MyVillage is a RESTful Social Media API built with Django and Django REST Framework. It connects **parents** seeking support and advice with **verified therapists** — creating a structured, safe space for meaningful community interaction.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Setup](#environment-setup)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [User Roles](#user-roles)
- [Running Tests](#running-tests)
- [Deployment](#deployment)

---

## Overview

MyVillage allows users to register as either a **parent** or a **therapist**, create and interact with posts, follow other users, and receive notifications for activity on their content. Therapists go through an admin verification step before appearing in discovery, keeping the platform trustworthy.

**Core features:**
- Role-based user registration (parent / therapist)
- JWT authentication
- Post creation, editing, deletion
- Comments and likes
- Follow / unfollow system
- Personalized feed from followed users
- Keyword search across posts
- Notifications for likes, comments, and follows
- Admin verification flow for therapists

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Framework | Django 6.x |
| API Layer | Django REST Framework |
| Authentication | Simple JWT |
| Database | SQLite (dev) / PostgreSQL (prod) |
| CORS | django-cors-headers |
| Deployment | PythonAnywhere |

---

## Project Structure

```
MyVillage/
├── my_village/          # Project config — settings, main URLs, wsgi
├── users/               # User auth, profiles, follow system
│   ├── models.py        # CustomUser, ParentProfile, TherapistProfile
│   ├── serializers.py   # Register, update, read serializers
│   ├── views.py         # Register, profile, follow, therapist list
│   ├── urls.py
│   └── signals.py       # Auto-creates profile on user registration
├── posts/               # Content — posts, comments, likes
│   ├── models.py        # Post, Comment, Like
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── social/              # Feed and search
│   ├── models.py        # FeedFilter (user feed preferences)
│   ├── views.py         # FeedView, SearchPostsView
│   └── urls.py
├── notifications/       # Activity notifications
│   ├── models.py        # Notification
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
└── manage.py
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- pip
- virtualenv

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/MyVillage.git
cd MyVillage

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers pillow

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser (for admin panel access)
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

The API will be running at `http://127.0.0.1:8000/`

---

## Environment Setup

For production, create a `.env` file in the root directory and make sure it's in your `.gitignore`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.pythonanywhere.com
DATABASE_URL=your-database-url
```

---

## API Endpoints

### Users

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/api/users/register/` | Public | Register as parent or therapist |
| POST | `/api/users/login/` | Public | Login and receive tokens |
| POST | `/api/users/token/refresh/` | Public | Refresh access token |
| GET/PUT | `/api/users/profile/<username>/` | Auth | View or update a profile |
| POST | `/api/users/follow/<username>/` | Auth | Follow or unfollow a user |
| GET | `/api/users/therapists/` | Auth | List verified therapists |
| GET | `/api/users/<username>/followers/` | Auth | List a user's followers |
| GET | `/api/users/<username>/following/` | Auth | List who a user follows |

### Posts

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET/POST | `/api/posts/` | Auth | List all posts or create one |
| GET/PUT/DELETE | `/api/posts/<id>/` | Auth / Owner | View, edit, or delete a post |
| GET/POST | `/api/posts/<id>/comments/` | Auth | View or add comments |
| DELETE | `/api/posts/<id>/comments/<id>/` | Owner | Delete a comment |
| POST | `/api/posts/<id>/like/` | Auth | Like or unlike a post |

### Social

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/social/feed/` | Auth | Posts from followed users |
| GET | `/api/social/search/?q=keyword` | Auth | Search posts by keyword |

### Notifications

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/notifications/` | Auth | Your notifications |
| POST | `/api/notifications/<id>/read/` | Auth | Mark one notification as read |
| POST | `/api/notifications/read-all/` | Auth | Mark all notifications as read |

---

## Authentication

This API uses **JWT (JSON Web Tokens)** for authentication.

**Register or login to get your tokens:**

```json
POST /api/users/login/
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "access": "eyJhbGciOiJIUzI1...",
    "refresh": "eyJhbGciOiJIUzI1..."
}
```

**Use the access token on every protected request:**
```
Authorization: Bearer <your_access_token>
```

Access tokens expire after **60 minutes**. Use the refresh token at `/api/users/token/refresh/` to get a new one without logging in again.

---

## User Roles

### Parent
Registers with optional fields: number of children, age range, and areas of concern.

```json
{
    "username": "jane_parent",
    "email": "jane@example.com",
    "password": "StrongPass123!",
    "password2": "StrongPass123!",
    "role": "parent",
    "parent_profile": {
        "number_of_children": 2,
        "children_age_range": "4-8 years",
        "concerns": "Managing anxiety and screen time"
    }
}
```

### Therapist
Must provide a license number at registration. Will not appear in the therapist discovery list until an admin verifies them via the Django admin panel at `/admin/`.

```json
{
    "username": "dr_smith",
    "email": "smith@example.com",
    "password": "StrongPass123!",
    "password2": "StrongPass123!",
    "role": "therapist",
    "therapist_profile": {
        "license_number": "LIC-12345",
        "specialization": "Child Anxiety, ADHD",
        "years_of_experience": 8
    }
}
```

---

## Running Tests

Start the development server and test all endpoints using **Postman** or any HTTP client.

```bash
python manage.py runserver
```

Key flows to test:
1. Register a parent and a therapist
2. Login with both accounts and save tokens
3. Create a post as the therapist
4. Follow the therapist as the parent
5. Check the parent's feed — the therapist's post should appear
6. Like the post — check notifications as the therapist
7. Verify the therapist via `/admin/` — check therapist list endpoint

---

## Deployment



### Production checklist

- `DEBUG = False`
- `SECRET_KEY` stored in environment variable, not in code
- `ALLOWED_HOSTS` set to your domain
- Static files collected with `python manage.py collectstatic`
- Database migrated on the server

---

## Admin Panel

Django's built-in admin panel is available at `/admin/`. Use your superuser credentials to log in.

From the admin panel you can:
- View and manage all users, posts, comments
- Verify therapist profiles by checking the `is_verified` flag on their TherapistProfile
- Monitor notifications

---

## Author

Built as part of the Backend Capstone Project — Moringa School, 2026.
