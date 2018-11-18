# -*- coding: utf-8 -*-

from wtforms import IntegerField, SelectField, Form
from wtforms.validators import DataRequired


class MainForm(Form):
    people = [
        ("Ania", "Ania"),
        ("Anita", "Anita"),
        ("Karolina", "Karolina"),
        ("Klaudia", "Klaudia"),
        ("Przemek", "Przemek"),
        ("Sylwia", "Sylwia")
    ]
    name = SelectField('Jak masz na imię?', choices=people, validators=[DataRequired()])
    pin = IntegerField('Podaj kod pin:', validators=[DataRequired()])
