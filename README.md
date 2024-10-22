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
   ```
   Run the command:
   ```
   python manage.py create_dummy_data
   ```

This will add a few sample events, news outlets, and articles to get you started.

## To Do
- Add scrapers for news outlets
- Add merging of articles
   - Add a way to check if articles are about the same thing
   - Add a way to merge them if they are
- Add a search function for events
- Add a recommendation system for events
- Add a bias and error detection system
   - Add a way to rate the bias and error of individual reporters
   - Add a way to rate the bias and error of individual news outlets
   - Add a way to see the bias and error of individual news outlets
- Add backend admin dashboard and control panel
- Update styles: make it look nicer
- Add a way to filter events by date, topic, etc.
- Add a way to filter news outlets by country, political leaning, etc.
- Add a way to filter reporters by country, political leaning, etc.