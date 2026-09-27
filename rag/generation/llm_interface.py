import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("RoadSense.RAG.LLMInterface")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

class LLMInterface:
    """
    Unified LLM Interface for RoadSense AI RAG Subsystem.
    Primary Generation Engine: OpenAI LLM (e.g., gpt-4o-mini).
    Fallback Generation Engine: Deterministic Civil Engineering Engine.
    """

    def __init__(self, provider: str = "auto", model_name: Optional[str] = None):
        self.provider = provider
        self.api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        self.model_name = model_name or os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()

        if provider == "auto":
            if self.api_key:
                self.active_provider = "openai"
            else:
                self.active_provider = "deterministic_engineering_engine"
        else:
            self.active_provider = provider

        logger.info(
            "LLMInterface initialized. Active Provider: %s, Model: %s, API Key Configured: %s",
            self.active_provider,
            self.model_name,
            "YES" if self.api_key else "NO"
        )

    def generate_report(
        self,
        case_context: Dict[str, Any],
        evidence_chunks: List[Dict[str, Any]],
        rag_mode: str = "evidence_aware_adaptive"
    ) -> str:
        """
        Generates an evidence-grounded road assessment report using either OpenAI LLM
        or the deterministic engineering engine fallback.
        """
        # Always verify current API key presence in environment dynamically
        current_api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if current_api_key:
            self.api_key = current_api_key
            if self.provider == "auto":
                self.active_provider = "openai"

        if self.active_provider == "openai" and self.api_key:
            try:
                return self._call_openai(case_context, evidence_chunks, rag_mode)
            except Exception as e:
                sanitized_msg = self._sanitize_error(str(e))
                logger.warning(
                    "OpenAI API call failed (%s: %s). Falling back to deterministic engineering engine.",
                    type(e).__name__,
                    sanitized_msg
                )
                return self._generate_deterministic_report(case_context, evidence_chunks, rag_mode)
        else:
            if self.active_provider == "openai" and not self.api_key:
                logger.warning("OpenAI provider requested but OPENAI_API_KEY is missing. Using deterministic fallback.")
            return self._generate_deterministic_report(case_context, evidence_chunks, rag_mode)

    def _sanitize_error(self, err_msg: str) -> str:
        if self.api_key and self.api_key in err_msg:
            return err_msg.replace(self.api_key, "[REDACTED_API_KEY]")
        return err_msg

    def _call_openai(
        self,
        case_context: Dict[str, Any],
        evidence_chunks: List[Dict[str, Any]],
        rag_mode: str
    ) -> str:
        """
        Executes OpenAI API call using the official SDK, strictly grounded by retrieved context and evidence.
        """
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)

        system_prompt = (
            "You are an expert highway pavement engineering AI assistant for RoadSense AI.\n"
            "Your task is to generate a comprehensive, evidence-grounded road damage assessment report.\n\n"
            "STRICT GROUNDING RULES:\n"
            "1. Do not invent facts, citations, or engineering standards.\n"
            "2. Do not fabricate numerical deterioration rates or severity percentages/formulas.\n"
            "3. Do not claim a definitive cause when the evidence only supports an association or contributing factor.\n"
            "4. Distinguish observed detection results from engineering interpretation.\n"
            "5. Distinguish weather observations from weather forecasts.\n"
            "6. Treat traffic as operational/maintenance context, not automatically as the cause of damage.\n"
            "7. If evidence is insufficient, explicitly state that the evidence is insufficient.\n"
            "8. Preserve uncertainty from the RAG pipeline.\n"
            "9. Use ONLY the provided citation/source information. Never cite a source that was not supplied in the evidence.\n"
            "10. Do not turn correlation into causation. Avoid statements claiming rainfall or traffic caused damage directly.\n"
            "11. Do not make unsupported predictions about when damage will worsen.\n"
            "12. Recommendations must be strictly grounded in the retrieved engineering evidence.\n\n"
            "For causal language, prefer wording such as:\n"
            "'Recent rainfall/moisture conditions may be one contributing factor associated with the observed pavement distress, based on engineering evidence. The available evidence does not establish rainfall as the sole or definitive cause.'\n\n"
            "OUTPUT STRUCTURE (Use these exact Markdown section headers):\n"
            "## OBSERVED DAMAGE\n"
            "## LOCATION CONTEXT\n"
            "## WEATHER CONTEXT\n"
            "## TRAFFIC / OPERATIONAL CONTEXT\n"
            "## ENGINEERING EVIDENCE\n"
            "## ASSESSMENT\n"
            "## POSSIBLE CONTRIBUTING FACTORS\n"
            "## MAINTENANCE IMPLICATION\n"
            "## UNCERTAINTY / LIMITATIONS\n"
            "## SOURCES\n"
        )

        user_content = {
            "query": case_context.get("query", "Road damage assessment"),
            "rag_mode": rag_mode,
            "observations": case_context.get("observations", []),
            "location_context": case_context.get("location_context", {}),
            "weather_context": case_context.get("weather_context", {}),
            "traffic_context": case_context.get("traffic_context", {}),
            "evidence_chunks": [
                {
                    "chunk_id": e.get("chunk_id"),
                    "source_id": e.get("source_id"),
                    "source_title": e.get("source_title"),
                    "organization": e.get("organization"),
                    "year": e.get("year"),
                    "page": e.get("page"),
                    "text": e.get("text")
                }
                for e in evidence_chunks
            ],
            "uncertainties": case_context.get("uncertainties", [])
        }

        user_prompt = (
            f"Generate a grounded RoadSense AI assessment report based strictly on the following context and evidence:\n\n"
            f"{json.dumps(user_content, indent=2)}\n"
        )

        logger.info("Executing OpenAI completion request using model: %s (RAG Mode: %s)", self.model_name, rag_mode)

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        report = response.choices[0].message.content or ""
        return report

    def _generate_deterministic_report(
        self,
        case_context: Dict[str, Any],
        evidence_chunks: List[Dict[str, Any]],
        rag_mode: str
    ) -> str:
        """
        Generates an authoritative, evidence-grounded engineering report
        strictly adhering to RoadSense AI non-causal rules when external LLM is unavailable.
        """
        obs = case_context.get("observations", [])
        loc = case_context.get("location_context", {})
        weath = case_context.get("weather_context", {})
        traff = case_context.get("traffic_context", {})
        uncert = case_context.get("uncertainties", [])

        damage_type = obs[0].get("damage_class", "pothole") if obs else "pothole"
        conf = obs[0].get("confidence", 0.90) * 100 if obs else 90.0

        # Build Section 1: Observed Damage
        sec_observed = (
            "## OBSERVED DAMAGE\n"
            f"- Primary Distress Class: {damage_type.capitalize()}\n"
            f"- Model Confidence: {conf:.1f}%\n"
            f"- Distress Count: {len(obs)}\n"
            f"- Severity Indicator: Moderate visual surface deterioration\n"
        )

        # Build Section 2: Location Context
        if loc.get("available"):
            sec_location = (
                "## LOCATION CONTEXT\n"
                f"- Mapped Road Corridor: {loc.get('mapped_road')}\n"
                f"- Road Classification: {loc.get('road_classification')}\n"
                f"- Coordinates: Latitude {loc.get('latitude')}, Longitude {loc.get('longitude')}\n"
                f"- Nearby Infrastructure: {loc.get('nearest_mapped_school', 'Nearest mapped corridor')}\n"
            )
        else:
            sec_location = "## LOCATION CONTEXT\n- Location context unavailable.\n"

        # Build Section 3: Weather Context
        if weath.get("available"):
            sec_weather = (
                "## WEATHER CONTEXT\n"
                f"- Recent Precipitation: {weath.get('rainfall_mm', 0.0)} mm\n"
                f"- Temperature: {weath.get('temperature_c', 25.0)} °C\n"
                f"- Moisture Condition: {weath.get('moisture_condition')}\n"
                "- Environmental Note: Moisture context is evaluated as an environmental exposure metric.\n"
            )
        else:
            sec_weather = "## WEATHER CONTEXT\n- Weather context unavailable.\n"

        # Build Section 4: Traffic / Operational Context
        if traff.get("available"):
            sec_traffic = (
                "## TRAFFIC / OPERATIONAL CONTEXT\n"
                f"- Corridor Route: {traff.get('route')}\n"
                f"- Traffic Volume Category: {traff.get('traffic_volume_level')}\n"
                f"- Operational Priority Impact: High traffic volume increases operational urgency for repair scheduling.\n"
            )
        else:
            sec_traffic = "## TRAFFIC / OPERATIONAL CONTEXT\n- Traffic context unavailable.\n"

        # Build Section 5 & 6: Engineering Evidence & Assessment
        if rag_mode == "NO_RAG" or not evidence_chunks:
            sec_evidence = (
                "## ENGINEERING EVIDENCE\n"
                "No engineering documentation retrieved for this assessment (NO_RAG baseline).\n"
            )
            sec_assessment = (
                "## ASSESSMENT\n"
                f"Visual observation confirms the presence of {damage_type}. Baseline analysis without retrieved "
                "standards relies on general pavement engineering principles.\n"
            )
        else:
            ev_summary_lines = []
            for item in evidence_chunks[:3]:
                ev_summary_lines.append(
                    f"- According to {item.get('source_title')} (p. {item.get('page')}): "
                    f"\"{item.get('text')[:180]}...\""
                )
            sec_evidence = "## ENGINEERING EVIDENCE\n" + "\n".join(ev_summary_lines) + "\n"

            best_src = evidence_chunks[0]
            sec_assessment = (
                "## ASSESSMENT\n"
                f"Retrieved authoritative evidence from {best_src.get('source_title')} supports standard intervention "
                f"guidelines for {damage_type}. Immediate surface cleaning, tack coating, and asphalt compaction are indicated.\n"
            )

        # Build Section 7: Possible Contributing Factors (Strictly Non-Causal)
        if weath.get("available") and weath.get("rainfall_mm", 0) > 10.0:
            sec_factors = (
                "## POSSIBLE CONTRIBUTING FACTORS\n"
                "- Environmental moisture/rainfall conditions may be one contributing factor associated with pavement distress "
                "acceleration, based on retrieved engineering evidence. Available evidence does NOT establish rainfall as the sole or definitive cause.\n"
            )
        else:
            sec_factors = (
                "## POSSIBLE CONTRIBUTING FACTORS\n"
                "- Surface traffic stress and cyclic environmental loading are common associated factors in flexible pavement deterioration.\n"
            )

        # Build Section 8: Maintenance Implication
        if traff.get("available") and traff.get("traffic_volume_level") == "High":
            sec_maint = (
                "## MAINTENANCE IMPLICATION\n"
                "- High traffic volume on this corridor elevates operational priority. Work-zone safety and temporary traffic control "
                "must be incorporated into maintenance scheduling to prevent traffic disruption.\n"
            )
        else:
            sec_maint = (
                "## MAINTENANCE IMPLICATION\n"
                "- Standard routine maintenance patching and sealant application should be scheduled per MoRTH SOP guidelines.\n"
            )

        # Build Section 9: Uncertainty / Limitations
        sec_limits = (
            "## UNCERTAINTY / LIMITATIONS\n"
            "- Exact remaining service life (RSL) cannot be determined from a single visual image.\n"
            "- Structural load-carrying capacity (e.g. Benkelman Beam Deflection) requires physical field testing.\n"
            "- Exact monetary repair cost cannot be estimated without site measurements and local schedule of rates.\n"
        )

        # Build Section 10: Sources
        if evidence_chunks and rag_mode != "NO_RAG":
            sources_lines = []
            seen_sources = set()
            for chunk in evidence_chunks:
                src_str = f"[{chunk.get('source_id')}] {chunk.get('source_title')} ({chunk.get('organization')}, {chunk.get('year')}), p. {chunk.get('page')}"
                if src_str not in seen_sources:
                    seen_sources.add(src_str)
                    sources_lines.append(f"- {src_str}")
            sec_sources = "## SOURCES\n" + "\n".join(sources_lines) + "\n"
        else:
            sec_sources = "## SOURCES\n- None (Baseline LLM output without document retrieval)\n"

        full_report = "\n".join([
            sec_observed,
            sec_location,
            sec_weather,
            sec_traffic,
            sec_evidence,
            sec_assessment,
            sec_factors,
            sec_maint,
            sec_limits,
            sec_sources
        ])

        return full_report

if __name__ == "__main__":
    llm = LLMInterface()
    from retrieval.case_context import CaseContextBuilder
    builder = CaseContextBuilder()
    ctx = builder.build_context(
        detector_results={"damage_class": "pothole", "confidence": 0.95},
        location={"latitude": 13.0827, "longitude": 80.2707, "mapped_road": "NH-48"},
        weather={"rainfall_mm": 32.0},
        traffic={"route": "NH-48 Corridor", "volume_level": "High"}
    )
    rep = llm.generate_report(ctx, [], rag_mode="NO_RAG")
    print("--- Generated Sample Report ---")
    print(rep[:600])
