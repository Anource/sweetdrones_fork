# Импорты для вк
import requests
import random
import json


class vk:
    def __init__(self, token, v):
        self.token = token
        self.v = v

    def send_request(self, method, extra_data={}):
        data = {'access_token': self.token, 'v': self.v}
        data.update(extra_data)
        return requests.post('https://api.vk.com/method/{}'.format(method), data=data)

    def send_message(self, user_id, message, attachment=''):
        data = {
            'user_id': user_id, 'message': message,
            'random_id': str(random.randint(0, 10000000)),
            'attachment': attachment
        }
        response = self.send_request('messages.send', data)
        answer = json.loads(response.content)
        if 'error' in answer:
            return 'Error {}: {}'.format(answer['error']['error_code'], answer['error']['error_msg'])
        elif 'response' in answer:
            return 'Message sent! Message id: {}'.format(answer['response'])
        else:
            return 'Unknown error!'

    def get_user_info(self, user_id, fields=''):
        data = {
            'user_ids': user_id, 'fields': fields
        }
        response = self.send_request('users.get', data)
        info = json.loads(response.content)
        return info

    def upload_photo(self, photo_path):
        upload_server = self.send_request('photos.getMessagesUploadServer')
        # print(json.loads(upload_server.text))
        upload_url = json.loads(upload_server.text)['response']['upload_url']
        files = {'photo': open(photo_path, 'rb')}
        upload_file = requests.post(upload_url, files=files)
        file_info = json.loads(upload_file.text)
        data = {
            'server': file_info['server'],
            'photo': file_info['photo'],
            'hash': file_info['hash']
        }
        save_photo = self.send_request('photos.saveMessagesPhoto', data)
        photo_info = json.loads(save_photo.text)
        return 'photo{}_{}'.format(photo_info['response'][0]['owner_id'], photo_info['response'][0]['id'])

    def upload_doc(self, user_id, doc_path):
        data = {
            'peer_id': user_id
        }
        upload_server = self.send_request('docs.getMessagesUploadServer', data)
        # print(upload_server.text)
        upload_url = json.loads(upload_server.text)['response']['upload_url']
        files = {'file': open(doc_path, 'rb')}
        upload_file = requests.post(upload_url, files=files)
        file_info = json.loads(upload_file.text)
        data = {
            'file': file_info['file']
        }
        save_doc = self.send_request('docs.save', data)
        doc_info = json.loads(save_doc.text)
        return 'doc{}_{}'.format(doc_info['response']['doc']['owner_id'], doc_info['response']['doc']['id'])

    def send_doc(self, user_id, message, doc_path):
        return self.send_message(user_id, message, attachment=self.upload_doc(user_id, doc_path))
