import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')  
        DB_USER = os.getenv('DB_USER', 'postgres')  
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')  
        DB_NAME = os.getenv('DB_NAME', 'trivia')  
        database_path = 'postgresql://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
        self.database_name = DB_NAME
        self.database_path = database_path
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_paginate_questions(self):
        result = self.client().get('/questions')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_retrieve_categories(self):
        result = self.client().get('/categories')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_retrieve_invalid_categories(self):
        result = self.client().get('/categories/1000')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_retrieve_questions(self):
        result = self.client().get('/questions')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_retrieve_invalid_questions(self):
        result = self.client().get('/questions?page=1000')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_delete_question(self):
        question = Question(question='test question', answer='test answer',difficulty=1, category=1)
        question.insert()
        question_id = question.id

        result = self.client().delete(f'/questions/{question_id}')
        data = json.loads(result.data)

        question = Question.query.filter(Question.id == question.id).one_or_none()

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
        self.assertEqual(question, None)

    def test_delete_invalid_question(self):
        result = self.client().delete('/questions/1000')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_question(self):
        new_question = {
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 1,
            'category': 1
        }
        before = len(Question.query.all())
        result = self.client().post('/questions', json=new_question)
        data = json.loads(result.data)
        after = len(Question.query.all())

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(after, before + 1)

    def test_create_invalid_question(self):
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 1
        }
        result = self.client().post('/questions', json=new_question)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_search_questions(self):
        new_search = {'searchTerm': 'l'}
        result = self.client().post('/questions/search', json=new_search)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_search_invalid_question(self):
        new_search = {'searchTerm': ''}
        result = self.client().post('/questions/search', json=new_search)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_questions_on_category(self):
        result = self.client().get('/categories/1/questions')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_questions_on_invalid_category(self):
        result = self.client().get('/categories/imp/questions')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_quiz(self):
        new_quiz = {'previous_questions': [], 'quiz_category': {'type': 'Entertainment', 'id': 5}}

        result = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_invalid_quiz(self):
        new_quiz = {'previous_questions': []}
        result = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()