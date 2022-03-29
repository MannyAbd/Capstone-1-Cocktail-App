from app import *


@app.route('/drinks/a')
def drink_a():
    res = requests.get(f"{BASE_URL}", params={'api_key': api_key, 'f': 'a'})
    val = res.json()
    a_drinks = val["drinks"]
    return render_template("by_letter.html",a_drinks=a_drinks)
    