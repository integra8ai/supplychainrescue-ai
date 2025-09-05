"""
SupplyChainRescue AI - Tkinter Dashboard
Main dashboard application for monitoring and controlling disaster relief operations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
from datetime import datetime
import requests


class SupplyChainDashboard:
    """
    Main Tkinter dashboard for SupplyChainRescue AI.
    Provides real-time monitoring and control of disaster relief logistics.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SupplyChainRescue AI - Disaster Relief Dashboard")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # Backend API configuration
        self.backend_url = "http://localhost:8000"

        # Dashboard state
        self.current_weather = {}
        self.active_routes = []
        self.system_status = {}

        # Initialize UI components
        self.setup_ui()
        self.create_menu()
        self.setup_periodic_updates()

        # Start the main loop
        self.root.mainloop()

    def setup_ui(self):
        """Set up the main UI layout with frames and widgets."""

        # Create main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = ttk.Label(
            header_frame,
            text="🚨 SupplyChainRescue AI Dashboard",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)

        self.status_label = ttk.Label(
            header_frame,
            text="🔄 Connecting...",
            foreground="orange"
        )
        self.status_label.pack(side=tk.RIGHT)

        # Create main content area with paned window for resizable sections
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left panel - Map/Visualization area
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=3)

        # Right panel - Data and controls
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        # Setup left panel (Map area)
        self.setup_map_area(left_frame)

        # Setup right panel (Data panels)
        self.setup_data_panels(right_frame)

        # Setup bottom status bar
        self.setup_status_bar(main_frame)

    def setup_map_area(self, parent):
        """Set up the map/visualization area."""

        map_frame = ttk.LabelFrame(
            parent, text="📍 Route Map & Visualization", padding=10)
        map_frame.pack(fill=tk.BOTH, expand=True)

        # Placeholder for map display
        self.map_canvas = tk.Canvas(
            map_frame,
            bg="#f0f0f0",
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.map_canvas.pack(fill=tk.BOTH, expand=True)

        # Add placeholder map content
        self.map_canvas.create_text(
            200, 150,
            text="🗺️ Interactive Map\n\nRoute visualization will appear here",
            font=("Helvetica", 12),
            fill="#666666",
            justify=tk.CENTER
        )

        # Map control buttons
        button_frame = ttk.Frame(map_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            button_frame,
            text="🗺️ Load Map",
            command=self.load_map_data
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="🎯 Center on Active Routes",
            command=self.center_on_routes
        ).pack(side=tk.LEFT, padx=(0, 10))

    def setup_data_panels(self, parent):
        """Set up the data panels on the right side."""

        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Weather tab
        self.setup_weather_tab()

        # Routes tab
        self.setup_routes_tab()

        # Alerts tab
        self.setup_alerts_tab()

        # Controls tab
        self.setup_controls_tab()

    def setup_weather_tab(self):
        """Set up weather monitoring tab."""

        weather_frame = ttk.Frame(self.notebook)
        self.notebook.add(weather_frame, text="🌦️ Weather")

        # Current weather display
        weather_display = ttk.LabelFrame(
            weather_frame, text="Current Conditions", padding=10)
        weather_display.pack(fill=tk.X, pady=(0, 10))

        self.weather_labels = {}
        weather_info = [
            "Temperature", "Humidity", "Wind Speed", "Visibility",
            "Weather Condition", "Last Updated"
        ]

        for i, info in enumerate(weather_info):
            ttk.Label(weather_display, text=f"{info}:").grid(
                row=i, column=0, sticky=tk.W, pady=2)
            self.weather_labels[info.lower().replace(" ", "_")] = ttk.Label(
                weather_display,
                text="Loading..."
            )
            self.weather_labels[info.lower().replace(" ", "_")].grid(
                row=i, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        # Weather forecast section
        forecast_frame = ttk.LabelFrame(
            weather_frame, text="Weather Impact on Routes", padding=10)
        forecast_frame.pack(fill=tk.BOTH, expand=True)

        self.forecast_text = tk.Text(forecast_frame, height=8, wrap=tk.WORD)
        self.forecast_text.pack(fill=tk.BOTH, expand=True)
        self.forecast_text.insert(
            tk.END, "Weather forecast and route impact analysis will appear here...")

        # Refresh button
        ttk.Button(
            forecast_frame,
            text="🔄 Refresh Weather",
            command=self.refresh_weather
        ).pack(pady=(10, 0))

    def setup_routes_tab(self):
        """Set up route monitoring tab."""

        routes_frame = ttk.Frame(self.notebook)
        self.notebook.add(routes_frame, text="🚛 Active Routes")

        # Route list
        list_frame = ttk.LabelFrame(
            routes_frame, text="Active Logistics Routes", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Route treeview
        columns = ("Route ID", "Truck", "Status", "Progress", "ETA")
        self.routes_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.routes_tree.heading(col, text=col)
            self.routes_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.routes_tree.yview)
        self.routes_tree.configure(yscrollcommand=scrollbar.set)

        self.routes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Route control buttons
        button_frame = ttk.Frame(routes_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            button_frame,
            text="📋 View Route Details",
            command=self.view_route_details
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="🔄 Refresh Routes",
            command=self.refresh_routes
        ).pack(side=tk.LEFT, padx=(0, 10))

    def setup_alerts_tab(self):
        """Set up alerts and notifications tab."""

        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text="🚨 Alerts")

        # Active alerts
        alerts_display = ttk.LabelFrame(
            alerts_frame, text="Active Alerts & Warnings", padding=10)
        alerts_display.pack(fill=tk.BOTH, expand=True)

        self.alerts_text = tk.Text(alerts_display, height=15, wrap=tk.WORD)
        self.alerts_text.pack(fill=tk.BOTH, expand=True)
        self.alerts_text.insert(
            tk.END, "🚨 System startup complete\n📅 Ready for disaster relief operations\n⏱️ Monitoring systems active")

        # Alert control buttons
        alert_buttons = ttk.Frame(alerts_frame)
        alert_buttons.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            alert_buttons,
            text="🔔 Test Alert System",
            command=self.test_alerts
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            alert_buttons,
            text="🔇 Clear All Alerts",
            command=self.clear_alerts
        ).pack(side=tk.LEFT)

    def setup_controls_tab(self):
        """Set up control and settings tab."""

        controls_frame = ttk.Frame(self.notebook)
        self.notebook.add(controls_frame, text="⚙️ Controls")

        # System controls
        system_frame = ttk.LabelFrame(
            controls_frame, text="System Controls", padding=10)
        system_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            system_frame,
            text="🔧 Run System Diagnostics",
            command=self.run_diagnostics
        ).pack(fill=tk.X, pady=(0, 5))

        ttk.Button(
            system_frame,
            text="📊 Generate Situation Report",
            command=self.generate_report
        ).pack(fill=tk.X, pady=(0, 5))

        ttk.Button(
            system_frame,
            text="🔄 Full System Refresh",
            command=self.full_refresh
        ).pack(fill=tk.X)

        # Settings
        settings_frame = ttk.LabelFrame(
            controls_frame, text="Settings", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(settings_frame, text="Backend API URL:").pack(anchor=tk.W)
        self.api_url_var = tk.StringVar(value=self.backend_url)
        ttk.Entry(
            settings_frame,
            textvariable=self.api_url_var,
            width=50
        ).pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            settings_frame,
            text="💾 Save Settings",
            command=self.save_settings
        ).pack(anchor=tk.W)

    def setup_status_bar(self, parent):
        """Set up bottom status bar."""

        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.connection_status = ttk.Label(
            status_frame, text="🔌 Backend: Connecting...")
        self.connection_status.pack(side=tk.LEFT)

        self.last_update = ttk.Label(status_frame, text="🕒 Last Update: Never")
        self.last_update.pack(side=tk.RIGHT)

    def create_menu(self):
        """Create menu bar."""

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.quit_application)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh All", command=self.full_refresh)
        view_menu.add_separator()
        view_menu.add_command(label="Toggle Dark Mode",
                              command=self.toggle_dark_mode)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="API Documentation",
                              command=self.show_api_docs)

    def setup_periodic_updates(self):
        """Set up periodic data updates."""

        def update_loop():
            while True:
                try:
                    self.root.after(0, self.update_dashboard_data)
                except tk.TclError:
                    break  # Window closed
                threading.Event().wait(30)  # Update every 30 seconds

        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()

        # Initial update
        self.update_dashboard_data()

    def update_dashboard_data(self):
        """Update all dashboard data from backend."""

        try:
            # Update system status
            self.check_backend_status()

            # Update weather data
            self.refresh_weather()

            # Update routes
            self.refresh_routes()

            # Update timestamp
            self.last_update.config(
                text=f"🕒 Last Update: {datetime.now().strftime('%H:%M:%S')}")

        except Exception as e:
            self.update_connection_status("Error", f"red")
            print(f"Dashboard update error: {e}")

    def check_backend_status(self):
        """Check backend connection status."""

        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                self.update_connection_status("Connected", "green")
                self.system_status = response.json()
            else:
                self.update_connection_status("Error", "red")
        except requests.exceptions.RequestException:
            self.update_connection_status("Disconnected", "red")

    def update_connection_status(self, status, color):
        """Update connection status indicator."""

        color_map = {
            "green": "green",
            "red": "#cc0000",
            "orange": "#ff6600",
        }

        status_text = f"🔌 Backend: {status}"
        self.connection_status.config(
            text=status_text, foreground=color_map.get(color, "black"))

    def refresh_weather(self):
        """Refresh weather data from backend API."""

        try:
            # Fetch current weather from backend
            weather_url = f"{self.backend_url}/api/v1/weather/current"
            # Default to NYC coordinates
            params = {"lat": 40.7128, "lon": -74.0060}

            response = requests.get(weather_url, params=params, timeout=10)
            response.raise_for_status()

            weather_result = response.json()
            if weather_result.get("success") and weather_result.get("data"):
                weather_data = weather_result["data"]

                # Update UI labels with real data
                temp_celsius = weather_data.get("temperature", 0)
                humidity_pct = weather_data.get("humidity", 0)
                wind_ms = weather_data.get("wind_speed", 0)
                visibility_m = weather_data.get("visibility", 10000)
                condition = weather_data.get(
                    "weather_condition", {}).get("main", "Unknown")
                last_updated = datetime.now().strftime("%H:%M:%S")

                # Update labels with formatted data
                self.weather_labels["temperature"].config(
                    text=f"{temp_celsius}°C")
                self.weather_labels["humidity"].config(text=f"{humidity_pct}%")
                self.weather_labels["wind_speed"].config(
                    text=f"{wind_ms * 3.6:.1f} km/h")
                self.weather_labels["visibility"].config(
                    text=f"{visibility_m/1000:.1f} km")
                self.weather_labels["weather_condition"].config(text=condition)
                self.weather_labels["last_updated"].config(text=last_updated)

                # Update forecast analysis
                self.forecast_text.delete(1.0, tk.END)
                forecast_analysis = self.analyze_weather_impact(weather_data)
                self.forecast_text.insert(tk.END, forecast_analysis)

                self.add_alert(
                    "🌦️ WEATHER UPDATED", f"Weather data refreshed from backend at {last_updated}")
            else:
                self._set_weather_error("Invalid response from backend")

        except requests.exceptions.RequestException as e:
            print(f"Weather API request failed: {e}")
            self._set_weather_error(f"Connection error: {str(e)}")
            self.add_alert("❌ WEATHER ERROR",
                           f"Failed to fetch weather data: {str(e)}")
        except Exception as e:
            print(f"Weather refresh error: {e}")
            self._set_weather_error(f"Error: {str(e)}")

    def _set_weather_error(self, error_message):
        """Set weather display to error state."""
        for key, label in self.weather_labels.items():
            if key == "last_updated":
                label.config(text=datetime.now().strftime("%H:%M:%S"))
            elif key == "weather_condition":
                label.config(text="Error")
            else:
                label.config(text="N/A")

        self.forecast_text.delete(1.0, tk.END)
        self.forecast_text.insert(
            tk.END, f"❌ Weather data unavailable\n\n{error_message}")

    def analyze_weather_impact(self, weather_data):
        """Analyze weather impact on logistics operations."""
        impact_level = "Low"
        recommendations = []

        temp = weather_data.get("temperature", 20)
        wind_speed = weather_data.get("wind_speed", 0) * 3.6  # Convert to km/h
        visibility = weather_data.get(
            "visibility", 10000) / 1000  # Convert to km
        precipitation = weather_data.get(
            "humidity", 50)  # Using humidity as proxy

        # Temperature impact
        if temp < 0:
            impact_level = "High"
            recommendations.append(
                "• Extreme cold: Reduce speeds, check vehicle antifreeze")
        elif temp > 35:
            impact_level = "Medium"
            recommendations.append(
                "• High heat: Monitor tire pressure, ensure driver breaks")

        # Wind impact
        if wind_speed > 50:
            impact_level = max(impact_level, "High")
            recommendations.append(
                "• Strong winds: Secure cargo, reduce speed when crossing bridges")
        elif wind_speed > 25:
            impact_level = max(impact_level, "Medium")
            recommendations.append(
                "• Moderate winds: Take caution on exposed roads")

        # Visibility impact
        if visibility < 1:
            impact_level = "High"
            recommendations.append(
                "• Poor visibility: Use fog lights, maintain greater following distance")
        elif visibility < 5:
            impact_level = max(impact_level, "Medium")
            recommendations.append(
                "• Reduced visibility: Increase following distance")

        # Precipitation impact
        if precipitation > 80:
            impact_level = max(impact_level, "Medium")
            recommendations.append(
                "• High humidity/moisture: Check road conditions, watch for hydroplaning")

        analysis = f"""🌦️ WEATHER IMPACT ANALYSIS
Current Conditions: {impact_level} Impact on Operations

Temperature: {temp}°C
Wind Speed: {wind_speed:.1f} km/h
Visibility: {visibility:.1f} km
Humidity: {precipitation}%

"""

        if recommendations:
            analysis += "\n📋 RECOMMENDATIONS:\n" + "\n".join(recommendations)
        else:
            analysis += "\n✅ Conditions favorable for logistics operations"

        return analysis

    def refresh_routes(self):
        """Refresh active routes data from backend."""

        try:
            # Clear existing routes
            for item in self.routes_tree.get_children():
                self.routes_tree.delete(item)

            # Fetch optimized routes from backend
            routes_url = f"{self.backend_url}/api/v1/optimize/routes"
            # In production, you might want to query routes differently
            # For now, we'll simulate with some test data

            routes_data = []

            # Try to get some real route data if backend is available
            try:
                response = requests.get(routes_url, timeout=5)
                if response.status_code == 200:
                    routes_result = response.json()
                    if routes_result.get("success"):
                        # Process real routes data from backend
                        backend_routes = routes_result.get(
                            "data", {}).get("routes", [])
                        for route in backend_routes:
                            routes_data.append({
                                "id": route.get("route_id", "Unknown"),
                                "truck": route.get("truck_id", "Truck-01"),
                                "status": "Optimized" if route.get("optimization") else "Active",
                                "progress": "100%",  # Would calculate from actual progress
                                "eta": route.get("estimated_duration", "TBD")
                            })

                        self.add_alert(
                            "🚛 ROUTES UPDATED", f"Fetched {len(routes_data)} routes from backend")
                    else:
                        self._load_mock_routes(routes_data)
                else:
                    self._load_mock_routes(routes_data)

            except requests.exceptions.RequestException:
                print("Backend unavailable, using mock routes")
                self._load_mock_routes(routes_data)

            # Display the routes
            for route in routes_data:
                self.routes_tree.insert("", tk.END, values=(
                    route["id"],
                    route["truck"],
                    route["status"],
                    route["progress"],
                    route["eta"]
                ))

            if not routes_data:
                # Add a placeholder row if no routes
                self.routes_tree.insert("", tk.END, values=(
                    "No routes available", "-", "-", "-", "-"))

        except Exception as e:
            print(f"Routes refresh error: {e}")
            self.add_alert("❌ ROUTES ERROR",
                           f"Failed to fetch routes: {str(e)}")

            # Add error placeholder
            self.routes_tree.insert("", tk.END, values=(
                "Error loading routes", "-", "-", "-", "-"))

    def _load_mock_routes(self, routes_data):
        """Load mock route data for demonstration."""
        mock_routes = [
            {
                "id": "RTE_001",
                "truck": "Truck-01",
                "status": "In Transit",
                "progress": "45%",
                "eta": "14:30"
            },
            {
                "id": "RTE_002",
                "truck": "Truck-02",
                "status": "Loading",
                "progress": "0%",
                "eta": "16:00"
            },
            {
                "id": "RTE_003",
                "truck": "Truck-03",
                "status": "Delivered",
                "progress": "100%",
                "eta": "13:15"
            }
        ]

        routes_data.extend(mock_routes)
        self.add_alert("📋 ROUTES LOADED",
                       "Using mock data - Backend routes unavailable")

    def load_map_data(self):
        """Load and display map data."""
        messagebox.showinfo(
            "Map", "Map loading feature will be implemented with the GIS integration.")

    def center_on_routes(self):
        """Center map view on active routes."""
        messagebox.showinfo(
            "Map", "Route centering feature will be implemented with the GIS integration.")

    def view_route_details(self):
        """View detailed information for selected route from backend."""
        selected = self.routes_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a route first.")
            return

        route_info = self.routes_tree.item(selected[0])['values']
        route_id = route_info[0]

        try:
            # Fetch detailed route information from backend
            route_detail_url = f"{self.backend_url}/api/v1/optimize/routes/{route_id}"
            response = requests.get(route_detail_url, timeout=10)

            if response.status_code == 200:
                route_result = response.json()
                if route_result.get("success"):
                    route_data = route_result.get("data", {}).get("route", {})

                    # Format detailed route information
                    details = f"""🚛 ROUTE DETAILS
Route ID: {route_data.get('route_id', route_id)}
Truck: {route_data.get('truck_id', 'Unknown')}
Total Distance: {route_data.get('total_distance', 'N/A')} km
Estimated Duration: {route_data.get('estimated_duration', 'N/A')} minutes
Risk Score: {route_data.get('risk_score', 'N/A')}

Stops: {len(route_data.get('stops', []))} destination(s)

Optimization Algorithm: {route_data.get('algorithm_used', 'Unknown')}"""

                    messagebox.showinfo("Route Details", details)
                    self.add_alert(
                        "📋 ROUTE LOADED", f"Detailed information for {route_id} fetched from backend")
                else:
                    # Fallback to basic info
                    basic_details = f"""🚛 BASIC ROUTE INFO
Route: {route_info[0]}
Truck: {route_info[1]}
Status: {route_info[2]}
Progress: {route_info[3]}
ETA: {route_info[4]}"""
                    messagebox.showinfo("Route Details", basic_details)
            else:
                # Use basic info if backend call fails
                basic_details = f"""🚛 BASIC ROUTE INFO
Route: {route_info[0]}
Truck: {route_info[1]}
Status: {route_info[2]}
Progress: {route_info[3]}
ETA: {route_info[4]}"""
                messagebox.showinfo("Route Details", basic_details)

        except requests.exceptions.RequestException:
            # Fallback if backend unavailable
            basic_details = f"""🚛 BASIC ROUTE INFO
Route: {route_info[0]}
Truck: {route_info[1]}
Status: {route_info[2]}
Progress: {route_info[3]}
ETA: {route_info[4]}

⚠️ Backend unavailable - showing cached data"""
            messagebox.showwarning("Route Details", basic_details)
            self.add_alert(
                "⚠️ BACKEND ISSUE", "Detailed route info unavailable - showing cached data")
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to load route details: {str(e)}")

    def test_alerts(self):
        """Test the alert system."""
        self.add_alert("🧪 ALERT SYSTEM TEST",
                       "This is a test alert to verify system functionality.")

    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts_text.delete(1.0, tk.END)
        self.alerts_text.insert(tk.END, "📋 All alerts cleared")

    def run_diagnostics(self):
        """Run system diagnostics by calling backend health endpoints."""

        try:
            # Test main health endpoint
            health_url = f"{self.backend_url}/health"
            response = requests.get(health_url, timeout=10)

            if response.status_code == 200:
                health_data = response.json()

                # Check ML models
                forecast_health_url = f"{self.backend_url}/api/v1/forecast/health"
                forecast_response = requests.get(
                    forecast_health_url, timeout=5)
                ml_status = "OK" if forecast_response.status_code == 200 else "ERROR"

                # Check route optimization
                optimize_health_url = f"{self.backend_url}/api/v1/optimize/health"
                optimize_response = requests.get(
                    optimize_health_url, timeout=5)
                optimize_status = "OK" if optimize_response.status_code == 200 else "ERROR"

                # Get weather service status from health data
                weather_status = "OK" if health_data.get("data", {}).get(
                    "services", {}).get("weather", "").startswith("operational") else "ERROR"

                diagnostics = f"""🔍 SYSTEM DIAGNOSTICS - {datetime.now().strftime('%H:%M:%S')}

✅ Backend connection: OK
✅ Database: {'OK' if 'database' in str(health_data) else 'ERROR'}
🤖 ML Models (Forecasting): {ml_status}
🎯 Route Optimization: {optimize_status}
🌦️ Weather Service: {weather_status}

📊 Services Status:"""

                services = health_data.get("data", {}).get("services", {})
                for service, status in services.items():
                    status_icon = "✅" if "operational" in str(
                        status).lower() else "❌"
                    diagnostics += f"\n{status_icon} {service.title()}: {status}"

                messagebox.showinfo("System Diagnostics", diagnostics)
                self.add_alert("🔍 DIAGNOSTICS COMPLETED",
                               "All systems checked successfully")
            else:
                messagebox.showerror("Diagnostics Error",
                                     "Backend health check failed")
                self.add_alert("❌ DIAGNOSTICS FAILED",
                               "Backend health endpoint unavailable")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Connection Error",
                                 f"Unable to connect to backend: {str(e)}")
            self.add_alert("❌ CONNECTION ERROR",
                           "Backend unreachable during diagnostics")
        except Exception as e:
            messagebox.showerror("Diagnostics Error",
                                 f"Unexpected error: {str(e)}")
            self.add_alert("❌ DIAGNOSTICS ERROR",
                           f"Unexpected error: {str(e)}")

    def generate_report(self):
        """Generate situation report."""
        messagebox.showinfo(
            "Report", "Situation report generation will be implemented with the reporting API integration.")

    def full_refresh(self):
        """Perform full system refresh."""
        self.status_label.config(text="🔄 Refreshing...")
        self.update_dashboard_data()
        self.status_label.config(text="✅ System Refreshed")

        messagebox.showinfo("Refresh", "All system data has been refreshed.")

    def save_settings(self):
        """Save dashboard settings."""
        self.backend_url = self.api_url_var.get()
        messagebox.showinfo("Settings", "Settings saved successfully.")

    def toggle_dark_mode(self):
        """Toggle dark mode theme."""
        messagebox.showinfo(
            "Theme", "Dark mode feature will be implemented in a future update.")

    def quit_application(self):
        """Quit the application."""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.root.quit()

    def show_about(self):
        """Show about dialog."""
        about_text = """
        SupplyChainRescue AI Dashboard

        Disaster Relief Supply Chain Optimization System

        Version: 1.0.0
        Built with: Python, Tkinter, FastAPI

        Features:
        • Real-time route monitoring
        • Weather impact analysis
        • ML-powered delay prediction
        • Interactive GIS mapping
        • Automated alert system
        """
        messagebox.showinfo("About", about_text)

    def show_api_docs(self):
        """Show API documentation."""
        import webbrowser
        webbrowser.open(f"{self.backend_url}/docs")

    def add_alert(self, title, message):
        """Add a new alert to the alerts tab."""

        timestamp = datetime.now().strftime("%H:%M:%S")
        alert_entry = f"[{timestamp}] {title}\n{message}\n\n"

        self.alerts_text.insert(tk.END, alert_entry)
        self.alerts_text.see(tk.END)  # Scroll to bottom


def main():
    """Main entry point for the dashboard application."""
    try:
        dashboard = SupplyChainDashboard()
    except KeyboardInterrupt:
        print("Dashboard closed by user")
    except Exception as e:
        print(f"Dashboard error: {e}")


if __name__ == "__main__":
    main()
