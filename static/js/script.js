// prevents the user from entering bad characters in input that could break the python code :(
$('input').on('keypress', function (e) {
  if(e.keyCode==13){return true};
  if (e.which < 48 && e.which!=32|| 
    (e.which > 57 && e.which < 65) || 
    (e.which > 90 && e.which < 97) ||
    e.which > 122) {
    e.preventDefault();
}
// console.log(e.keyCode)
});

/*
        Load json file for sigml available for easy searching
    */
        // $("#speech_loader").hide();
        // $('#loader').hide();
    
        $.getJSON("js/sigmlFiles.json", function(json){
            sigmlList = json;
        });
    
        // code for clear button in input box for words
        // $("#btnClear").click(function() {
        //     $("#inputText").val("");
        // });
    
        // // code to check if avatar has been loaded or not and hide the loading sign
        // var loadingTout = setInterval(function() {
        //     if(tuavatarLoaded) {
        //         $("#loading").hide();
        //         clearInterval(loadingTout);
        //         console.log("Avatar loaded successfully !");
        //     }
        // }, 1000);
    

// list of puntutation marks for english language
englishpMarks = ["?", "!", "."];

hindipMarks = []; // include the hindi puntuation marks in UTF format

var wordArrayJson=[];
// makes a li for available words in signFiles

function FinalText(word, fileName)
{
	this.word = word;
	this.fileName = fileName;
}

function test_list()
{
    
    let ul = document.querySelector(".test_list");
    fetch('static/js/sigmlFiles.json')
    .then(response => response.json())
     .then((data)=>
     {
         data.forEach((e)=>
         {
            // let word = e.name;
            let tempjson = {word:e.name};
            wordArrayJson.push(tempjson);
             let li=document.createElement("li");
            //  li.appendChild(document.createTextNode(e.name));
            li.innerHTML=`<a href="#player" onclick="setSiGMLURL('SignFiles/${e.name}.sigml');" > ${e.name}</a>`
            ul.appendChild(li);
            // console.log(e.name);
         });
     });

}
test_list();

// word array for playing words
var wordArray=[];

// stops a tag from redirecting
$('a').click(function(event){
    event.preventDefault();
  });

// stops submit button from submitting the form 
let form =  document.getElementById('form');
form.addEventListener('submit', function(event) {
    event.preventDefault();
});


let sub =  document.getElementById('submit');
  sub.addEventListener('click',()=>
  {

    let input =  document.getElementById('text').value;
    console.log("INPUT is ",input);

    // ajax request to get the response from flask in json and play the words
      $.ajax({
          url:'/',
          type:'POST',
          data:{text:input},
          success: function(res)
          {
            convert_json_to_arr(res);
            play_each_word();
            display_isl_text(res);
          },
          error: function(xhr)
          {
            console.log(xhr);
          }
      });
  });

  // displays isl text 
function display_isl_text(words)
  {
      let p = document.getElementById("isl_text");
      p.textContent="";
      Object.keys(words).forEach(function(key) 
      {
        p.textContent+= words[key]+" ";
      });
  }
// displays currently playing word/letter
  function display_curr_word(word)
  {
      let p = document.querySelector(".curr_word_playing");
      p.textContent=word;
      p.style="color:Red; font-size:24px;font-decoration:bold;";
  }

  // displays error message if some error is there
  function display_err_message()
  {
   
    let p = document.querySelector(".curr_word_playing");
    p.textContent="Some error occurred (Probably Sigml file of the word/letter is not proper)";
    p.style="color:Red; font-size:24px;font-decoration:bold;";
  }

// converts the returned  json to array
function convert_json_to_arr(words)
{
    wordArray=[];
    console.log("wordArray",words);
    Object.keys(words).forEach(function(key) {
        wordArray.push(words[key]);
    });
    console.log("wordArray",wordArray);
}

function isSpace(letter)
{
	// check if the letter is a space
	if(letter.charCodeAt(0).toString(16) == "20")
		return true;
	return false;
}

// plays each word
function play_each_word(){
  totalWords = wordArray.length;
  i = 0;
  var int = setInterval(function () {
      if(i == totalWords) {
          if(playerAvailableToPlay) {
              clearInterval(int);
              finalHint = $("#inputText").val();
              $("#textHint").html(finalHint);
              document.querySelector("#submit").disabled=false;
          }
          else{
            display_err_message();
            document.querySelector("#submit").disabled=false;
          }
      } else if(playerAvailableToPlay) {
              playerAvailableToPlay = false;
              startPlayer("SignFiles/" + wordArray[i]+".sigml");
              display_curr_word(wordArray[i]);
              console.log("CURRENTLY PLAYING",wordArray[i]);
              document.querySelector("#submit").disabled=true;
              i++;
            //   playerAvailableToPlay=true;
          }
         else {
            let errtext = $(".statusExtra").val(); 
            console.log("ERROR:- ", "Some error occurred (Probably Sigml file of the word/letter is not proper)");
            display_err_message();
            if(errtext.indexOf("invalid") != -1) {
                playerAvailableToPlay=true;
                document.querySelector("#submit").disabled=false;
            }
         }
  }, 1000);
};

function getParsedText(speech) {
  // console.log("$$ 1");

  var HttpClient = function() {
      this.get = function(aUrl, aCallback) {
          var anHttpRequest = new XMLHttpRequest();
          anHttpRequest.onreadystatechange = function() {
              if (anHttpRequest.readyState == 4 && anHttpRequest.status == 200)
                  aCallback(anHttpRequest.responseText);
          }

          anHttpRequest.open( "GET", aUrl, false );
          anHttpRequest.send( null );
      }
  };
  var final_response = "";
  var client = new HttpClient();
  client.get('http://127.0.0.1:5000/parser' + '?speech=' + speech, function(response) {
      console.log(response);
      final_response = JSON.parse(response);
  });
  // console.log("$$ 4");
  
  document.getElementById('isl').innerHTML = final_response['isl_text_string'];
  document.getElementById('speech_').innerHTML = speech; 
  return final_response['pre_process_string'];
}

function startDictation() {
  $('#speech_recognizer').hide();
  $("#speech_loader").show();
  console.log('Speech recognition started...');

  if (window.hasOwnProperty('webkitSpeechRecognition')) {
      recognition = new webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.lang = "en-US";
      recognition.start();

      recognition.onresult = function(e) {
          //document.getElementById('transcript').value = e.results[0][0].transcript;
          $('#speech_recognizer').show();
          $("#speech_loader").hide();
          $('#loader').show();

          console.log('Speech: ' + e.results[0][0].transcript);

          let speech = e.results[0][0].transcript;

          let parsedSpeech = getParsedText(speech);

          clickme(parsedSpeech);

          $('#loader').hide();

          recognition.stop();
          
          console.log('Speech recognition stopped...');

      };
      recognition.onerror = function(e) {
          recognition.stop();
      }
  }
}

var recognition = new webkitSpeechRecognition();
recognition.continuous     = true;
recognition.interimResults = true;

recognition.onstart = function() {
  console.log("Recognition started");
};
recognition.onresult = function(event){
  var text = event.results[0][0].transcript;
  console.log(text);

  if (text === "stop avatar") {
      recognition.stop();
  }

  document.getElementById('dom-target').value = text;
  // clickme();

};
recognition.onerror = function(e) {
  console.log("Error");
};

// recognition.onend = function() {
//     console.log("Speech recognition ended");
// };

function startDictation2() {
  recognition.lang = 'en-IN'; // 'en-US' works too, as do many others
  recognition.start();
}

// sets the avatarLoaded to true 
var loadingTout = setInterval(function() {
    if(tuavatarLoaded) {
        // $("#loading").hide();
        clearInterval(loadingTout);
        console.log("Avatar loaded successfully !");
    }
}, 1500);

function clickme(speech) {

  inputText = speech;
  // read the language that has been set
  lang = "English"; // using english for default
  tokens = [];

  if(lang=="English") {

      // tokenize the english paragraph
      tokenString = tokenizeEnglish(inputText);
      tokens = tokenString.split(',');
      console.log("Got tokens");

  } else if(lang == "Hindi") {

      // tokenize the english paragraph
      tokenString = tokenizeHindi(inputText);
      tokens = tokenString.split(',');
      console.log("Got tokens");

  }

  // remove empty values from tokens
  for(x = 0; x < tokens.length; x++) {
      t = tokens[x];

      if(t == "")
          tokens.splice(x, 1);
  }

  console.log(tokens);

  // process tokens based on language settings
  // use the script to generate the sigml files available and if
  // word file is available use word file less speak as letter based
  // list of sigmlfile is available in sigmlArray.js


  for(x = 0; x < tokens.length; x++) {
      // process each token
      t = tokens[x];
      if(t == "EOL")
          continue;
      // convert token to lower case for seaching in the database
      // search for name and it will return filename if it will exists
      t = t.toLowerCase();
      t = t.replace('.',""); // remove the puntuation from the end
      tokens[x] = t;
  }

  console.log(tokens);

  // reset the wordArray and arrayCounter here
  wordArray = [];
  arrayCounter = 0;
  console.log("sigmllength : "+sigmlList.length);
  for(x = 0; x < tokens.length; x++)
  {
      wordfoundflag = false;
      t = tokens[x];
      for(y = 0; y < sigmlList.length; y++) {
          if(sigmlList[y].name == t) {
              // console.log(sigmlList[y].sid);
              wordArray[arrayCounter++] = new FinalText(t, sigmlList[y].fileName);
              wordfoundflag = true;
              break;
          }
      }

      // if word not found then add chars - starts here
      if(wordfoundflag == false) {
          wordlen = t.length;
          for(p = 0; p < wordlen; p++) {
              q = t[p];
              //q=q.toUpperCase();
              for(k = 0; k < sigmlList.length; k++) {
                  if(sigmlList[k].name == q) {
                      wordArray[arrayCounter++] = new FinalText(q, sigmlList[k].fileName);
                      break;
                  }
              }
          }
          max = 0,countit=0;

          for(k=0;k<sigmlList.length;k++)
          {
              countit++;
              if(sigmlList[k].sid>max)
              { max = sigmlList[k].sid; }
          }
          console.log("maxi is : "+max);
          max = max + 1;
          if(t!="EOL"){
              console.log("k is : "+k);
              var obj = {"sid": max,"name": t,"fileName": t+".sigml"};

              var newdata = JSON.stringify(sigmlList);
              console.log(newdata);

          }
      }
      // if not word found part ends here
  }
  console.log(wordArray);
  console.log(wordArray.length);

  $("#debugger").html(JSON.stringify(wordArray));

  // wordArray object contains the word and corresponding files to be played
  // call the startPlayer on it in syn manner
  totalWords = wordArray.length;
  i = 0;

  var int = setInterval(function () {
      if(i == totalWords) {
          if(playerAvailableToPlay) {
              clearInterval(int);
              finalHint = $("#inputText").val();
              $("#textHint").html(finalHint);
          }
      } else {
          if(playerAvailableToPlay) {
              playerAvailableToPlay = false;
              startPlayer("SignFiles/" + wordArray[i].fileName);
              $("#textHint").html(wordArray[i].word);
              i++;
          }
      }
  }, 1500);
}

function tokenizeEnglish(inText)
{
	flag = false; // flag will be set true if the inText text will end with pMarks
	len = inText.length; 
	
	// the input should end with a punctuation mark
	for(x = 0; x < englishpMarks.length; x++) {
		// check if last character of the sentence is pMarks or not
		if(inText[len - 1] == englishpMarks[x]) {
			flag = true;
			break;
		}
	}
	
	// if no puntuation in the end then put a puntuation mark in the sentence
	if(flag == false)
		inputText = inText + ".";
	else
		inputText = inText;
	
	// convert the given paragraph into sentences 
	// result is an array holding each sentence own its own
	result = inputText.match( /[^\.!\?]+[\.!\?]+/g );
	console.log("tokenize into sentences : " + result);
	
	// convert each sentence into words and also add the pause 
	// identifier to make the animation pause after each word
	
	// loop over the result array and replace space and end of sentence 
	// and store it newString
	newString="";
	for(y = 0; y < result.length; y++) {
		line = result[y];
		for(x = 0; x < line.length; x++) {
			if(isSpace(line[x]))
				newString = newString + ",";
			else 
				newString = newString + line[x];
		}
		newString = newString + ",EOL,"; // EOL - end of line		
	}
	
	// create array of tokens
	console.log("Processed sting : " + newString);
	return newString;
}

function tokenizeHindi(inText)
{
	// implement the function to convert into the tokens here
	return intext;
}

// JavaScript code for converting text to speech
document.getElementById('convertToSpeech').addEventListener('click', async function () {
  const inputText = document.getElementById('inputText').value;
  const translatedText = await translateText(inputText);
  document.getElementById('translatedText').textContent = translatedText;
  speakText(translatedText);
});

async function translateText(text) {
  const deepLApiKey = '85a5e763-cca5-3058-8620-d3413ff41864:fx';
  const deepLApiEndpoint = 'https://api-free.deepl.com/v2/translate';
  const targetLanguage = 'EN'; // Change to your desired target language code

  const response = await fetch(deepLApiEndpoint, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `auth_key=${deepLApiKey}&text=${encodeURIComponent(text)}&target_lang=${targetLanguage}`,
  });

  if (response.ok) {
      const data = await response.json();
      return data.translations[0].text;
  } else {
      console.error('Failed to translate text');
      return text; // Return original text if translation fails
  }
}

function speakText(text) {
  const speechSynthesis = window.speechSynthesis;
  const utterance = new SpeechSynthesisUtterance(text);
  speechSynthesis.speak(utterance);
  document.getElementById('convertedSpeechText').textContent = text;
}