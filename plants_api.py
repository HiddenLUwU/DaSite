import flask
from flask import jsonify, make_response, request
from . import db_session
from .plants_UwU import Plants

blueprint = flask.Blueprint(
    'news_api',
    __name__,
    template_folder='templates'
)


@blueprint.app_errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@blueprint.app_errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@blueprint.route('/api/plants/<int:plants_id>', methods=['GET'])
def get_one_news(plants_id):
    db_sess = db_session.create_session()
    plant = db_sess.query(Plants).get(plants_id)
    if not plant:
        return make_response(jsonify(
            {
                'error': 'Not found'
            }
        ), 404)
    return jsonify(
        {
            'plants': plant.to_dict(only=(
                'message', 'sender'))
        }
    )


@blueprint.route('/api/plants', methods=['POST'])
def create_news():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['plant', 'image', 'message', 'sender']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    plant = Plants(
        plant=request.json['plant'],
        image=request.json['image'],
        message=request.json['message'],
        sender=request.json['sender']
    )
    db_sess.add(plant)
    db_sess.commit()
    return jsonify({'id': plant.id})


@blueprint.route('/api/plants/<int:plants_id>', methods=['DELETE'])
def delete_news(plants_id):
    db_sess = db_session.create_session()
    plant = db_sess.query(Plants).get(plants_id)
    if not plant:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(plant)
    db_sess.commit()
    return jsonify({'success': 'OK'})
