import random
from flask import Flask, request, abort, jsonify
from flask_cors import CORS

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Book API Tutorial Reference: https://github.com/udacity/cd0037-API-Development-and-Documentation-exercises/
# blob/master/6_Final_Review/backend/flaskr/__init__.py

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def valid_question(body):
    if not ('question' in body and 'answer' in body and 'category' in body and 'difficulty' in body):
        return False
    else:
        return True


def valid_quiz(body):
    if not ('quiz_category' in body and 'previous_questions' in body):
        return False
    else:
        return True

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
        return response

    @app.route('/categories')
    def retrieve_categories():
        categories = Category.query.order_by(Category.type).all()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': [category.format() for category in categories]
        })

    @app.route('/questions')
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.all()

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': [category.format() for category in categories]
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(422)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        if not valid_question(body):
            abort(422)

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        try:
            question = Question(question=new_question, answer=new_answer, category=new_category,
                                difficulty=new_difficulty)
            question.insert()

            return jsonify({
                'success': True,
                'question.id': question.id
            })
        except:
            abort(422)


    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        if search_term:
            results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in results],
                'total_questions': len(results),
                'current_category': None
            })
        abort(404)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_on_category(category_id):
        try:
            questions = Question.query.filter(Question.category == str(category_id)).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': category_id
            })
        except:
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def quiz():
        try:
            body = request.get_json()
            if not valid_quiz(body):
                abort(422)

            category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')

            if category['type'] == 'click':
                remaining_questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
            else:
                remaining_questions = Question.query.filter_by(category=category['id']).filter(
                  Question.id.notin_(previous_questions)).all()

            random_question = None
            if len(remaining_questions) > 0:
                random_index = random.randrange(0, len(remaining_questions))
                random_question = remaining_questions[random_index].format()

            return jsonify({
                'success': True,
                'question': random_question
            })
        except:
            abort(422)

    # Error Tutorial Reference: https://github.com/udacity/cd0037-API-Development-and-Documentation-exercises/
    # blob/2e69c73c956190615d54b506436138cec720a91a/2_Errors_Review/backend/flaskr/__init__.py#L131
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify({"success": False, "error": 500, "message": "internal server error"})
        )

    return app
