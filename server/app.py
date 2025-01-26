#!/usr/bin/env python3
from flask import Flask, request, make_response
from flask_restful import Api, Resource
from flask_migrate import Migrate
from models import db, Restaurant, RestaurantPizza, Pizza
import os

# Set up the database URI from environment or fallback to default
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask app and configuration
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable Flask-SQLAlchemy modification tracking
app.json.compact = False  # Pretty-print JSON output

# Initialize database and migration
migrate = Migrate(app, db)
db.init_app(app)

# Set up Flask-RESTful API
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        """Fetch all restaurants."""
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants], 200

class RestaurantByID(Resource):
    def get(self, id):
        """Fetch a restaurant by ID."""
        restaurant = db.session.get(Restaurant, id)  # Using db.session.get() instead of query.get()
        if restaurant:
            return restaurant.to_dict(), 200
        return {'error': 'Restaurant not found'}, 404

    def delete(self, id):
        """Delete a restaurant by ID."""
        restaurant = db.session.get(Restaurant, id)  # Using db.session.get() instead of query.get()
        if restaurant:
            try:
                db.session.delete(restaurant)
                db.session.commit()
                return {}, 204
            except Exception as e:
                db.session.rollback()
                return {'error': f'Failed to delete: {str(e)}'}, 500
        return {'error': 'Restaurant not found'}, 404

class Pizzas(Resource):
    def get(self):
        """Fetch all pizzas."""
        pizzas = Pizza.query.all()
        return [pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas], 200

class RestaurantPizzas(Resource):
    def post(self):
        """Create a new restaurant-pizza relation."""
        data = request.get_json()
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"]
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return make_response(new_restaurant_pizza.to_dict(), 201)
        except ValueError:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400
        except Exception as e:
            db.session.rollback()
            return {"errors": [f"unexpected error: {str(e)}"]}, 400

# Register resources with routes
api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantByID, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
