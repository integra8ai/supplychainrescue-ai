"""
Basic ML model for road delay prediction in SupplyChainRescue AI.
This is a simple linear regression model trained on synthetic data.
"""

import pickle
import os
import random
from datetime import datetime
from typing import Dict, Tuple
import pandas as pd
import numpy as np


class DelayPredictor:
    """
    Simple linear regression model for predicting road delays based on weather factors.

    This is a basic implementation suitable for Day 6 - it uses synthetic training data
    and provides predictions based on weather conditions, traffic factors, and road characteristics.
    """

    def __init__(self, model_path: str = "backend/ml_models/delay_model.pkl"):
        self.model_path = model_path
        self.weights = None
        self.bias = None
        self.feature_names = [
            'visibility', 'wind_speed', 'precipitation', 'temperature',
            'traffic_load', 'road_type_factor'
        ]

    def generate_training_data(self, n_samples: int = 1000) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Generate synthetic training data for the delay prediction model.
        """
        np.random.seed(42)
        random.seed(42)

        # Generate synthetic features
        data = []
        for _ in range(n_samples):
            sample = {
                'visibility': random.randint(500, 12000),  # meters
                'wind_speed': random.uniform(0, 20),       # m/s
                'precipitation': random.uniform(0, 25),     # mm/hour
                'temperature': random.uniform(-10, 35),     # Celsius
                'traffic_load': random.uniform(0, 1),       # normalized
                # highway = 1.0, local = 0.8, etc.
                'road_type_factor': random.uniform(0.5, 1.5)
            }

            # Calculate delay based on simple rule-based logic (ground truth)
            delay = self._calculate_delay_from_factors(sample)
            sample['delay'] = delay
            data.append(sample)

        df = pd.DataFrame(data)
        X = df[self.feature_names]
        y = df['delay']

        return X, y

    def _calculate_delay_from_factors(self, factors: Dict) -> float:
        """
        Calculate delay using rule-based logic (this will be our target variable)
        """
        delay = 0

        # Visibility impact
        if factors['visibility'] < 2000:
            delay += 40 * (1 - factors['visibility']/2000)
        elif factors['visibility'] < 5000:
            delay += 20 * (1 - factors['visibility']/5000)

        # Wind impact
        if factors['wind_speed'] > 15:
            delay += 15
        elif factors['wind_speed'] > 10:
            delay += 10

        # Precipitation impact
        if factors['precipitation'] > 10:
            delay += 25
        elif factors['precipitation'] > 2:
            delay += 10

        # Temperature impact
        if factors['temperature'] < 0:
            delay += 20
        elif factors['temperature'] > 30:
            delay += 10

        # Traffic impact
        delay += factors['traffic_load'] * 30

        # Road type adjustment
        delay *= factors['road_type_factor']

        return max(0, min(delay, 120))  # Cap at 2 hours

    def train(self):
        """
        Train the model using simple linear regression with synthetic data.
        """
        print("Training delay prediction model...")

        # Generate training data
        X, y = self.generate_training_data(2000)

        # Add intercept term
        X_intercept = np.column_stack([np.ones(len(X)), X])

        # Solve for weights using normal equation: w = (X^T X)^-1 X^T y
        XTX = X_intercept.T @ X_intercept
        XTX_inv = np.linalg.inv(XTX)
        weights = XTX_inv @ X_intercept.T @ y

        self.bias = weights[0]
        self.weights = weights[1:]

        print("Model trained successfully!")
        print(f"Bias: {self.bias:.4f}")
        print(f"Weights: {dict(zip(self.feature_names, self.weights))}")

    def predict(self, features: Dict) -> float:
        """
        Make a delay prediction based on input features.
        """

        if self.weights is None:
            # Fallback to rule-based logic if model not loaded
            return self._calculate_delay_from_factors(features)

        try:
            # Extract features in the correct order
            feature_values = [features[name] for name in self.feature_names]
            prediction = self.bias + np.dot(self.weights, feature_values)
            return max(0, prediction)
        except KeyError as e:
            print(f"Missing feature: {e}")
            # Fallback to rule-based
            return self._calculate_delay_from_factors(features)

    def save_model(self):
        """Save the trained model to disk."""
        model_data = {
            'weights': self.weights,
            'bias': self.bias,
            'feature_names': self.feature_names,
            'trained_at': datetime.now().isoformat()
        }

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Model saved to {self.model_path}")

    def load_model(self) -> bool:
        """Load the trained model from disk."""
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)

            self.weights = model_data['weights']
            self.bias = model_data['bias']
            self.feature_names = model_data['feature_names']

            print(f"Model loaded from {self.model_path}")
            return True
        except FileNotFoundError:
            print(f"Model file not found: {self.model_path}")
            return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def ensure_model_exists(self):
        """Ensure a trained model exists, train if necessary."""
        if not self.load_model():
            print("No saved model found, training new model...")
            self.train()
            self.save_model()


def get_delays_predictor():
    """
    Factory function to get a configured DelayPredictor instance.
    """
    predictor = DelayPredictor()
    predictor.ensure_model_exists()
    return predictor


if __name__ == "__main__":
    # Standalone training/testing
    predictor = DelayPredictor()
    predictor.train()
    predictor.save_model()

    # Test prediction
    test_features = {
        'visibility': 8000,
        'wind_speed': 5.0,
        'precipitation': 1.0,
        'temperature': 20.0,
        'traffic_load': 0.7,
        'road_type_factor': 1.0
    }

    prediction = predictor.predict(test_features)
    print(f"Test prediction: {prediction:.2f} minutes delay")
