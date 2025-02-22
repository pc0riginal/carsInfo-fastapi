import random
import os
os.chdir('./static/images')
# Function to generate random data for cars
def generate_car_data(car_id):
    makes = ["CarBrand", "Speedy", "Elektrik", "CarPro", "TurboFast"]
    models = ["Fast", "SuperCar", "Beetle", "FourWheeler SUV", "AutoCar", "Supersonic"]
    years = random.randint(1995, 2025)
    prices = round(random.uniform(15000, 300000), 2)
    engines = ["V4", "V6", "V8", "V12", "Electric"]
    autonomous = random.choice([True, False])
    continents = ["NA", "AF", "OC", "SA", "EU", "AS", "AN"]
    images = os.listdir()
    
    car = {
        "image":random.choice(images),
        "make": random.choice(makes),
        "model": random.choice(models),
        "year": years,
        "price": prices,
        "engine": random.choice(engines),
        "autonomous": autonomous,
        "sold": random.sample(continents, random.randint(0, len(continents)))  # Random countries sold
    }
    
    return car

cars = []
# Generate more cars up to 100
for car_id in range(1, 101):
    car = generate_car_data(car_id)
    car["car_id"] = car_id
    cars.append(car)

# You now have a dictionary `cars` with 100 cars
print(cars)