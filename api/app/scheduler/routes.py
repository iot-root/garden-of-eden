from app.lib.lib import check_sensor_guard
from flask import Blueprint, request, jsonify

# All schedulers share the same instance, and since we can't instantitate the base class, 
# we'll just use any for these generic routes
# DO NOT ADD add() and update() routes as these contain sensor specific commands
from app.scheduler.scheduler import lightScheduler as scheduler

schedule_blueprint = Blueprint('schedule', __name__)

# Schedule Routes
@schedule_blueprint.route('/delete', methods=['POST'])
def delete():
    try:
        id = request.json['id']
        scheduler.delete(id)
        return jsonify(msg='deleted'), 200
    except Exception as e:
        return jsonify(error=str(e))

@schedule_blueprint.route('/delete-all', methods=['POST'])
def deleteAll():
    try:
        scheduler.deleteAll()
        return jsonify(msg='deleted all'), 200
    except Exception as e:
        return jsonify(error=str(e))

@schedule_blueprint.route('/get-all', methods=['GET'])
def getAll():
    try:
        jobs = scheduler.getAll()
        return jsonify(jobs), 200
    except Exception as e:
        return jsonify(error=str(e))