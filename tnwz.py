# coding: utf-8
import datetime
import hashlib
import time
import random
import requests
from pymongo import MongoClient


class Tnwz(object):
    """头脑王者"""

    def __init__(self, uid, token="", quiz_bank=False, open_id=""):
        # API URL
        self.host = "https://question.hortor.net"
        self.url_login = self.host + "/question/player/login"
        self.url_into_room = self.host + "/question/bat/intoRoom"
        self.url_match = self.host + "/question/bat/match"
        self.url_leave_room = self.host + "/question/bat/leaveRoom"
        self.url_begin_fight = self.host + "/question/bat/beginFight"
        self.url_find_quiz = self.host + "/question/bat/findQuiz"
        self.url_choose_answer = self.host + "/question/bat/choose"
        self.url_get_fight_result = self.host + "/question/bat/fightResult"

        self.open_id = open_id
        self.uid = uid
        self.token = token
        if not token:
            self.login()

        # fighting
        self.room_id = -1
        self.quiz_bank = quiz_bank

    @staticmethod
    def create_sign(params):
        """签名"""
        params = sorted(params.items())
        src = ''.join(['{}={}'.format(key, value)
                       for key, value in params if key not in ["sign"]])
        hmd5 = hashlib.md5()
        src = src.encode('utf-8')
        # print(src)
        hmd5.update(src)
        return hmd5.hexdigest()

    def handle_request(self, api, params):
        """Make requests"""
        params.update({"token": self.token})
        sign = self.create_sign(params)
        params.update({
            "sign": sign
        })
        headers = {
            "Host": "question.hortor.net",
            "Accept-Encoding": "br, gzip, deflate",
            'Content-Type': 'application/x-www-form-urlencoded',
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_2 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Mobile/15C202 MicroMessenger/6.6.1 NetType/WIFI Language/en"
        }
        # print(api)
        result = requests.post(api, params, headers=headers)
        if result.status_code != 200:
            raise Exception("Maybe network error")

        rj = result.json()
        if rj["errcode"] != 0:
            raise Exception("Game Error")

        return rj

    def _get_current_time(self):
        return str(int(datetime.datetime.now().strftime("%s")) * 1000)

    def into_room(self, room_id=None):
        """Enter a room"""
        print("Into Room {}".format(-1 if not room_id else room_id))
        params = {
            # 是否进入别人房间
            "roomID": -1 if not room_id else room_id,
            "uid": self.uid,
            "t": self._get_current_time()
        }
        result = self.handle_request(self.url_into_room, params)
        self.room_id = result["data"]["roomId"]
        print("Room: {}".format(self.room_id))
        return self.room_id

    def match(self):
        """Match"""
        params = {
            "matchId": 300012,
            "npcId": "undefined",
            "uid": self.uid,
            "t": self._get_current_time()
        }
        print("matching...")
        result = self.handle_request(self.url_match, params)
        return result

    def leave_room(self):
        """Leave room"""
        print("Leave room {}".format(self.room_id))
        params = {
            "roomID": self.room_id,
            "uid": self.uid,
            "t": self._get_current_time()
        }
        result = self.handle_request(self.url_leave_room, params)
        # check if success
        return True

    def begin_fight(self):
        """Begin fight"""
        print("Begin fight")
        params = {
            "roomID": self.room_id,
            "uid": self.uid,
            "t": self._get_current_time()
        }
        result = self.handle_request(self.url_begin_fight, params)
        # check if success
        return True

    def find_quiz(self, quiz_num):
        """Find quiz"""
        print("Find quiz of {}".format(quiz_num))
        params = {
            "roomID": self.room_id,
            "uid": self.uid,
            "t": self._get_current_time(),
            "quizNum": quiz_num
        }
        result = self.handle_request(self.url_find_quiz, params)
        result = result["data"]
        return result

    def choose_answer(self, quiz_num, option, timeout=False):
        """Choose answer"""
        print("Choose answer of quiz {}".format(quiz_num))
        params = {
            "roomID": self.room_id,
            "uid": self.uid,
            "t": self._get_current_time(),
            "quizNum": quiz_num,
            "options": option
        }
        if timeout:
            # 0.5s ~ 2s
            time.sleep(random.randint(500, 2000) / 1000.)
        result = self.handle_request(self.url_choose_answer, params)
        result = result["data"]
        return result

    def get_fight_result(self):
        """Get result of fight"""
        print("Get fight result")
        params = {
            "roomID": self.room_id,
            "type": 0,
            "uid": self.uid,
            "t": self._get_current_time()
        }
        result = self.handle_request(self.url_get_fight_result, params)
        return result

    def battle_answer(self, quiz_num):
        """One quiz"""
        # 获取题目
        quiz = self.find_quiz(quiz_num)
        if not quiz:
            return False
        # print(quiz['quiz'])
        # print(quiz['options'])

        # 查找题库内是否有该题
        found = False
        if self.quiz_bank:
            answer, found = self.quiz_bank.look_for_quiz(quiz)

        if not found:
            answer = random.randint(0, 3)

        # 回答问题
        result = self.choose_answer(quiz_num, answer)

        if self.quiz_bank and not found:
            self.quiz_bank.save_quiz(quiz, answer=result["answer"])

    def battle_answers(self, auto=False, period=10):
        """Answer question"""
        for quiz_num in range(1, 6):

            self.battle_answer(quiz_num)

            # 每次答题1秒
            time.sleep(period)

    def battle_with_friend(self, friend, period=10):
        """Start a battle"""
        if not isinstance(friend, Tnwz):
            raise Exception("Error friend")
        self.into_room()
        friend.into_room(self.room_id)

        # 房间主人开始
        self.begin_fight()
        # friend.begin_fight()

        for quiz_num in range(1, 6):
            self.battle_answer(quiz_num)
            friend.battle_answer(quiz_num)
            time.sleep(period)

        self.get_fight_result()
        friend.get_fight_result()
        self.leave_room()
        friend.leave_room()
        return True

    def battle_with_match(self):
        """match battle"""
        self.match()
        self.battle_answers()
        self.get_fight_result()

    def login(self):
        """login"""
        if not self.open_id:
            raise Exception("No openId")
        print("Login user: {}".format(self.uid))
        params = {
            "scene": 1089,
            "openId": self.open_id,
            "playerId": self.uid,
            "uid": 0,
            "t": self._get_current_time()
        }
        result = self.handle_request(self.url_login, params=params)
        self.token = result["data"]["token"]
        print("Token {}".format(self.token))
        return True


class QuizBank():
    """题库"""

    def __init__(self):

        self.client = MongoClient('mongodb://localhost:27017/')
        db = self.client.tnwzDB
        if not db:
            db.createCollection('Quizzes')

        self.quizzes = db.Quizzes

    def look_for_quiz(self, quiz):
        """look for answer of quiz

        quiz example:
        {
            'quiz': '中国历史中，韩非与李斯的师傅是？', 
            'options': ['老子', '孔子', '荀子', '鬼谷子'], 
            'num': 4,
            'school': '文科', 
            'type': '历史', 
            'typeID': 3, 
            'contributor': '找抽的猫', 
            'partner': 0, 
            'endTime': 1516529447, 
            'curTime': 1516529433, 
            'myBuff': {}
            }
        """
        answer = -1
        found = False
        target = self.quizzes.find_one({"quiz": quiz['quiz']})
        if target:
            # find index
            if target["answer_str"] in quiz['options']:
                print("Found an existed quiz: {}".format(quiz['quiz']))
                print(target["answer_str"])
                answer = quiz["options"].index(target["answer_str"]) + 1
                found = True
        return answer, found

    def save_quiz(self, quiz, answer):
        """Save new quiz"""
        saved_quiz = {
            "quiz": quiz["quiz"],
            "options": quiz["options"],
            "school": quiz["school"],
            "type": quiz["type"],
            "answer": answer,
            "answer_str": quiz["options"][answer - 1],
        }
        inserted_id = self.quizzes.insert_one(saved_quiz).inserted_id
        if inserted_id:
            return True
        return False


if __name__ == '__main__':

    # battble with friend
    users = [{
        "uid": "",
        "token": ""
    }, {
        "uid": "",
        "token": ""
    }]
    quiz_bank = QuizBank()
    open_id = ""
    user_1 = Tnwz(
        uid=users[0]["uid"],
        token=users[0]["token"],
        quiz_bank=quiz_bank,
        open_id=open_id)
    user_2 = Tnwz(
        uid=users[1]["uid"],
        token=users[1]["token"],
        open_id=open_id)
    while True:
        user_1.battle_with_friend(friend=user_2, period=0)
