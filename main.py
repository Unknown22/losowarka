# -*- coding: utf-8 -*-

from flask import Flask, redirect, url_for, render_template, request
from sql_handler import create_connection, prepare_schema, prepare_start_data, check_if_person_got_reminder_key, \
    get_person_and_reminder_pin, get_person_pin, get_person_reminder_pin, get_person_to_gift
from forms import MainForm

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def home():
    form = MainForm(request.form)
    if request.method == "POST":
        if form.validate():
            conn = create_connection()
            app.logger.info("Preparing schema")
            prepare_schema(conn)
            app.logger.info("Inserting init data")
            prepare_start_data(conn)
            if request.form['action'] == "Potwierdź":
                if get_person_pin(conn, form.name.data) != int(form.pin.data):
                    return "Niepoprawny pin"
                if check_if_person_got_reminder_key(conn, form.name.data) == 0:
                    person, reminder_pin = get_person_and_reminder_pin(conn, form.name.data)
                    conn.close()
                    return render_template("success.html", person=person, reminder_pin=reminder_pin)
                else:
                    conn.close()
                    return "Już losowałeś/aś. Użyj opcji przypomnij podając pin otrzymany po losowaniu."
            else:
                if get_person_reminder_pin(conn, form.name.data) != int(form.pin.data):
                    conn.close()
                    return "Niepoprawny pin"
                person_to_gift = get_person_to_gift(conn, form.name.data)
                conn.close()
                return "Przypomnienie: prezent od Ciebie otrzyma <b>{person}</b>".format(**{"person": person_to_gift})

            conn.close()
    return render_template('main.html', form=form)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'kakadu'
    app.run(port=8080, debug=True)
