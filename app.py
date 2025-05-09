from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import pandas as pd
from io import BytesIO
import time
import os

app = Flask(__name__)
app.secret_key = "Harshidontlikeexcel"

# Petty error messages now with CSV awareness
ERROR_MESSAGES = {
    "file_missing": "🙄 Forgot files? My morning coffee remembers its creamer.",
    "key_error": "🤷‍♀️ Column not found. Try looking between 'Monday Blues' and 'Friday Fatigue'.",
    "general_error": "💥 System overload. Like your brain before that bath.",
    "empty_file": "📦 File emptier than your coworker's promises."
}

def read_file(file):
    """Smart file reader that handles both Excel and CSV"""
    filename = file.filename.lower()
    
    if filename.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file)
    elif filename.endswith('.csv'):
        return pd.read_csv(file)
    else:
        raise ValueError("Unsupported file type")

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            # Get files with relaxed standards
            file1 = request.files.get("file1")
            file2 = request.files.get("file2")
            
            if not (file1 and file2):
                flash(ERROR_MESSAGES["file_missing"], "error")
                return redirect(url_for("home"))
            
            # Dramatic pause for effect
            time.sleep(1.5)
            
            # Read files with our new chill reader
            df1 = read_file(file1)
            df2 = read_file(file2)
            
            # Validation because we care (unlike some people)
            if df1.empty or df2.empty:
                flash(ERROR_MESSAGES["empty_file"], "error")
                return redirect(url_for("home"))
            
            key_column = "ID"  # ⚠️ CHANGE THIS TO YOUR KEY COLUMN
            comparison = df1.merge(df2, on=key_column, suffixes=('_A', '_B'), how="outer")
            comparison["Status"] = comparison.apply(
                lambda row: "✅ Match" if str(row["Amount_A"]) == str(row["Amount_B"]) else "❌ Mismatch",
                axis=1
            )
            
            # Save to buffer
            output = BytesIO()
            comparison.to_excel(output, index=False)
            output.seek(0)
            
            return send_file(
                output,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name="Reconciliation_Report.xlsx"
            )
            
        except KeyError:
            flash(ERROR_MESSAGES["key_error"], "error")
        except Exception as e:
            flash(f"{ERROR_MESSAGES['general_error']} Details: {str(e)}", "error")
        return redirect(url_for("home"))
    
    return render_template("index.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", 
        message="🚀 Page vanished like your will to live on Mondays."
    ), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", 
        message="🤖 My circuits overloaded—just like your inbox."
    ), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, use_reloader=True)