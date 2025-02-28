from app import create_app, db
from app.models import User, Hatim, HatimParticipation, Friendship, Achievement

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Hatim': Hatim,
        'HatimParticipation': HatimParticipation,
        'Friendship': Friendship,
        'Achievement': Achievement
    }

if __name__ == '__main__':
    app.run(debug=True)
