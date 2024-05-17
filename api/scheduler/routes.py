from api.lib.lib import check_sensor_guard
from flask import Blueprint, request, jsonify

# All schedulers share the same instance, and since we can't instantitate the base class, 
# we'll just use any for these generic routes
# DO NOT ADD add() and update() routes as these contain sensor specific commands
from api.scheduler.scheduler import lightScheduler as scheduler

schedule_blueprint = Blueprint('schedule', __name__)

# Schedule Routes
@schedule_blueprint.route('/delete', methods=['POST'])
def delete():
    id = request.json['id']
    scheduler.delete(id)
    return jsonify(msg='deleted'), 200

@schedule_blueprint.route('/delete-all', methods=['POST'])
def deleteAll():
    scheduler.deleteAll()
    return jsonify(msg='deleted all'), 200

@schedule_blueprint.route('/get-all', methods=['GET'])
def getAll():
    jobs = scheduler.getAll()
    return jsonify(jobs), 200