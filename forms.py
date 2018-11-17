from wtforms import IntegerField, SelectField, Form
from wtforms.validators import Required


class MainForm(Form):
    people = [
        ("Ania", "Ania"),
        ("Anita", "Anita"),
        ("Karolina", "Karolina"),
        ("Klaudia", "Klaudia"),
        ("Przemek", "Przemek")
    ]
    name = SelectField('Jak masz na imię?', choices=people)#, validators=[required()])
    pin = IntegerField('Podaj kod pin:')#, validators=[required()])
