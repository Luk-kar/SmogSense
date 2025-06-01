# Connections
import requests

# Download Polish stopwords from GitHub (or use your own list)
url = 'https://raw.githubusercontent.com/Luk-kar/stopwords/master/polish.stopwords.txt'
response = requests.get(url)
if response.status_code == 200:
    polish_stopwords = response.text.splitlines()
else:
    raise ConnectionError("Failed to download the stopwords file")

additional_stop_words = [
    "na", "dla", "za", "co", "nie", "się", "ze", "bo", "taki", 
    "jest", "tego", "jeśli", "które", "cię", "te", "przy", "niż",
    "tym", "którym", "być", "od", "ten", "do", "już",
    "gdzie", "będzie", "trzeba", "jego", "nikt", "w", "na", "o"
]

polish_stopwords += additional_stop_words