"""Web application for XFormTest

http://xform-test.pma2020.org
"""
import platform
import os
import flask
from flask import Flask, render_template, request
# noinspection PyProtectedMember
from static_methods import _run_background_process
from werkzeug.utils import secure_filename

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

is_windows = platform.system() == 'Windows'
path_char = '\\' if is_windows else '/'


@app.route('/', methods=['GET', 'POST'])
def index():
    if flask.request.method == 'GET':
        return render_template('index.html')
    else:
        try:
            file = request.files['xform-file']
            filename = secure_filename(file.filename)
            upload_folder = basedir + path_char + 'temp_uploads'
            file_path = os.path.join(upload_folder, filename)

            if os.path.exists(file_path):
                os.remove(file_path)

            try:
                file.save(file_path)
            except FileNotFoundError:
                os.mkdir(upload_folder)
                file.save(file_path)

            options_list = request.form.getlist('options[]')
            options = " ".join(options_list)

            command = "python -m qtools2.convert "+options+" "+file_path
            stdout, stderr = _run_background_process(command)
            return render_template('index.html', stderr=stderr, stdout=stdout)

        except Exception as err:
            msg = 'An unexpected error occurred:\n\n' + str(err)
            return render_template('index.html', stderr=msg)

@app.route('/qtools/<string:filename>')
def xform_test(filename):
    """ret = _run_terminal_command('java -jar xform-test-0.3.0.jar
    temp_uploads\\MultipleTestCases.xml')
    print('return value', ret)"""
    command = 'java -jar xform-test-0.3.0.jar temp_uploads'+path_char+filename
    try:
        stdout, stderr = _run_background_process(command) if not is_windows else _run_windows_process(command)
        # flash(out, "warning")
        return render_template('index.html', error=stderr, out=stdout)
    except Exception as err:
        # TODO: @bciar: I'm getting an IDE error "unresolved attribute for
        # base class Exception" - Joe 2018/11/06
        error = err if not is_windows else err.stderr.decode("utf-8")
        return render_template('index.html', error=err)


if __name__ == '__main__':
    app.run(debug=True)