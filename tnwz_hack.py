# coding: utf-8
import json
from tnwz import QuizBank, Tnwz


class TnwzHacker:
    """头脑王者hacker"""

    def __init__(self, quiz_bank=None):
        self.quiz_bank = quiz_bank
        self._cache = {}

    def _load_as_json(self, text):
        result = {}
        for t in text.split("&"):
            key, value = t.split("=")
            result[key] = value
        return result

    def _json_dumps(self, jso):
        result = "&".join(["{}={}".format(key, value)
                           for key, value in jso.items()])
        return result

    def request(self, flow):
        """modify request"""
        if ('question.hortor.net' in flow.request.host) and \
                ("question/bat/choose" in flow.request.path):
            # get answer
            answer_msg = self._load_as_json(flow.request.text)

            room_id = answer_msg['roomID']
            quiz_num = answer_msg['quizNum']
            # find right answer
            found = False
            if self.quiz_bank:
                quiz = self._get_quiz(room_id, quiz_num)
                if not quiz:
                    answer, found = "", False
                else:
                    answer, found = self.quiz_bank.look_for_quiz(quiz)
            if found:
                # modify
                answer_msg['option'] = answer
                answer_msg["token"] = self._get_quiz("user", "token")
                answer_msg['sign'] = Tnwz.create_sign(answer_msg)
                text = self._json_dumps(answer_msg)
                flow.request.text = text
                flow.request.content = str.encode(text)

    def _get_quiz(self, room_id, quiz_num):
        """Get quiz and options"""
        key = "{}_{}".format(room_id, quiz_num)
        if key in self._cache:
            return self._cache[key]
        return {}

    def _cache_quiz(self, room_id, quiz_num, quiz):
        """Cache quiz"""
        self._cache["{}_{}".format(room_id, quiz_num)] = quiz
        return True

    def response(self, flow):
        """hack response"""
        if ('question.hortor.net' in flow.request.host) and \
                ("question/bat/findQuiz" in flow.request.path):
            # get quiz and options
            request_text = self._load_as_json(flow.request.text)
            room_id = request_text["roomID"]
            # 第一题有bug,题号不正确
            # quiz_num = request_text["quizNum"]
            body = json.loads(flow.response.text)
            quiz_num = body['data']['num']
            self._cache_quiz(room_id, quiz_num, body["data"])

        if ('question.hortor.net' in flow.request.host) and \
                ("question/player/login" in flow.request.path):
            # get token
            print("Login.....")
            body = json.loads(flow.response.text)
            self._cache_quiz("user", "token", body["data"]["token"])


tnwz_hacker = TnwzHacker(QuizBank())


def response(flow):
    """hack response"""
    return tnwz_hacker.response(flow)


def request(flow):
    """hack request"""
    return tnwz_hacker.request(flow)


def start():
    """入口"""
    print("Start......")
