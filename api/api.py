from context import bgchof
import flask
from datetime import date, datetime

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route("/", methods=["GET"])
def home():
    return "<h1>Bulgarian Christian Orthodox Fasting</h1><p>This site is a prototype API for bgchof project.</p>"


# a route to return the message for a specific date
@app.route("/api/v1/getMsgForDate", methods=["GET"])
def api_msgForDate():
    if "theDate" in flask.request.args:
        theDate = date.fromisoformat(flask.request.args["theDate"])
        return bgchof.getFastingStatusForDate(theDate)
    # elif: #define other input cases
    else:
        inputDate = date.today()
        return bgchof.getFastingStatusForDate(inputDate)


# a route to return the value for a specific date

app.run()
