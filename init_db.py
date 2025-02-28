from app import create_app, db
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    try:
        app = create_app()
        with app.app_context():
            # Check if tables exist
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if not existing_tables:
                logger.info("Creating database tables...")
                db.create_all()
                logger.info("Database tables created successfully!")
            else:
                logger.info("Database tables already exist:")
                for table in existing_tables:
                    logger.info(f"- {table}")
                
                # Ensure tables are up to date
                logger.info("Ensuring tables are up to date...")
                db.create_all()
                logger.info("Database schema is up to date!")
                
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        logger.exception("Full traceback:")
        raise

if __name__ == '__main__':
    init_db()
