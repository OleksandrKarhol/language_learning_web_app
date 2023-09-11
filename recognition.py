import requests 
import config 


# upload

upload_endpoint = "https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
headers = {'authorization': config.API_KEY}

def upload(filename):

    def read_file(filename):
        # Open the file in binary mode for reading
        with open(filename, 'rb') as _file:
            while True:
                # Read a chunk of data from the file
                data = _file.read()
                # If there's no more data, stop reading
                if not data:
                    break
                # Yield the data as a generator
                yield data

    
    upload_response = requests.post(upload_endpoint,
                            headers = headers,
                            data = read_file(filename))

    audio_url = upload_response.json()['upload_url']
    return audio_url


# transcribe
def transcribe(audio_url):
    transcipt_request = {'audio_url': audio_url}
    transcript_response = requests.post(transcript_endpoint,
                            json = transcipt_request,
                            headers = headers)

    job_id = transcript_response.json()['id']
    return job_id


# poll
def poll(transcript_id):

    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers = headers)
    return polling_response.json()

def get_transcription(audio_url):
    transcript_id = transcribe(audio_url)
    while True: 
        data = poll(transcript_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data['error']