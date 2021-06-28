import MySQLdb
from flask import *
from flask_mysqldb import MySQL
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from csv import writer

# from model import *
app = Flask(__name__, template_folder="template", static_url_path='/static')

app.secret_key = 'abcdef ghijkl mnopqr stuvw xyz'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'palak'
app.config['MYSQL_DB'] = 'MovieSpy'

mysql = MySQL(app)

test = pd.read_csv('FINAL_MOVIE_TABLE.csv')


def create_sim():
    test = pd.read_csv('FINAL_MOVIE_TABLE.csv')
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(test['comb'])
    sim = cosine_similarity(count_matrix)
    return test, sim


def rcmd(m):
    m = m.lower()
    try:
        test.head()
    except:
        test, sim = create_sim()
    i = test.loc[test['movie_title'] == m].index[0]

    lst = list(enumerate(sim[i]))

        # sorting this list in decreasing order based on the similarity score
    lst = sorted(lst, key=lambda x: x[1], reverse=True)

        # taking top 1- movie scores
        # not taking the first index since it is the same movie
    lst = lst[1:11]
        # making an empty list that will containg all 10 movie recommendations
    l = []
    for i in range(len(lst)):
        a = lst[i][0]
        l.append(test['movie_title'][a])
    return l


def searchHelper(year, name):
    name = name.lower()
    test1 = pd.read_csv('FINAL_MOVIE_TABLE.csv')
    t = test1.loc[(test1['year'] == year)]

    t1 = t.loc[(t['director_name'] == name)]

    l = t1['movie_title'].tolist()
    return l


@app.route('/', methods={'GET', 'POST'})
def home():
    return render_template('homepage.html')


@app.route('/userportal')
def userportal():
    if 'loggedin' in session:
        return render_template('userportal.html')
    else:
        return redirect(url_for('user'))


@app.route('/user', methods={'GET', 'POST'})
def user():
    msg = ''
    if request.method == 'POST' and 'user_id' in request.form and 'upwd' in request.form:
        uid = request.form['user_id']
        pwd = request.form['upwd']
        # Now, check if account exists in database
        curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curr.execute("SELECT * FROM user where user_id = %s", (uid, ))
        account = curr.fetchone()

        if pwd != account["upwd"] and len(pwd) != 0:
            flash("Incorrect User_id/Password..!!!", "error")
        elif account and pwd == account["upwd"]:
            session['loggedin'] = True
            session['id'] = account['user_id']
            session['password'] = account['upwd']
            return redirect(url_for('userportal'))
        elif request.form['pass'] == 'pass':
            return redirect(url_for('ChangePasswordUser', uid=uid))
    return render_template('userLogIn.html')


@app.route('/user', methods={'GET', 'POST'})
@app.route('/user/register', methods={'GET', 'POST'})
def register():
    msg = ''
    if request.method == "POST" and 'user_id' in request.form and 'upwd' in request.form and 'ucnfrmpwd' in request.form:
        id = request.form['user_id']
        pwd = request.form['upwd']
        cpwd = request.form['ucnfrmpwd']
        ques = request.form['questions']
        ans = request.form['answer']
        curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curr.execute("SELECT * FROM user where user_id = %s and upwd = %s", (id, pwd,))
        account = curr.fetchone()
        if account:
            flash("Account Already Exist...!!!", "error")
        elif pwd != cpwd:
            flash("Password doesn't match..!!!", "error")
        else:
            curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curr.execute("INSERT INTO USER(user_id,upwd,question,answer) VALUES (%s,%s,%s,%s) ", (id, pwd, ques, ans,))
            mysql.connection.commit()
            return redirect(url_for('user'))
    return render_template('userRegister.html')


@app.route('/user', methods={'GET', 'POST'})
@app.route('/user/<uid>', methods={'GET', 'POST'})
def ChangePasswordUser(uid):
    curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curr.execute("SELECT * FROM user WHERE user_id = %s", (uid,))
    account = curr.fetchone()
    ques = account["question"]
    if request.method == 'POST' and 'pwd' in request.form and 'confirm_pwd' in request.form and 'answer' in request.form:
        pwd = request.form['pwd']
        cn_pwd = request.form['confirm_pwd']
        ans = request.form['answer']
        curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curr.execute("SELECT * FROM user WHERE user_id = %s", (uid, ))
        account = curr.fetchone()
        if pwd == cn_pwd and ans == account["answer"]:
            curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curr.execute("UPDATE user SET upwd = %s where user_id = %s", (pwd, uid, ))
            mysql.connection.commit()
            return redirect(url_for('user'))
        elif pwd != cn_pwd:
            flash("Password Doesn't Match", "error")
        else:
            flash("Invalid Security Answer", "error")
    return render_template('ChangePasswordUser.html', value=ques)


@app.route('/admin', methods={'GET', 'POST'})
def admin():
    if request.method == 'POST' and 'admin_id' in request.form and 'apwd' in request.form:
        id = request.form['admin_id']
        pwd = request.form['apwd']
        curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curr.execute("SELECT * FROM admin WHERE admin_id = %s", (id, ))
        account = curr.fetchone()
        if pwd != account["apwd"] and len(pwd) != 0:
            flash("Incorrect Admin_id/Password..!!!", "error")
        elif account and pwd == account["apwd"]:
            session['loggedin'] = True
            session['id'] = account['admin_id']
            session['password'] = account['apwd']
            return redirect(url_for('adminportal'))
        elif request.form['pass'] == 'pass':
            return redirect(url_for('ChangePasswordAdmin', aid=id))
    return render_template('adminLogIn.html')


@app.route('/admin', methods={'GET', 'POST'})
@app.route('/admin/<aid>', methods={'GET', 'POST'})
def ChangePasswordAdmin(aid):
    curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curr.execute("SELECT * FROM admin WHERE admin_id = %s", (aid,))
    account = curr.fetchone()
    ques = account["question"]
    if request.method == 'POST' and 'pwd' in request.form and 'confirm_pwd' in request.form and 'answer' in request.form:
        pwd = request.form['pwd']
        cn_pwd = request.form['confirm_pwd']
        ans = request.form['answer']
        curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curr.execute("SELECT * FROM admin WHERE admin_id = %s", (aid, ))
        account = curr.fetchone()
        if pwd == cn_pwd and ans == account["answer"]:
            curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curr.execute("UPDATE admin SET apwd = %s where admin_id = %s", (pwd, aid, ))
            mysql.connection.commit()
            return redirect(url_for('admin'))
        elif pwd != cn_pwd:
            flash("Password Doesn't Match", "error")
        else:
            flash("Invalid Security Answer", "error")
    return render_template('ChangePasswordUser.html', value=ques)


@app.route('/viewUser')
def viewUser():
    curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curr.execute("SELECT * FROM user")
    account = curr.fetchall()
    if account:
        return render_template('viewUser.html', value=account)
    return render_template('viewUser.html')


@app.route('/viewAdmin')
def viewAdmin():
    curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curr.execute("SELECT * FROM admin")
    account = curr.fetchall()
    if account:
        return render_template('viewAdmin.html', value=account)
    return render_template('viewAdmin.html')


@app.route('/viewMovies')
def viewMovies():
    test = pd.read_csv('FINAL_MOVIE_TABLE.csv', header=0)
    val = test.values.tolist()
    return render_template('viewMovies.html', value=val)


@app.route('/adminportal')
def adminportal():
    if 'loggedin' in session:
        return render_template('adminportal.html')
    else:
        return redirect(url_for('admin'))


@app.route('/admin', methods={'GET', 'POST'})
@app.route('/admin/register', methods={'GET', 'POST'})
def adminRegister():
    if request.method == "POST" and "admin_id" in request.form and "apwd" in request.form and "acnfrmpwd" in request.form and "key" in request.form:
        id = request.form['admin_id']
        pwd = request.form['apwd']
        cpwd = request.form['acnfrmpwd']
        akey = request.form['key']
        ques = request.form['questions']
        ans = request.form['answer']
        curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curr.execute("SELECT * FROM admin WHERE admin_id = %s and apwd = %s", (id, pwd,))
        account = curr.fetchone()
        if account:
            flash("Account Already Exist..!!!", "error")
        elif pwd != cpwd:
            flash("Password doesn't match..!!!", "error")
        elif akey != "12345abc":
            flash("Incorrect Confirmation Key..!!!", "error")
        else:
            curr = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            curr.execute("INSERT INTO admin(admin_id,apwd,question,answer) VALUES (%s,%s,%s,%s) ", (id, pwd, ques, ans, ))
            mysql.connection.commit()
            return redirect(url_for('admin'))
    return render_template('adminRegister.html')


@app.route('/<person>')
def access(person):
    if person == 'User':
        return redirect(url_for('user'))
    else:
        return redirect(url_for('admin'))


@app.route('/addMovie', methods={'GET', 'POST'})
def addMovie():
    if request.method == 'POST' and request.form['action'] == 'add' and 'movie_title' in request.form and 'movie_year' in request.form and 'genre' in request.form and 'director_name' in request.form and 'actor_1_name' in request.form and 'actor_2_name' in request.form and 'actor_3_name' in request.form:
        title = request.form['movie_title']
        year1 = request.form['movie_year']
        genre = request.form['genre']
        director = request.form['director_name']
        actor1 = request.form['actor_1_name']
        actor2 = request.form['actor_2_name']
        actor3 = request.form['actor_3_name']
        year = int(year1)
        comb = actor1+" "+actor2+" "+actor3+" "+director+" "+genre+" "
        test.loc[len(test.index)] = [year, director, actor1, actor2, actor3, genre, title, comb]
        test.to_csv('FINAL_MOVIE_TABLE.csv', index=False)
        return redirect(url_for('recommend'))
    return render_template('addmovie.html')


@app.route('/recommend', methods={'GET', 'POST'})
def recommend():
    if request.method == 'POST':
        if request.form['action'] == 'get' and 'movie_title' in request.form:
            m = request.form['movie_title']
            if len(m) != 0:
                return redirect(url_for('predict', movie=m))
        elif request.form['action'] == 'portal':
            return redirect(url_for('userportal'))
    return render_template('recommendation.html')


@app.route('/search', methods={'GET', 'POST'})
def search():
    if request.method == 'POST':
        if 'year' in request.form and 'director' in request.form:
            year = request.form['year']
            dir = request.form['director']
            return redirect(url_for('searched_movies', y=year, d=dir))
    return render_template('search.html')


@app.route('/search')
@app.route('/search/searched_movies/<y>/<d>')
def searched_movies(y, d):
    r = list()
    year = int(y)
    r = searchHelper(year, d)
    if len(r) == 0:
        flash("No movie by this director in given year exist in our database", "error")
    else:
        d = d.upper()
        return render_template('searched_movies.html', year=year, name=d, lst=r)
    return render_template('searched_movies.html', year=year, name=d)


@app.route('/recommend')
@app.route('/recommend/predict/<movie>')
def predict(movie):
    r = list()
    test = pd.read_csv('FINAL_MOVIE_TABLE.csv')
    if movie not in test['movie_title'].unique():
        flash("Sorry !!! The Movie doesn't exist in our database.You Can Add it in our database.", "error")
    else:
        r = rcmd(movie)
        movie = movie.upper()
        return render_template('predict.html', movie=movie, r=r)
    return render_template('predict.html', movie=movie)

if __name__ == '__main__':
    app.run(debug=True)
