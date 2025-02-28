from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, DateField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from datetime import datetime

class CreateHatimForm(FlaskForm):
    title = StringField('Hatim Title', validators=[
        DataRequired(),
        Length(min=3, max=100)
    ])
    target_completion_date = DateField('Target Completion Date', 
        validators=[DataRequired()],
        format='%Y-%m-%d'
    )
    is_public = BooleanField('Make this Hatim public')
    auto_join = BooleanField('Allow friends to join automatically')
    submit = SubmitField('Create Hatim')

    def validate_target_completion_date(self, field):
        if field.data < datetime.now().date():
            raise ValidationError('Target completion date must be in the future')

class JoinHatimForm(FlaskForm):
    juz_selection = SelectMultipleField('Select Juz to Read',
        choices=[(str(i), f'Juz {i}') for i in range(1, 31)],
        validators=[DataRequired()]
    )
    submit = SubmitField('Join Hatim')

class UpdateProgressForm(FlaskForm):
    completed_juz = SelectMultipleField('Mark Completed Juz',
        choices=[(str(i), f'Juz {i}') for i in range(1, 31)],
        validators=[DataRequired()]
    )
    submit = SubmitField('Update Progress')
