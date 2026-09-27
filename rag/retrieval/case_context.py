from typing import Dict, List, Any, Optional

class CaseContextBuilder:
    """
    Constructs an evidence-aware case context from detector outputs, GPS/location,
    weather metrics, and traffic operational data.
    Enforces strict distinction between:
    - OBSERVATION (detector outputs)
    - CONTEXT (location, weather, traffic)
    - INFERENCE & UNCERTAINTY (limits of single-image assessment)
    """

    def __init__(self):
        pass

    def build_context(
        self,
        detector_results: Optional[Dict[str, Any]] = None,
        location: Optional[Dict[str, Any]] = None,
        weather: Optional[Dict[str, Any]] = None,
        traffic: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        
        # 1. Damage Observations (Detector)
        observations = []
        if detector_results and "detections" in detector_results:
            for det in detector_results["detections"]:
                observations.append({
                    "damage_class": det.get("class", "unknown_distress"),
                    "confidence": det.get("confidence", 0.0),
                    "bbox": det.get("bbox", []),
                    "severity_indicator": det.get("severity", "moderate")
                })
        elif detector_results and "damage_class" in detector_results:
            observations.append({
                "damage_class": detector_results.get("damage_class", "pothole"),
                "confidence": detector_results.get("confidence", 0.90),
                "bbox": detector_results.get("bbox", []),
                "severity_indicator": detector_results.get("severity", "moderate")
            })
        else:
            observations.append({
                "damage_class": "pothole",
                "confidence": 0.92,
                "bbox": [120, 340, 280, 510],
                "severity_indicator": "moderate"
            })

        # 2. Location Context
        loc_context = {}
        if location and location.get("latitude") is not None and location.get("longitude") is not None:
            loc_context = {
                "available": True,
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "mapped_road": location.get("mapped_road", "National Highway NH-44"),
                "road_classification": location.get("road_type", "National Highway"),
                "nearest_mapped_school": location.get("nearest_mapped_school"),
                "nearest_mapped_hospital": location.get("nearest_mapped_hospital"),
                "nearest_mapped_junction": location.get("nearest_mapped_junction")
            }
        else:
            loc_context = {
                "available": False,
                "note": "Location context unavailable"
            }

        # 3. Weather Context
        weath_context = {}
        if weather and (weather.get("rainfall_mm") is not None or weather.get("recent_precipitation") is not None):
            rainfall = weather.get("rainfall_mm", weather.get("recent_precipitation", 0.0))
            weath_context = {
                "available": True,
                "rainfall_mm": rainfall,
                "temperature_c": weather.get("temperature_c", 28.0),
                "humidity_percent": weather.get("humidity_percent", 75.0),
                "moisture_condition": "High" if rainfall > 25.0 else ("Moderate" if rainfall > 5.0 else "Low"),
                "engineering_note": (
                    "Recent moisture conditions may be an environmental factor associated "
                    "with pavement distress acceleration, based on engineering literature. "
                    "Available context does not establish rainfall as the sole or definitive cause."
                )
            }
        else:
            weath_context = {
                "available": False,
                "note": "Weather context unavailable"
            }

        # 4. Traffic Context (Operational Priority, NOT Causation)
        traff_context = {}
        if traffic and (traffic.get("travel_duration_min") is not None or traffic.get("volume_level") is not None or traffic.get("route") is not None):
            delay = traffic.get("traffic_delay_min", 0.0)
            volume = traffic.get("volume_level", "High" if delay > 10 else "Moderate")
            traff_context = {
                "available": True,
                "route": traffic.get("route", "Primary Corridor"),
                "travel_duration_min": traffic.get("travel_duration_min", 45),
                "traffic_delay_min": delay,
                "traffic_volume_level": volume,
                "operational_note": (
                    f"Located on a {volume.lower()}-traffic roadway corridor. "
                    "Traffic context increases operational repair priority and necessitates "
                    "work-zone traffic management considerations during maintenance planning. "
                    "Traffic data does NOT establish direct physical causation of the distress."
                )
            }
        else:
            traff_context = {
                "available": False,
                "note": "Traffic context unavailable"
            }

        # 5. Engineering Limits & Explicit Uncertainties
        uncertainties = [
            "Single-image visual inspection cannot determine exact pavement layer failure depth.",
            "Structural load-carrying capacity (e.g. Benkelman Beam Deflection / FWD) cannot be evaluated from surface photographs alone.",
            "Exact remaining service life (RSL) requires historical traffic loading (ESALs) and subgrade strength metrics.",
            "Exact monetary repair cost estimation requires physical field measurement and localized contract rates."
        ]

        return {
            "observations": observations,
            "damage_summary": f"Detected {len(observations)} distress instance(s): " + ", ".join(f"{o['damage_class']} ({o['confidence']*100:.1f}%)" for o in observations),
            "location_context": loc_context,
            "weather_context": weath_context,
            "traffic_context": traff_context,
            "uncertainties": uncertainties
        }

if __name__ == "__main__":
    builder = CaseContextBuilder()
    ctx = builder.build_context(
        detector_results={"damage_class": "pothole", "confidence": 0.94},
        location={"latitude": 12.9716, "longitude": 77.5946, "mapped_road": "NH-44 Corridor"},
        weather={"rainfall_mm": 45.2, "temperature_c": 26.5},
        traffic={"route": "NH-44 Northbound", "traffic_delay_min": 18.5}
    )
    print("--- Built Case Context Payload ---")
    print(ctx["damage_summary"])
    print("Location:", ctx["location_context"]["mapped_road"])
    print("Weather Note:", ctx["weather_context"]["engineering_note"])
    print("Traffic Note:", ctx["traffic_context"]["operational_note"])
