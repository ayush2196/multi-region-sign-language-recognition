
from flask import Flask,request,render_template,send_from_directory,jsonify
import utilities.languageProcessing as lp
import ssl
import json

ssl._create_default_https_context = ssl._create_unverified_context

app =Flask(__name__,static_folder='static', static_url_path='')

@app.route('/',methods=['GET'])
def index():
	lp.clear_all();
	return render_template('index.html')

@app.route('/',methods=['GET','POST'])
def flask_test():
	lp.clear_all();
	text = request.form.get('text') #gets the text data from input field of front end
	print("text is", text)
	if(text==""):
		return "";
	lp.take_input(text)

	# fills the json 
	for words in lp.final_output_in_sent:
		for i,word in enumerate(words,start=1):
			lp.final_words_dict[i]=word;

	print("---------------Final words dict--------------");
	print(lp.final_words_dict)

	return lp.final_words_dict;

@app.route('/static/<path:path>')
def serve_signfiles(path):
	return send_from_directory('static',path)

@app.route('/parser', methods=['GET', 'POST'])
def parseit():
    if request.method == "POST":
        input_string = request.form['text']
    else:
        input_string = request.args.get('speech')
    input_string = input_string.capitalize()
    isl_parsed_token_list = lp.convert_eng_to_isl(input_string)

    # lemmatize tokens
    lemmatized_isl_token_list = lp.lemmatize_tokens(isl_parsed_token_list)

    # remove stop words
    filtered_isl_token_list = lp.filter_stop_words(lemmatized_isl_token_list)

    isl_text_string = ""

    for token in filtered_isl_token_list:
        isl_text_string += token
        isl_text_string += " "

    isl_text_string = isl_text_string.lower()

    data = {
        'isl_text_string': isl_text_string,
        'pre_process_string': lp.pre_process(isl_text_string)
    }
    return json.dumps(data)

if __name__=="__main__":
	app.run(debug=True)