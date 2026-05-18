from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, List, Optional
import json
import math

class Coordinates(BaseModel):
    """Coordinates model with lat and lng fields."""
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")

class PropertyData(BaseModel):
    """Input schema for Property Analysis and Scoring Tool."""
    address: str = Field(..., description="Full address of the property")
    price: float = Field(..., description="Property price in USD")
    size_in_acres: float = Field(..., description="Property size in acres")
    zoning_classification: str = Field(..., description="Zoning classification (e.g., Residential, Commercial, Industrial, Mixed-Use)")
    coordinates: Optional[Coordinates] = Field(default=None, description="Property coordinates with lat and lng values")
    
class PropertyAnalysisScoringTool(BaseTool):
    """Tool for analyzing property development potential and investment suitability."""

    name: str = "property_analysis_scoring_tool"
    description: str = (
        "Analyzes property data for development potential and investment suitability. "
        "Calculates composite scores based on multiple factors including location desirability, "
        "price-to-size ratio, zoning advantages, and provides detailed analysis breakdown "
        "with suitability summaries and risk assessments."
    )
    args_schema: Type[BaseModel] = PropertyData

    def _calculate_price_per_acre_score(self, price: float, size_in_acres: float) -> float:
        """Calculate price per acre score (0-100)."""
        try:
            price_per_acre = price / size_in_acres
            
            # Scoring based on typical market ranges
            if price_per_acre <= 5000:
                return 100  # Excellent value
            elif price_per_acre <= 15000:
                return 85   # Good value
            elif price_per_acre <= 30000:
                return 70   # Fair value
            elif price_per_acre <= 50000:
                return 50   # Average value
            elif price_per_acre <= 100000:
                return 30   # High value
            else:
                return 10   # Very expensive
        except ZeroDivisionError:
            return 0

    def _calculate_size_score(self, size_in_acres: float) -> float:
        """Calculate development potential based on size (0-100)."""
        if size_in_acres >= 50:
            return 100  # Large development potential
        elif size_in_acres >= 20:
            return 85   # Good development potential
        elif size_in_acres >= 10:
            return 70   # Moderate development potential
        elif size_in_acres >= 5:
            return 55   # Limited development potential
        elif size_in_acres >= 1:
            return 40   # Small development potential
        else:
            return 20   # Very limited potential

    def _calculate_zoning_score(self, zoning_classification: str) -> float:
        """Calculate zoning advantage score (0-100)."""
        zoning_scores = {
            "mixed-use": 100,
            "commercial": 90,
            "industrial": 85,
            "residential": 75,
            "agricultural": 60,
            "recreational": 50,
            "conservation": 30
        }
        
        zoning_lower = zoning_classification.lower()
        for zone_type, score in zoning_scores.items():
            if zone_type in zoning_lower:
                return score
        return 50  # Default for unknown zoning

    def _calculate_location_score(self, address: str, coordinates: Optional[Coordinates]) -> float:
        """Calculate location desirability score based on address analysis (0-100)."""
        score = 50  # Base score
        address_lower = address.lower()
        
        # Positive location indicators
        positive_keywords = [
            ("downtown", 20), ("city center", 20), ("metro", 15),
            ("highway", 15), ("interstate", 15), ("main street", 10),
            ("business district", 15), ("commercial district", 15),
            ("university", 10), ("airport", 10), ("waterfront", 15),
            ("lake", 10), ("river", 8), ("park", 5)
        ]
        
        # Negative location indicators
        negative_keywords = [
            ("rural", -10), ("remote", -15), ("industrial area", -5),
            ("flood zone", -20), ("wetland", -15)
        ]
        
        # Apply positive adjustments
        for keyword, adjustment in positive_keywords:
            if keyword in address_lower:
                score += adjustment
        
        # Apply negative adjustments
        for keyword, adjustment in negative_keywords:
            if keyword in address_lower:
                score += adjustment
        
        # Ensure score stays within bounds
        return max(0, min(100, score))

    def _calculate_market_trend_score(self, address: str, zoning: str) -> float:
        """Estimate market trend score based on location and zoning (0-100)."""
        base_score = 60
        address_lower = address.lower()
        zoning_lower = zoning.lower()
        
        # Growth area indicators
        growth_indicators = [
            ("tech hub", 20), ("silicon", 15), ("innovation district", 15),
            ("new development", 15), ("planned community", 10),
            ("expansion area", 10), ("growth corridor", 12)
        ]
        
        # Zoning trend adjustments
        if "mixed-use" in zoning_lower:
            base_score += 15
        elif "commercial" in zoning_lower:
            base_score += 10
        
        # Apply growth indicators
        for indicator, adjustment in growth_indicators:
            if indicator in address_lower:
                base_score += adjustment
        
        return max(0, min(100, base_score))

    def _determine_risk_level(self, development_score: float, price_per_acre: float) -> str:
        """Determine investment risk level."""
        if development_score >= 80 and price_per_acre <= 30000:
            return "Low"
        elif development_score >= 70 and price_per_acre <= 50000:
            return "Medium-Low"
        elif development_score >= 60 and price_per_acre <= 75000:
            return "Medium"
        elif development_score >= 50 and price_per_acre <= 100000:
            return "Medium-High"
        else:
            return "High"

    def _generate_suitability_summary(self, property_data: dict, scores: dict, development_score: float, risk_level: str) -> str:
        """Generate detailed suitability summary."""
        address = property_data["address"]
        price = property_data["price"]
        size = property_data["size_in_acres"]
        zoning = property_data["zoning_classification"]
        price_per_acre = price / size if size > 0 else 0
        
        summary_parts = []
        
        # Overall assessment
        if development_score >= 80:
            summary_parts.append(f"EXCELLENT development opportunity at {address}.")
        elif development_score >= 70:
            summary_parts.append(f"STRONG development potential at {address}.")
        elif development_score >= 60:
            summary_parts.append(f"GOOD development opportunity at {address}.")
        elif development_score >= 50:
            summary_parts.append(f"MODERATE development potential at {address}.")
        else:
            summary_parts.append(f"LIMITED development potential at {address}.")
        
        # Price analysis
        if scores["price_per_acre"] >= 85:
            summary_parts.append(f"Outstanding value at ${price_per_acre:,.0f} per acre.")
        elif scores["price_per_acre"] >= 70:
            summary_parts.append(f"Good value proposition at ${price_per_acre:,.0f} per acre.")
        elif scores["price_per_acre"] >= 50:
            summary_parts.append(f"Fairly priced at ${price_per_acre:,.0f} per acre.")
        else:
            summary_parts.append(f"Premium pricing at ${price_per_acre:,.0f} per acre may limit returns.")
        
        # Size assessment
        if scores["size"] >= 85:
            summary_parts.append(f"Large {size:.1f}-acre parcel offers substantial development flexibility.")
        elif scores["size"] >= 70:
            summary_parts.append(f"Good-sized {size:.1f}-acre property supports meaningful development.")
        elif scores["size"] >= 55:
            summary_parts.append(f"Moderate {size:.1f}-acre size allows for focused development.")
        else:
            summary_parts.append(f"Limited {size:.1f}-acre size constrains development options.")
        
        # Zoning benefits
        if scores["zoning"] >= 90:
            summary_parts.append(f"{zoning} zoning provides maximum development flexibility.")
        elif scores["zoning"] >= 75:
            summary_parts.append(f"{zoning} zoning offers good development options.")
        else:
            summary_parts.append(f"{zoning} zoning may limit development scope.")
        
        # Risk assessment
        summary_parts.append(f"Investment risk level: {risk_level}.")
        
        return " ".join(summary_parts)

    def _run(self, address: str, price: float, size_in_acres: float, 
             zoning_classification: str, coordinates: Optional[Coordinates] = None) -> str:
        """Execute property analysis and scoring."""
        try:
            # Input validation
            if price <= 0:
                return json.dumps({"error": "Price must be greater than 0"})
            if size_in_acres <= 0:
                return json.dumps({"error": "Size must be greater than 0"})
            
            # Calculate individual scores
            price_per_acre_score = self._calculate_price_per_acre_score(price, size_in_acres)
            size_score = self._calculate_size_score(size_in_acres)
            zoning_score = self._calculate_zoning_score(zoning_classification)
            location_score = self._calculate_location_score(address, coordinates)
            market_trend_score = self._calculate_market_trend_score(address, zoning_classification)
            
            # Calculate weighted composite development score
            weights = {
                "price_per_acre": 0.25,
                "size": 0.20,
                "zoning": 0.20,
                "location": 0.20,
                "market_trends": 0.15
            }
            
            development_score = (
                price_per_acre_score * weights["price_per_acre"] +
                size_score * weights["size"] +
                zoning_score * weights["zoning"] +
                location_score * weights["location"] +
                market_trend_score * weights["market_trends"]
            )
            
            # Calculate additional metrics
            price_per_acre = price / size_in_acres
            risk_level = self._determine_risk_level(development_score, price_per_acre)
            
            # Store scores for reference
            scores = {
                "price_per_acre": price_per_acre_score,
                "size": size_score,
                "zoning": zoning_score,
                "location": location_score,
                "market_trends": market_trend_score
            }
            
            # Generate suitability summary
            property_data = {
                "address": address,
                "price": price,
                "size_in_acres": size_in_acres,
                "zoning_classification": zoning_classification
            }
            
            suitability_summary = self._generate_suitability_summary(
                property_data, scores, development_score, risk_level
            )
            
            # Prepare analysis details
            analysis_details = {
                "component_scores": scores,
                "price_per_acre": round(price_per_acre, 2),
                "scoring_weights": weights,
                "key_factors": {
                    "strengths": [],
                    "concerns": [],
                    "recommendations": []
                }
            }
            
            # Identify strengths and concerns
            if scores["price_per_acre"] >= 70:
                analysis_details["key_factors"]["strengths"].append("Excellent price per acre value")
            if scores["size"] >= 70:
                analysis_details["key_factors"]["strengths"].append("Good development scale potential")
            if scores["zoning"] >= 80:
                analysis_details["key_factors"]["strengths"].append("Favorable zoning classification")
            if scores["location"] >= 70:
                analysis_details["key_factors"]["strengths"].append("Strong location desirability")
            
            if scores["price_per_acre"] < 50:
                analysis_details["key_factors"]["concerns"].append("High price per acre may impact ROI")
            if scores["size"] < 50:
                analysis_details["key_factors"]["concerns"].append("Limited size constrains development options")
            if development_score < 60:
                analysis_details["key_factors"]["concerns"].append("Below-average overall development potential")
            
            # Add recommendations
            if risk_level in ["High", "Medium-High"]:
                analysis_details["key_factors"]["recommendations"].append("Consider detailed market analysis before proceeding")
            if scores["zoning"] < 70:
                analysis_details["key_factors"]["recommendations"].append("Investigate zoning variance or rezoning opportunities")
            if development_score >= 70:
                analysis_details["key_factors"]["recommendations"].append("Strong candidate for development - consider fast-tracking due diligence")
            
            # Convert coordinates to dict for JSON serialization if present
            coordinates_dict = None
            if coordinates:
                coordinates_dict = {"lat": coordinates.lat, "lng": coordinates.lng}
            
            # Compile final result
            result = {
                "enhanced_property": {
                    "original_data": {
                        "address": address,
                        "price": price,
                        "size_in_acres": size_in_acres,
                        "zoning_classification": zoning_classification,
                        "coordinates": coordinates_dict
                    },
                    "suitability_summary": suitability_summary,
                    "development_score": round(development_score, 1),
                    "risk_level": risk_level,
                    "analysis_details": analysis_details
                },
                "analysis_timestamp": "Analysis completed successfully"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": f"Property analysis failed: {str(e)}",
                "input_received": {
                    "address": address,
                    "price": price,
                    "size_in_acres": size_in_acres,
                    "zoning_classification": zoning_classification
                }
            })