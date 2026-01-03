# GlobeTrotter - Travel Planning Application

GlobeTrotter is a travel planning application that allows users to create itineraries, manage trip budgets, and view their travel plans on an interactive calendar.

## Project Structure

The project is organized into two main directories:

- **`backend/`**: Contains the server-side logic, database models, and instance data.
    - `app.py`: The main Flask application entry point.
    - `models.py`: Database schema definitions using SQLAlchemy.
    - `instance/`: Contains the SQLite database file (`sarvn.db`).
- **`frontend/`**: Contains client-side assets and templates.
    - `templates/`: HTML templates for the application.

## Key Features

- **User Authentication**: Secure registration and login system.
- **Trip Management**: Create and manage multiple trips with dates and descriptions.
- **Itinerary Builder**: Add and organize trip sections (activities) within a trip.
- **Interactive Calendar**: View your trip timeline and activities on a monthly calendar grid.
- **Budget Tracking**: Manage and monitor your trip expenses.
- **Search & Discovery**: Find and explore trips planned by other users.

## Prerequisites

- Python 3.x
- Flask
- Flask-SQLAlchemy

## Installation

1. Clone the repository.
2. Install the required dependencies:
   ```bash
   pip install flask flask-sqlalchemy
   ```

## Running the Application

To start the development server, run the following command from the project root:

```bash
python backend/app.py
```

The application will be accessible at `http://127.0.0.1:5000/`.

## Deployment Note

When deploying, ensure that the `template_folder` path in `backend/app.py` is correctly configured to point to the `frontend/templates` directory.
