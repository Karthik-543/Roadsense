def adapt_query(query: str, target_category: str = None) -> str:
    """
    Applies deterministic domain-aware expansion to reformulate initial queries
    when evidence evaluation indicates insufficient initial retrieval context.
    """
    q_lower = query.lower()

    # Distress specific domain expansions (MoRTH / IRC technical terms)
    if "pothole" in q_lower:
        expansion = "pothole bituminous pavement patch repair compaction cold mix hot mix MoRTH guidelines"
    elif "longitudinal" in q_lower or "longitudinal crack" in q_lower:
        expansion = "longitudinal joint cracking crack sealing slurry seal asphalt overlay MoRTH distress terminology"
    elif "transverse" in q_lower or "transverse crack" in q_lower:
        expansion = "transverse thermal cracking crack filling sealing sealant bituminous overlay IRC standard"
    elif "alligator" in q_lower or "fatigue" in q_lower:
        expansion = "alligator fatigue cracking subgrade base structural failure full depth patch rehabilitation"
    elif "crack" in q_lower:
        expansion = "bituminous pavement cracking distress repair maintenance sealing patch"
    elif "weather" in q_lower or "rain" in q_lower or "moisture" in q_lower:
        expansion = "pavement moisture intrusion environmental degradation precipitation subgrade saturation FHWA drainage"
    elif "traffic" in q_lower or "heavy traffic" in q_lower:
        expansion = "high traffic volume roadway preservation work zone traffic management maintenance scheduling operational priority"
    elif "maintenance" in q_lower or "repair" in q_lower:
        expansion = "routine periodic preventive maintenance pavement distress intervention criteria SOP National Highways"
    else:
        expansion = "road pavement distress engineering maintenance inspection standards MoRTH NHAI IRC"

    adapted = f"{query} {expansion}"
    return adapted.strip()

if __name__ == "__main__":
    test_queries = [
        "What repair is suitable for potholes?",
        "How does rain affect pavement?",
        "What are the repair methods for alligator cracking?"
    ]
    for tq in test_queries:
        print(f"Original: '{tq}'\nAdapted:  '{adapt_query(tq)}'\n")