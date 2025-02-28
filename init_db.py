from app import create_app, db
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_db():
    try:
        app = create_app()
        logger.info(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI'].replace('://', '://<hidden>:<hidden>@')}")
        
        with app.app_context():
            # Test database connection
            try:
                db.session.execute(text('SELECT 1'))
                logger.info("Successfully connected to database!")
            except OperationalError as e:
                logger.error(f"Failed to connect to database: {str(e)}")
                raise

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

            except SQLAlchemyError as e:
                logger.error(f"Database schema error: {str(e)}")
                raise

    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        logger.exception("Full traceback:")
        raise

if __name__ == '__main__':
    init_db()
