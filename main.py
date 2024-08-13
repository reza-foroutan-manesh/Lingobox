import os

from flask import flash, request, url_for, render_template, redirect, Flask
import requests
from languages import languages, native_names

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')

os.environ.get('X-RapidAPI-Key')
URL = "https://microsoft-translator-text.p.rapidapi.com"

HEADERS = {
    "content-type": "application/json",
    "X-RapidAPI-Key": os.environ.get('X-RapidAPI-Key'),
    "X-RapidAPI-Host": "microsoft-translator-text.p.rapidapi.com"
}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/swap', methods=['GET', 'POST'])
def swap():
    if request.method == 'POST':
        action = request.form.get('action')
        if not action == 'TRANSLATE':
            item1 = request.form.get('select1')
            item2 = request.form.get('select2')
            box1 = request.form.get('txt-to-tr')
            box2 = request.form.get('tr')
            return render_template('translator.html', languages=native_names, anchor='translator', item1=item1, item2=item2,
                                   box1=box1, box2=box2, swap=True)
        elif action == 'TRANSLATE':
            try:
                lan_1 = ''
                lan_2 = ''
                textarea_1 = request.form.get('txt-to-tr')
                if textarea_1 == "":
                    flash('Box cannot be empty')
                    return redirect(url_for('swap'))

                for (key, value) in languages['translation'].items():
                    if value['nativeName'] == f"{request.form.get('select1')}":
                        lan_1 = key
                    if value['nativeName'] == f"{request.form.get('select2')}":
                        lan_2 = key
                # print(lan_1, lan_2)
                querystring = {"to[0]": f"{lan_2}", "api-version": "3.0", "profanityAction": "NoAction",
                               "textType": "plain"}

                payload = [{"Text": f"{textarea_1}"}]

                response = requests.post(f"{URL}/translate", json=payload, headers=HEADERS, params=querystring)

                # print(response.json()[0]['translations'][0]['text'])
                return render_template('translator.html', result=response.json()[0]['translations'][0]['text'],
                                       first_text=textarea_1, t_1=request.form.get('select1'),
                                       t_2=request.form.get('select2'), languages=native_names, translate=True)
            except KeyError:
                flash('Select your language please!!!')
                return redirect(url_for('swap'))

    return render_template('translator.html', languages=native_names)


@app.route('/dictionary', methods=["GET", "POST"])
def dictionary():
    if request.method == "POST":

        # print(request.form['vocab'], request.form['select-to'])
        from_lan = ''
        to_lan = 'en'
        vocab = request.form['vocab']
        payload = [{"Text": vocab}]
        for (key, value) in languages['translation'].items():
            if value['nativeName'] == f"{request.form['select-from']}":
                from_lan = key

        # print(from_lan, to_lan)

        querystring = {"to": to_lan, "api-version": "3.0", "from": from_lan}

        response = requests.post(f"{URL}/Dictionary/Lookup", json=payload, headers=HEADERS, params=querystring)

        result = response.json()[0]

        dict_result = []
        position = ''
        for num in range(len(result['translations'])):

            s = result['translations'][num]['displayTarget']
            position = result['translations'][0]['posTag']

            if s not in dict_result:
                dict_result.append(s.title())

        dict_result_t = ", ".join(dict_result)
        # print(dict_result)
        # print(request.form['select-from'])


        words = []
        for word in dict_result:
            if " " not in word:
                words.append(word.lower())

        audio_us = f'https://ssl.gstatic.com/dictionary/static/sounds/20200429/{words[0]}--_gb_1.mp3'
        d_url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{words[0]}'
        response = requests.get(d_url)
        phonetic_text = []
        show = False
        num_definitions = len(response.json()[0]['meanings'][0]['definitions'])
        # print(len(response.json()[0]['phonetics']))
        for n in range(len(response.json()[0]['phonetics'])):
            try:
                phonetic_text.append(response.json()[0]['phonetics'][n]['text'])
            except KeyError:
                pass

        allPartOfSpeech = []
        allDefinitions_n = []
        allDefinitions_v = []
        allDefinitions_adj = []
        allExamples = []
        wikiSource = []

        for i in range(len(response.json())):
            try:
                wikiSource.append("".join(response.json()[i]['sourceUrls']))
            except KeyError:
                pass

        try:
            print(response.json())
            for i in range(num_definitions):
                # i need to work here for extract all of needed parts
                if response.json()[0]['meanings'][i]['partOfSpeech'] == 'noun':
                    # print("yes it is noun")
                    for nd in range(len(response.json()[0]['meanings'][i]['definitions'])):
                        allDefinitions_n.append(response.json()[0]['meanings'][i]['definitions'][nd]['definition'])

                elif response.json()[0]['meanings'][i]['partOfSpeech'] == 'verb':
                    # print("yes it is verb")
                    for nd in range(len(response.json()[0]['meanings'][i]['definitions'])):
                        allDefinitions_v.append(response.json()[0]['meanings'][i]['definitions'][nd]['definition'])

                elif response.json()[0]['meanings'][i]['partOfSpeech'] == 'adjective':
                    # print("yes it is adj")
                    for nd in range(len(response.json()[0]['meanings'][i]['definitions'])):
                        allDefinitions_adj.append(response.json()[0]['meanings'][i]['definitions'][nd]['definition'])
                        try:
                            allExamples.append(response.json()[0]['meanings'][i]['definitions'][nd]['example'])
                        except KeyError:
                            pass
            # print(phonetic_text, audio_us)
        except:
            show = False
            pass
        # print(allDefinitions_n)
        # print(allDefinitions_v)
        # print(allDefinitions_adj)
        # print(allExamples)
        # print(phonetic_text)
        # print(wikiSource)
        return render_template('dict.html', dictionary=True, languages=native_names,
                               from_lan=request.form['select-from']
                               , to_lan=request.form['select-to'], word=vocab.title(), pos=position,
                               result=dict_result_t, audio=audio_us, phonetic_text=phonetic_text[0], show=show,
                               examples=allExamples, definitions_v=allDefinitions_v, definitions_n=allDefinitions_n,
                               definitions_adj=allDefinitions_adj, positions=allPartOfSpeech, wiki=wikiSource[0])
    return render_template('dict.html', languages=native_names)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(debug=True, port=5004)
