# 🚨 SupplyChainRescue AI

**AI-Powered Disaster Relief Supply Chain Optimization System**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Tkinter](https://img.shields.io/badge/Tkinter-GUI-orange.svg)](https://docs.python.org/3/library/tkinter.html)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT)

## 📋 Overview

SupplyChainRescue AI is a comprehensive disaster relief logistics optimization platform that combines **machine learning**, **real-time weather integration**, **GPS route optimization**, and an **intuitive graphical dashboard** to streamline emergency supply chain operations.

### ✨ Key Features

- 🤖 **Machine Learning**: AI-powered delay prediction using weather and traffic data
- 🌦️ **Weather Integration**: Real-time weather impact analysis for route planning
- 🚛 **Smart Route Optimization**: OR-Tools integration with penalty-based routing
- 🎯 **Real-time Monitoring**: Live dashboard with interactive maps and alerts
- 📊 **Comprehensive Analytics**: Situation reports and performance metrics
- 🔧 **Modular Architecture**: Scalable FastAPI backend with Tkinter frontend

## 🏗️ System Architecture

```
📁 SupplyChainRescue AI/
├── 🚀 Backend (FastAPI)
│   ├── 🌐 API Routes (/api/v1/)
│   │   ├── 🌦️ Weather: Current conditions & forecasts
│   │   ├── 🛣️ Roads: Network data & status monitoring
│   │   └── 🎯 Optimize: Route optimization with OR-Tools
│   ├── 🤖 ML Models: Delay prediction algorithms
│   ├── 💾 Database: SQLite with SQLAlchemy & Alembic
│   └── 🔧 Core: Config, logging, health monitoring
├── 🖥️ Dashboard (Tkinter)
│   ├── 📊 Real-time monitoring interface
│   ├── 🗺️ Interactive route visualization
│   └── 🚨 Alert management system
└── 📚 Documentation & Tests
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js (optional, for advanced dashboard features)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/supplychainrescue-ai.git
   cd supplychainrescue-ai
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**

   ```bash
   # Initialize database tables
   python -c "from backend.db.database import create_tables; create_tables()"

   # Run database migrations (optional, for advanced schema management)
   alembic upgrade head
   ```

4. **Train the ML models** (optional)

   ```bash
   python backend/ml_models/delay_predictor.py
   ```

### Running the Application

1. **Start the backend API server**

   ```bash
   python -m backend.main
   ```

   Server will start on `http://localhost:8000`

2. **Launch the dashboard** (in a new terminal)

   ```bash
   python dashboard/main.py
   ```

3. **Access the API documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## 📡 API Documentation

### 🔗 Base URL: `http://localhost:8000/api/v1`

### 🌦️ Weather Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/weather/current` | Get current weather conditions |
| POST | `/weather/forecast` | Get weather forecast predictions |
| GET | `/weather/historical` | Retrieve historical weather data |
| GET | `/weather/alerts` | Get severe weather alerts |
| GET | `/weather/health` | Weather service health check |

**Example Weather Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/weather/current?lat=40.7128&lon=-74.0060"
```

### 🛣️ Road Network Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/roads/health` | Road network service status |
| GET | `/roads/nodes` | Retrieve road network nodes |
| GET | `/roads/edges` | Get road network edges |
| GET | `/roads/closures` | List active road closures |
| POST | `/roads/closures` | Report new road closure |
| GET | `/roads/status/{road_id}` | Get specific road status |
| GET | `/roads/statistics` | Get road network statistics |

### 🎯 Route Optimization Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/optimize/health` | Optimization service status |
| POST | `/optimize/route` | Optimize logistics routes |
| GET | `/optimize/routes/{route_id}` | Get specific route details |
| GET | `/optimize/algorithms` | List available algorithms |

**Example Route Optimization:**

```json
POST /api/v1/optimize/route
{
  "origin": {"lat": 40.7128, "lng": -74.0060},
  "destinations": [
    {"lat": 40.7505, "lng": -73.9934},
    {"lat": 40.7589, "lng": -73.9851}
  ],
  "trucks": [{"id": "truck_1", "capacity": 100}],
  "avoid_closures": true,
  "optimize_for_weather": true
}
```

### 🤖 Forecasting Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/forecast/health` | Forecasting service status |
| POST | `/forecast/predict` | Generate road delay predictions |
| GET | `/forecast/predictions/{road_id}` | Get predictions for specific road |

### 🏥 Health & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Overall system health |
| GET | `/health/detailed` | Detailed system status |

## 🖥️ Dashboard Usage

### 🚀 Getting Started

1. Launch the dashboard: `python dashboard/main.py`
2. Verify backend connection (green status indicator)
3. Monitor real-time data updates (auto-refreshes every 30 seconds)

### 📊 Dashboard Sections

#### 🌦️ Weather Tab

- **Current Conditions**: Live weather data with impact analysis
- **Route Impact**: AI-generated recommendations based on weather
- **Refresh Controls**: Manual weather data updates

#### 🚛 Routes Tab

- **Active Routes**: Real-time truck and delivery monitoring
- **Route Details**: Click to view detailed optimization data
- **Status Updates**: Live progress and ETA tracking

#### 🚨 Alerts Tab

- **System Alerts**: Real-time notifications and warnings
- **Alert Management**: Clear, test, and manage notifications
- **Log History**: Complete alert history with timestamps

#### ⚙️ Controls Tab

- **System Diagnostics**: Run comprehensive health checks
- **Settings**: Configure backend URL and parameters
- **Report Generation**: Export situation reports

### 🎮 Interactive Features

- **🔄 Auto-refresh**: All data updates automatically every 30 seconds
- **🖱️ Click Controls**: Interactive buttons for manual refreshes
- **⚡ Real-time Alerts**: Instant notifications for system events
- **📊 Live Monitoring**: Continuous backend connectivity checks
- **🛠️ Settings**: Configurable parameters for different environments

## 🧪 Testing

### Running Tests

```bash
# Backend API tests
pytest tests/ -v

# Integration tests
pytest tests/integration/ -v

# Performance tests
pytest tests/performance/ -v
```

### Test Coverage

- ✅ Backend API endpoints
- ✅ ML model predictions
- ✅ Route optimization algorithms
- ✅ Database operations
- ✅ Error handling scenarios

## 🔧 Configuration

### Environment Variables

```bash
# Application settings
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./supplychain_rescue.db

# External APIs
OPENWEATHER_API_KEY=your_openweather_key
OSM_USER_AGENT=SupplyChainRescueAI/1.0

# ML Model settings
MODEL_CACHE_DIR=./models
```

### Advanced Configuration

- **Database**: Supports SQLite (development) and PostgreSQL (production)
- **ML Models**: Configurable model cache and update frequencies
- **Weather API**: Multiple provider support (OpenWeatherMap, etc.)
- **Route Optimization**: Different algorithms and constraints

## 🐛 Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Ensure FastAPI server is running on port 8000
   - Check network connectivity and firewall settings
   - Verify backend URL in dashboard settings

2. **Weather Data Not Loading**
   - Confirm OpenWeather API key is configured
   - Check API rate limits and account status
   - Verify network access to weather services

3. **ML Model Errors**
   - Ensure model file exists: `backend/ml_models/delay_model.pkl`
   - Retrain model: `python backend/ml_models/delay_predictor.py`
   - Check scikit-learn and numpy versions

4. **Database Errors**
   - Verify database file exists: `supplychain_rescue.db`
   - Run migrations: `alembic upgrade head`
   - Check file permissions for SQLite database

### Performance Optimization

- Use PostgreSQL for production deployments
- Implement caching for weather data
- Configure ML model update intervals
- Optimize dashboard refresh frequencies

## 📈 Features Roadmap

- [ ] Advanced GIS mapping integration
- [ ] Mobile dashboard application
- [ ] Real-time truck GPS tracking
- [ ] Multi-vehicle route optimization
- [ ] Emergency response protocols
- [ ] Blockchain integration for supply tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with FastAPI for high-performance APIs
- OR-Tools integration for advanced optimization
- Tkinter for accessible desktop applications
- Machine learning powered by scikit-learn

---

**🚀 Ready to save lives through optimized disaster relief logistics!**
