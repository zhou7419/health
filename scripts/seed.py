import os
import sys
import random
from datetime import date, timedelta

# Add project root to sys.path to allow importing from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, Base, engine
from app.models.metric import MetricDefinition, MetricRecord

def seed_data():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(MetricRecord).count() > 0:
        print("Data already exists. Skipping seed.")
        db.close()
        return

    print("Seeding metric definitions...")
    
    definitions = [
        MetricDefinition(name="体重", unit="kg", expected_min=60.0, expected_max=75.0),
        MetricDefinition(name="收缩压", unit="mmHg", expected_min=90.0, expected_max=120.0),
        MetricDefinition(name="舒张压", unit="mmHg", expected_min=60.0, expected_max=80.0),
        MetricDefinition(name="心率", unit="bpm", expected_min=60.0, expected_max=100.0),
        MetricDefinition(name="空腹血糖", unit="mmol/L", expected_min=3.9, expected_max=6.1)
    ]
    db.add_all(definitions)
    db.commit()
    
    # Retrieve assigned IDs
    def_map = {d.name: d.id for d in definitions}

    print("Seeding mock health metric data...")
    
    # Generate dates over the past 3 months
    base_date = date.today() - timedelta(days=90)
    dates = [base_date + timedelta(days=i) for i in range(0, 90, 7)] # Check up roughly every week
    
    metrics_to_add = []
    
    # Starting values
    weight = 70.0
    systolic = 125
    diastolic = 82
    heart_rate = 72
    blood_sugar = 5.2
    
    for record_date in dates:
        # Simulate slight variations
        weight += random.uniform(-0.5, 0.3)
        systolic += random.randint(-3, 2)
        diastolic += random.randint(-2, 2)
        heart_rate += random.randint(-4, 4)
        blood_sugar += random.uniform(-0.2, 0.1)
        
        # Add weight
        metrics_to_add.append(MetricRecord(
            metric_id=def_map["体重"], value=round(weight, 1), record_date=record_date, notes="晨起空腹"
        ))
        
        # Add blood pressure
        metrics_to_add.append(MetricRecord(
            metric_id=def_map["收缩压"], value=systolic, record_date=record_date, notes="右臂"
        ))
        metrics_to_add.append(MetricRecord(
            metric_id=def_map["舒张压"], value=diastolic, record_date=record_date, notes="右臂"
        ))
        
        # Add heart rate
        metrics_to_add.append(MetricRecord(
            metric_id=def_map["心率"], value=heart_rate, record_date=record_date, notes="静息"
        ))
        
        # Add blood sugar (fasting)
        metrics_to_add.append(MetricRecord(
            metric_id=def_map["空腹血糖"], value=round(blood_sugar, 2), record_date=record_date, notes="餐前"
        ))

    db.add_all(metrics_to_add)
    db.commit()
    print(f"Successfully inserted {len(metrics_to_add)} mock records.")
    db.close()

if __name__ == "__main__":
    seed_data()
