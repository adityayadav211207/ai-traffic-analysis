import os

from flask import Flask, render_template

from routes.auth import auth
from routes.dashboard import dashboard
from routes.upload import upload
from routes.manage_users import manage_users
from routes.dataset_management import dataset_management
from routes.reports import report
from routes.analytics import analytics
from routes.ai import ai
from routes.settings import settings
from routes.prediction import prediction
from routes.api import api


app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "trafficvision-development-key")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# =====================================
# Register Blueprints
# =====================================

app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(upload)
app.register_blueprint(manage_users)
app.register_blueprint(dataset_management)
app.register_blueprint(report)
app.register_blueprint(analytics)
app.register_blueprint(ai)
app.register_blueprint(settings)
app.register_blueprint(prediction)
app.register_blueprint(api)

# =====================================
# Home
# =====================================

@app.route("/")
def home():

    return render_template("index.html")


# =====================================
# Run App
# =====================================

if __name__ == "__main__":

    app.run(debug=True, host="127.0.0.1", port=5000)