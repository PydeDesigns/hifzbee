from app import create_app, db
import logging
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    try:
        app = create_app()
        with app.app_context():
            # Test database connection
            try:
                # Try a simple query
                db.session.execute(text('SELECT 1'))
                logger.info("Successfully connected to database!")
            except Exception as e:
                logger.error(f"Failed to connect to database: {str(e)}")
                raise

            # Check if tables exist
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if not existing_tables:
                logger.info("No tables found. Creating database tables...")
                db.create_all()
                logger.info("Database tables created successfully!")
            else:
                logger.info("Existing tables found:")
                for table in existing_tables:
                    logger.info(f"- {table}")
                
                # Drop and recreate all tables to ensure schema is up to date
                logger.info("Updating database schema...")
                db.drop_all()
                db.create_all()
                logger.info("Database schema updated successfully!")
                
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        logger.exception("Full traceback:")
        raise

if __name__ == '__main__':
    init_db()
