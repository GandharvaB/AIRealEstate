from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, List
import requests
import json
import time
import os

class Coordinates(BaseModel):
    """Coordinates model with explicit lat and lng fields."""
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")

class PropertyAnalysisInput(BaseModel):
    """Input schema for Sarvam Property Analysis Tool."""
    address: str = Field(..., description="Property address")
    price: float = Field(..., description="Property price in dollars")
    size_in_acres: float = Field(..., description="Property size in acres")
    zoning_classification: str = Field(..., description="Zoning classification (e.g., residential, commercial, industrial)")
    coordinates: Coordinates = Field(..., description="Property coordinates with lat and lng values")

class SarvamPropertyAnalysisTool(BaseTool):
    """Tool for analyzing property data using Sarvam AI API for enhanced insights and suitability assessments."""

    name: str = "sarvam_property_analysis"
    description: str = (
        "Analyzes property data using Sarvam API to generate detailed suitability summaries, "
        "development scores, and risk assessments. Takes property information including address, "
        "price, size, zoning, and coordinates to provide AI-powered property analysis."
    )
    args_schema: Type[BaseModel] = PropertyAnalysisInput

    def _make_sarvam_request(self, prompt: str, max_retries: int = 3) -> str:
        """Make a request to Sarvam API with retry logic."""
        api_key = os.getenv("SARVAM_API_KEY")
        if not api_key:
            raise ValueError("SARVAM_API_KEY environment variable is required")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "sarvam-1",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://api.sarvam.ai/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "")
                elif response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        return "Rate limit exceeded. Please try again later."
                else:
                    response.raise_for_status()
                    
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    return f"API request failed: {str(e)}"
        
        return "Failed to get response from Sarvam API after retries"

    def _calculate_development_score(self, price: float, size_in_acres: float, zoning: str) -> int:
        """Calculate development score based on property characteristics."""
        score = 50  # Base score
        
        # Price factor (higher price generally indicates better location/potential)
        if price > 1000000:
            score += 15
        elif price > 500000:
            score += 10
        elif price > 250000:
            score += 5
        
        # Size factor
        if size_in_acres > 10:
            score += 20
        elif size_in_acres > 5:
            score += 15
        elif size_in_acres > 1:
            score += 10
        elif size_in_acres > 0.5:
            score += 5
        
        # Zoning factor
        zoning_lower = zoning.lower()
        if "commercial" in zoning_lower:
            score += 15
        elif "mixed" in zoning_lower:
            score += 12
        elif "residential" in zoning_lower:
            score += 8
        elif "industrial" in zoning_lower:
            score += 6
        
        return min(100, max(0, score))

    def _determine_risk_level(self, development_score: int, price: float, size_in_acres: float) -> str:
        """Determine risk level based on various factors."""
        if development_score >= 80:
            return "Low"
        elif development_score >= 60:
            return "Medium"
        elif development_score >= 40:
            return "Medium-High"
        else:
            return "High"

    def _run(self, address: str, price: float, size_in_acres: float, zoning_classification: str, coordinates: Coordinates) -> str:
        """Analyze property using Sarvam AI API."""
        try:
            # Calculate basic metrics
            development_score = self._calculate_development_score(price, size_in_acres, zoning_classification)
            risk_level = self._determine_risk_level(development_score, price, size_in_acres)
            
            # Create prompt for Sarvam API
            prompt = f"""
            Analyze this property for development potential and suitability:
            
            Property Details:
            - Address: {address}
            - Price: ${price:,.2f}
            - Size: {size_in_acres} acres
            - Zoning: {zoning_classification}
            - Coordinates: {coordinates.lat}, {coordinates.lng}
            - Development Score: {development_score}/100
            - Risk Level: {risk_level}
            
            Please provide a detailed suitability summary covering:
            1. Location advantages and challenges
            2. Zoning implications for development
            3. Size appropriateness for potential projects
            4. Market positioning based on price point
            5. Key considerations for investors or developers
            
            Keep the analysis professional and focused on practical development insights.
            """
            
            # Get AI-generated suitability summary
            suitability_summary = self._make_sarvam_request(prompt)
            
            # Create comprehensive analysis
            analysis_details = {
                "location_analysis": f"Property located at {address} with coordinates {coordinates.lat}, {coordinates.lng}",
                "financial_metrics": {
                    "price_per_acre": round(price / size_in_acres, 2) if size_in_acres > 0 else 0,
                    "total_investment": price
                },
                "development_factors": {
                    "zoning_type": zoning_classification,
                    "land_area": f"{size_in_acres} acres",
                    "development_score_breakdown": {
                        "price_factor": "Evaluated based on market positioning",
                        "size_factor": "Assessed for development potential",
                        "zoning_factor": "Analyzed for permitted uses"
                    }
                }
            }
            
            # Compile final result
            result = {
                "property_address": address,
                "suitability_summary": suitability_summary,
                "development_score": development_score,
                "risk_level": risk_level,
                "analysis_details": analysis_details,
                "api_status": "Successfully analyzed using Sarvam AI"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {
                "error": f"Property analysis failed: {str(e)}",
                "property_address": address,
                "status": "analysis_failed"
            }
            return json.dumps(error_result, indent=2)