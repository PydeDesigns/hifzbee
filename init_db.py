from app import create_app, db
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_db(app, max_retries=5, delay=5):
    """Wait for database to be ready"""
    retries = 0
    while retries < max_retries:
        try:
            with app.app_context():
                # Try a simple query
                db.session.execute(text('SELECT 1'))
                logger.info("Database is ready!")
                return True
        except Exception as e:
            retries += 1
            logger.warning(f"Database not ready (attempt {retries}/{max_retries}): {str(e)}")
            if retries < max_retries:
                logger.info(f"Waiting {delay} seconds before retrying...")
                time.sleep(delay)
    
    logger.error("Max retries reached. Database is not available.")
    return False

def init_db():
    try:
        app = create_app()
        
        # Wait for database to be ready
        if not wait_for_db(app):
            logger.error("Could not connect to database after multiple attempts")
            return False

        with app.app_context():
            try:
                # Drop all tables if they exist
                logger.info("Dropping all existing tables...")
                db.drop_all()
                logger.info("Successfully dropped all tables")

                # Create all tables
                logger.info("Creating all tables...")
                db.create_all()
                logger.info("Successfully created all tables")

                # Verify tables were created
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                logger.info("Created tables:")
                for table in tables:
                    logger.info(f"- {table}")
                    columns = [col['name'] for col in inspector.get_columns(table)]
                    logger.info(f"  Columns: {', '.join(columns)}")

                return True

            except SQLAlchemyError as e:
                logger.error(f"Database schema error: {str(e)}")
                raise

    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        logger.exception("Full traceback:")
        raise

    return False

if __name__ == '__main__':
    success = init_db()
    if not success:
        logger.error("Database initialization failed")
        exit(1)
    logger.info("Database initialization completed successfully")
