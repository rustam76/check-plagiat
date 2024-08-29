from apps.controller import blueprint

@blueprint.route('/login')
def index():
    return {'message': 'Hello, World!'}