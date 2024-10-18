Debrief -- the news aggregator

## Overview

Debrief is a news aggregator that uses AI to aggregate the expositions found in news articles and provide insights into the diversity of reporting.

## Features

- Summarize news articles as a list of facts
- Rank facts by newsworthiness for easy skimming
- Search for news articles
- Measures various biases and errors of individual reporters and news outlets

## How to use

The home page acts similarly to a social media feed, but instead of showing you posts from your friends, it shows you events which are populated by multiple news outlets covering the same story.

Clicking on an event will show you the facts as reported by each news outlet.

An event consists of:
- A title
- A list of facts (ordered by newsworthiness)
- Citation(s) for each fact, which are links to the original news articles

## Development

Debrief is built with Django, React, and Postgres.

## Structure

- `backend/`: Django project
- `frontend/`: React project
- `data/`: Postgres database
- `scripts/`: Scripts for data collection and processing
- `media/`: Media files

## Setup and Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- PostgreSQL

### Backend Setup
1. Navigate to the backend directory:
   ```
   cd backend
   ```
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   Create a `.env` file in the `backend` directory with the following content:
   ```
   DEBUG=True
   SECRET_KEY=your_secret_key
   DATABASE_URL=postgres://user:password@localhost:5432/debrief
   ```
5. Run migrations:
   ```
   python manage.py migrate
   ```
6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```
   cd frontend
   ```
2. Install dependencies:
   ```
   npm install
   ```

### Database Setup
1. Create a PostgreSQL database named `debrief`
2. Update the `DATABASE_URL` in the `.env` file with your database credentials

## Running the Application

### Backend
1. Activate the virtual environment (if not already activated)
2. Run the Django development server:
   ```
   python manage.py runserver
   ```

### Frontend
1. In a new terminal, navigate to the frontend directory
2. Start the React development server:
   ```
   npm start
   ```

The application should now be running. Access the backend at `http://localhost:8000` and the frontend at `http://localhost:3000`.

## Populating with Dummy Data

To populate the database with dummy events for testing:

1. Create a management command in the Django app:
   ```
   python manage.py create_dummy_data
   ```
2. Run the command:
   ```
   python manage.py create_dummy_data
   ```

This will add a few sample events, news outlets, and articles to get you started.
