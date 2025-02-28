# HifzBee 🐝

HifzBee is a collaborative Quran memorization platform that helps Muslims organize and participate in group Hatims (complete Quran readings). The application features a beautiful honeycomb-inspired design and makes it easy to join or create Hatims.

## Features

- 🍯 Beautiful honeycomb layout for Juz selection
- 📱 Mobile-first, responsive design
- 👥 Multiple authentication options:
  - Email/Password login
  - Google Sign-in
  - Guest access with local progress saving
- 🤝 Collaborative Hatim organization:
  - Create new Hatims
  - Join existing Hatims
  - Select multiple Juz
  - Track completion progress
- 🎨 Bee-themed visual design with yellow-dominant color scheme

## Technology Stack

- Backend: Flask (Python)
- Database: SQLAlchemy with SQLite
- Frontend: HTML, CSS, JavaScript
- Authentication: Flask-Login, Google OAuth
- Styling: Bootstrap with custom CSS

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hifzbee.git
cd hifzbee
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

4. Initialize the database:
```bash
python init_db.py
```

5. Run the development server:
```bash
flask run
```

## Deployment

The application is configured for deployment on Render. Simply connect your GitHub repository to Render, and it will automatically deploy using the configuration in `render.yaml`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
