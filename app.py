import os
import random
from operator import itemgetter, attrgetter, methodcaller
from flask import Flask, render_template, redirect, request
import json
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import RadioField
from wtforms import SubmitField
from wtforms import HiddenField
from wtforms import SelectField
from wtforms.validators import InputRequired, Length, DataRequired


app = Flask(__name__)
app.secret_key = os.urandom(40)


class FormRequest(FlaskForm):
    name = StringField("Вас зовут", [InputRequired(message="Необходимо указать имя"),
                                     Length(min=2, max=50, message="Имя %(min)d - %(max)d символов")])
    phone = StringField("Ваш телефон", [InputRequired(message="Необходимо ввести ваш номер телефона"),
                                        Length(max=15, message="Слишком много символов в номере телефона")])
    goal = RadioField('Какая цель занятий?', choices=[("travel", "Для путешествий"), ("study", "Для учебы"),
                                                      ("work", "Для работы"), ("relocate", "Для переезда"),
                                                      ("programming", "Для программирования")], default="study")
    time = RadioField('Сколько времени есть?', choices=[('time1', '1-2 часа в неделю'), ('time2', '3-5 часов в неделю'),
             ('time3', '5-7 часов в неделю'), ('time4', '7-10 часов в неделю')], default="time2")
    submit = SubmitField('Найдите мне преподавателя')



class BookingToTeacher(FlaskForm):
    name = StringField("Вас зовут", [InputRequired(message="Необходимо указать имя"),
                                     Length(min=2, max=50, message="Имя %(min)d - %(max)d символов")])
    phone = StringField("Ваш телефон", [InputRequired(message="Необходимо ввести ваш номер телефона"),
                                        Length(max=15, message="Слишком много символов в номере телефона")])
    submit = SubmitField('Записаться на пробный урок')
    weekday = HiddenField("День недели для записи")
    time = HiddenField("Часы занятий для записи")
    teacher = HiddenField("Id учителя")


class SortTeachers(FlaskForm):
    sort_type = SelectField("Сортировка преподавателей",
                            choices=[("Случайно", "В случайном порядке"),
                                     ("Рейтинг", "Сначала лучшие по рейтингу"),
                                     ("Дорогие", "Сначала дорогие"),
                                     ("Недорогие", "Сначала недорогие")])
    submit = SubmitField('Сортировать')


with open("goals.json", "r", encoding='utf-8') as f:
    goals = json.load(f)
with open("teachers.json", "r", encoding='utf-8') as f:
    teachers = json.load(f)

days_of_week = dict(map(lambda a, b, c: (a, [b, c]), teachers[0]['free'].keys(),
                        ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'],
                        ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']))
goals_pictures = ["⛱", "🏫", "🏢", "🚜", "🎮"]
goals_pict = dict(map(lambda a, b, c, d: (a, [b, c, 'goal' + str(d)]), goals.keys(), goals.values(), goals_pictures,
                      list(range(1, len(goals_pictures) + 1))))
time_have = [('time1', '1-2 часа в неделю'), ('time2', '3-5 часов в неделю'),
             ('time3', '5-7 часов в неделю'), ('time4', '7-10 часов в неделю')]

#FormRequest.goal.choices = [(a, b[0]) for a, b in goals_pict.items()]
#FormRequest.goal.default = FormRequest.goal.choices[0][0]
#FormRequest.time.choices = [[a[0], a[1]] for a in time_have]
#FormRequest.time.default = FormRequest.time.choices[0][0]

@app.route('/')
# здесь будет главная
def render_main():
    return render_template('index.html', teachers=random.sample(teachers, min(6, len(teachers))), goals=goals_pict)


@app.route('/all/', methods=["POST", "GET"])
# здесь будут преподаватели
def render_all():
    form = SortTeachers()
    teachers_sort = teachers[:]
    if request.method == 'POST':
        sort_type = form.sort_type.data
        if sort_type == form.sort_type.choices[0][0]:
            random.shuffle(teachers_sort)
        if sort_type == form.sort_type.choices[1][0]:
            teachers_sort = sorted(teachers_sort, key=lambda a: a["rating"], reverse=True)
        if sort_type == form.sort_type.choices[2][0]:
            teachers_sort = sorted(teachers_sort, key=lambda a: a["price"], reverse=True)
        if sort_type == form.sort_type.choices[3][0]:
            teachers_sort = sorted(teachers_sort, key=lambda a: a["price"])
    return render_template('all.html', teachers=teachers_sort, form=form)


@app.route('/goals/<goal>/')
# здесь будет цель <goal>
def render_goal(goal):
    if goal not in goals.keys():
        return render_template('str_404.html', error='Неверно указана цель обучения'), 404
    teachers_goal = [a for a in teachers if goal in a['goals']]
    return render_template('goal.html', teachers=teachers_goal, goal=goals_pict[goal])


@app.route('/profiles/<int:teacher_id>/')
# здесь будет преподаватель <id учителя>
def render_profile(teacher_id):
    if teacher_id not in range(0, len(teachers)):
        return render_template('str_404.html', error='Неверно указан код преподавателя'), 404
    return render_template('profile.html', teacher=teachers[teacher_id], goals=goals, days_of_week=days_of_week)


@app.route('/request/', methods=["POST", "GET"])
# здесь будет заявка на подбор
def render_request():
    form = FormRequest()
    if form.validate():
        print("Validate")
    if form.validate_on_submit():
        print("form.validate_on_submit():")
    if request.method == "POST":

        print("POST")
        #return redirect('/request_done/')
        goal = goals_pict[form.goal.data][0]
        time = dict(time_have)[form.time.data]
        name = form.name.data
        phone = form.phone.data
        request_records = []
        with open("request.json", "r", encoding='utf-8') as file_t:
            content = file_t.read()
            if len(content) > 0:
                request_records = json.loads(content)
        request_records.append([goal, time, name, phone])
        with open("request.json", "w", encoding='utf-8') as file_t:
            json.dump(request_records, file_t)
        return render_template('request_done.html', request_param=[goal, time, name, phone])
    print("request", request.method)
    #form.goal.choices = [(a, b[0]) for a, b in goals_pict.items()]
    #form.goal.default = form.goal.choices[0][0]
    #form.time.choices = [[a[0], a[1]] for a in time_have]
    #form.time.default = form.time.choices[0][0]
    #form.process()
    return render_template('request.html', form=form)


@app.route('/request_done/', methods=["POST", "GET"])
# заявка на подбор отправлена
def render_request_done():
    form = FormRequest()
    print("/request_done/", form.goal.data)
    #    if not form.validate_on_submit():
    #        return render_template('str_404.html', error='Неверно указана страница'), 404
    goal = goals_pict[form.goal.data][0]
    time = dict(time_have)[form.time.data]
    name = form.name.data
    phone = form.phone.data
    request_records = []
    with open("request.json", "r", encoding='utf-8') as file_t:
        content = file_t.read()
        if len(content) > 0:
            request_records = json.loads(content)
    request_records.append([goal, time, name, phone])
    with open("request.json", "w", encoding='utf-8') as file_t:
        json.dump(request_records, file_t)
    return render_template('request_done.html', request_param=[goal, time, name, phone])


@app.route('/booking/<int:teacher_id>/<day_of_week>/<time_booking>/')
#  здесь будет форма бронирования <id учителя>
def render_booking(teacher_id, day_of_week, time_booking):
    days = [(b, a) for a, b in days_of_week.values()]
    if teacher_id not in range(0, len(teachers)) or day_of_week not in dict(days).keys() or (time_booking + ':00') \
            not in list(teachers[0]["free"].values())[0].keys():
        return render_template('str_404.html', error='Неверно указаны данные бронирования'), 404
    day_booking = [dict(days)[day_of_week], day_of_week]
    form = BookingToTeacher()
    form.weekday.data = day_booking[1]
    form.time.data = time_booking + ':00'
    form.teacher.data = str(teacher_id)
    return render_template('booking.html', teacher=teachers[teacher_id], day_booking=day_booking, form=form)


@app.route('/booking_done/', methods=["POST", "GET"])
#  заявка отправлена
def render_booking_done():
    if request.method != 'POST':
        return render_template('str_404.html', error='Неверно указана страница'), 404
    days = dict([(b[1], [b[0], a]) for a, b in days_of_week.items()])
    form = BookingToTeacher()
    day = days[form.weekday.data][0]
    time = form.time.data
    name = form.name.data
    phone = form.phone.data
    booking_param = [day, time, name, phone]
    booking_records = []
    # teachers[int(form.teacher.data)]['free'][days[form.weekday.data][1]][time] = False
    with open("booking.json", "r", encoding='utf-8') as file_t:
        content = file_t.read()
        if len(content) > 0:
            booking_records = json.loads(content)
    booking_records.append([form.teacher.data, day, time, name, phone])
    with open("booking.json", "w", encoding='utf-8') as file_t:
        json.dump(booking_records, file_t)
    return render_template('booking_done.html', booking_param=booking_param)


@app.errorhandler(404)
def render_not_found(error):
    return render_template('str_404.html', error=error), 404


if __name__ == '__main__':
    app.run(debug=True)
