import os
from tabnanny import check
from flask import Flask, render_template, request, escape
from vsearch import search4letters
from werkzeug.utils import secure_filename

from DBcm import UseDatabase


list_album_item=[]
list_album_item_exists=[]
class AlbumItem:
    def __init__(self,name,desc,coast):
        self.name=name
        self.desc=desc
        self.coast=coast

UPLOAD_FOLDER = 'auth_admin/static/img'


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'vsearch',
                          'password': 'vsearchpasswd',
                          'database': 'vsearchlogDB', }


def signup_user(req: 'flask_request'):
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """insert into username
                  (name, login, email, password, ip, browser_string)
                  values
                  (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(_SQL, (req.form['username'],
                              "login",
                              req.form['useremail'],
                              req.form['userpasswd'],
                              req.remote_addr,
                              req.user_agent.browser,
                              ))


def log_request(req: 'flask_request', res: str) -> None:
    """Log details of the web request and the results."""

    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """insert into log
                  (phrase, letters, ip, browser_string, results)
                  values
                  (%s, %s, %s, %s, %s)"""
        cursor.execute(_SQL, (req.form['phrase'],
                              req.form['letters'],
                              req.remote_addr,
                              req.user_agent.browser,
                              res, ))


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    """Extract the posted data; perform the search; return results."""
    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Here are your results:'
    results = str(search4letters(phrase, letters))
    log_request(request, results)
    return render_template('results.html',
                           the_title=title,
                           the_phrase=phrase,
                           the_letters=letters,
                           the_results=results,)


@app.route('/signup_user', methods=['POST'])
def sign_up() -> 'html':
    """Extract the posted data; perform the search; return results."""
    name_value = request.form['username']
    email_value = request.form['useremail']
    passwd_value = request.form['userpasswd']
    signup_user(request)
    return render_template('signup_successfull.html',
                           the_title="Sign up is done successfull!",
                           the_user_name=name_value,
                           the_user_email=email_value,
                           the_user_passwd=passwd_value)


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    """Display this webapp's HTML form."""
    return render_template('entry.html',
                           the_title='Welcome to search4letters on the web!')


@app.route('/contactus')
def contact_us() -> 'html':
    """Display this webapp's HTML form."""
    return render_template('contactus.html',
                           the_title='Welcome to search4letters on the web!')


@app.route('/viewlog')
def view_the_log() -> 'html':
    """Display the contents of the log file as a HTML table."""
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select phrase, letters, ip, browser_string, results
                  from log"""
        cursor.execute(_SQL)
        contents = cursor.fetchall()
    titles = ('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')
    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_titles=titles,
                           the_data=contents,)


@app.route('/viewlog_users')
def view_the_log_users() -> 'html':
    """Display the contents of the log file as a HTML table."""
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select name, email, ip, browser_string
                  from username"""
        cursor.execute(_SQL)
        contents = cursor.fetchall()
    titles = ('Name', 'Email', 'Remote_addr', 'User_agent')
    return render_template('viewlog_users.html',
                           the_title='List Users',
                           the_row_titles=titles,
                           the_data=contents)


@app.route('/signin_users', methods=['POST'])
def signin_users() -> 'html':
    """Display the contents of the log file as a HTML table."""
    with UseDatabase(app.config['dbconfig']) as cursor:        
        cursor.execute("select email from username")
        contents_email = cursor.fetchall()
    with UseDatabase(app.config['dbconfig']) as cursor:        
        cursor.execute("select password from username")
        contents_passwd = cursor.fetchall()
    
    email_value = request.form['useremail']
    passwd_value = request.form['userpasswd']

# check valid input signin data
    if email_value==contents_email[-1][-1] and passwd_value==contents_passwd[-1][-1]:
        return render_template('admin.html',
                           the_title='Admin page',                           
                           the_name_user="name",
                           nameU=contents_email[-1][-1],
                           passwdU=contents_passwd[-1][-1],
                           )
    else:
        return render_template('admin.html',
                           the_title='Admin page',                           
                           the_name_user="name",
                           nameU=contents_email,
                           passwdU=contents_passwd,
                           )
# end check valid input signin data

@app.route('/admin')
def admin() -> 'html':
    """Display the contents of the log file as a HTML table."""    
    titles = ('$user@root')
    return render_template('admin.html')


@app.route('/signin')
def signin() -> 'html':
    """Display the contents of the log file as a HTML table."""    
    titles = ('$user@root')
    return render_template('signin.html')


@app.route('/signup')
def signup_withoute() -> 'html':
    """Display the contents of the log file as a HTML table."""    
    titles = ('$user@root')
    return render_template('signup.html')


@app.route('/logout')
def logout() -> 'html':
    """Display the contents of the log file as a HTML table."""    
    titles = ('$user@root')
    return render_template('entry.html')


@app.route('/order')
def order_page() -> 'html':
    """Display the contents of the log file as a HTML table."""        
    return render_template('order.html')


@app.route('/album')
def album() -> 'html':
    """
    with UseDatabase(app.config['dbconfig']) as cursor:        
        cursor.execute("select name from items")
        name_item = cursor.fetchall()
    with UseDatabase(app.config['dbconfig']) as cursor:        
        cursor.execute("select features from items")
        desc_item = cursor.fetchall()
    with UseDatabase(app.config['dbconfig']) as cursor:        
        cursor.execute("select coast from items")
        coast_item = cursor.fetchall()
    
    with UseDatabase(app.config['dbconfig']) as cursor:        
        cursor.execute("select id from items where id=(select max(id) from items)")
        id_item = cursor.fetchall()        
    with UseDatabase(app.config['dbconfig']) as cursor:                        
        cursor.execute("select name from items")
        old_name = cursor.fetchall()
    with UseDatabase(app.config['dbconfig']) as cursor:                        
        cursor.execute("select features from items")
        old_desc = cursor.fetchall()
    with UseDatabase(app.config['dbconfig']) as cursor:                        
        cursor.execute("select coast from items")
        old_coast = cursor.fetchall()
    
    n=id_item
    while(n!=0):        
        exist_name=old_name[n]
        exist_desc=old_desc[n]
        exist_coast=old_coast[n]
        old_item=AlbumItem(exist_name,exist_desc,exist_coast)
        n=-1
    
    list_album_item.append(old_item)
    """
    return render_template('album.html',list_item_total=list_album_item)


@app.route('/add_item', methods=['POST'])
def add_item() -> 'html':
    name_item = request.form['add_item']
    desc_item = request.form['desc_item']
    coast_item = request.form['coast_item']
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """insert into items
                  (name, features, coast)
                  values
                  (%s, %s, %s)"""
        cursor.execute(_SQL, (request.form['add_item'],
                              request.form['desc_item'],
                              request.form['coast_item']                              
                              ))
    
    new_item=AlbumItem(name_item,desc_item,coast_item)
    list_album_item.append(new_item)
    
    return render_template('admin.html', num_item=len(list_album_item))


@app.route('/upload', methods = ['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files['File']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "File saved successfully"


if __name__ == '__main__':
    app.run(debug=True)
