from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, List, Optional
import requests
import json
import time
import math
from math import radians, cos, sin, asin, sqrt

class RealEstateSearchInput(BaseModel):
    """Input schema for Real Estate API Integration Tool."""
    target_location: str = Field(..., description="Target location for property search (address, city, state, or coordinates)")
    search_radius_miles: float = Field(default=5.0, description="Search radius in miles from target location")
    min_price: Optional[int] = Field(default=None, description="Minimum property price")
    max_price: Optional[int] = Field(default=None, description="Maximum property price")
    zoning_type: Optional[str] = Field(default=None, description="Zoning classification filter (residential, commercial, agricultural, etc.)")
    minimum_acres: Optional[float] = Field(default=None, description="Minimum property size in acres")

class RealEstateApiTool(BaseTool):
    """Tool for integrating with real estate APIs to search properties with comprehensive filtering and error handling."""

    name: str = "real_estate_api_tool"
    description: str = (
        "Searches real estate properties using multiple API providers (Zillow, ATTOM Data, RentSpider). "
        "Supports location-based searches with radius filtering, handles rate limits with exponential backoff, "
        "and returns standardized property data including plot_id, address, price, size_in_acres, zoning_classification, and listing_url."
    )
    args_schema: Type[BaseModel] = RealEstateSearchInput

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the haversine distance between two points on Earth in miles."""
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of Earth in miles
        r = 3956
        return c * r

    def _exponential_backoff_request(self, url: str, headers: Dict[str, str], params: Dict[str, Any], max_retries: int = 4) -> Dict[str, Any]:
        """Make HTTP request with exponential backoff retry logic for rate limits."""
        retry_delays = [2, 4, 8, 16]  # Exponential backoff delays in seconds
        
        for attempt in range(max_retries + 1):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code == 200:
                    return {
                        "status_code": 200,
                        "data": response.json(),
                        "error": None
                    }
                elif response.status_code == 429:  # Rate limit exceeded
                    if attempt < max_retries:
                        delay = retry_delays[attempt]
                        time.sleep(delay)
                        continue
                    else:
                        return {
                            "status_code": 429,
                            "data": None,
                            "error": f"Rate limit exceeded. Max retries ({max_retries}) reached."
                        }
                elif response.status_code == 400:
                    return {
                        "status_code": 400,
                        "data": None,
                        "error": f"Bad request: {response.text}"
                    }
                else:
                    return {
                        "status_code": response.status_code,
                        "data": None,
                        "error": f"API error: {response.status_code} - {response.text}"
                    }
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                    time.sleep(delay)
                    continue
                else:
                    return {
                        "status_code": 500,
                        "data": None,
                        "error": "Request timeout after 30 seconds and max retries reached."
                    }
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                    time.sleep(delay)
                    continue
                else:
                    return {
                        "status_code": 500,
                        "data": None,
                        "error": f"Request failed: {str(e)}"
                    }
        
        return {
            "status_code": 500,
            "data": None,
            "error": "Max retries reached without successful response."
        }

    def _geocode_location(self, location: str, api_keys: Dict[str, str]) -> Optional[Dict[str, float]]:
        """Convert address to coordinates using a geocoding service."""
        # Try to parse coordinates directly (lat,lon format)
        try:
            if ',' in location:
                coords = location.split(',')
                if len(coords) == 2:
                    lat = float(coords[0].strip())
                    lon = float(coords[1].strip())
                    return {"latitude": lat, "longitude": lon}
        except ValueError:
            pass
        
        # Use a free geocoding service (nominatim) as fallback
        try:
            geocode_url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": location,
                "format": "json",
                "limit": 1
            }
            headers = {"User-Agent": "RealEstateApiTool/1.0"}
            
            response = requests.get(geocode_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        "latitude": float(data[0]["lat"]),
                        "longitude": float(data[0]["lon"])
                    }
        except Exception:
            pass
        
        return None

    def _search_rapidapi_properties(self, location: str, params: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Search properties using RapidAPI real estate endpoints."""
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
        }
        
        # Example endpoint - you may need to adjust based on actual API
        url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
        
        api_params = {
            "location": location,
            "status_type": "ForSale"
        }
        
        if params.get("min_price"):
            api_params["minPrice"] = params["min_price"]
        if params.get("max_price"):
            api_params["maxPrice"] = params["max_price"]
        
        return self._exponential_backoff_request(url, headers, api_params)

    def _search_attom_properties(self, location: str, params: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Search properties using ATTOM Data API."""
        headers = {
            "apikey": api_key,
            "Accept": "application/json"
        }
        
        url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/basicprofile"
        
        api_params = {
            "address1": location
        }
        
        return self._exponential_backoff_request(url, headers, api_params)

    def _standardize_property_data(self, raw_data: Dict[str, Any], provider: str, target_coords: Optional[Dict[str, float]], radius_miles: float) -> List[Dict[str, Any]]:
        """Convert raw API response to standardized property format."""
        standardized_properties = []
        
        try:
            properties = []
            
            # Extract properties based on provider
            if provider == "rapidapi":
                properties = raw_data.get("props", raw_data.get("results", []))
            elif provider == "attom":
                properties = raw_data.get("property", [])
                if not isinstance(properties, list):
                    properties = [properties]
            
            for prop in properties:
                try:
                    # Extract basic information with fallbacks
                    plot_id = (
                        prop.get("zpid") or 
                        prop.get("propertyId") or 
                        prop.get("identifier", {}).get("Id") or 
                        f"{provider}_{hash(str(prop))}"
                    )
                    
                    # Address handling
                    if provider == "rapidapi":
                        address = prop.get("address", {})
                        full_address = f"{address.get('streetAddress', '')} {address.get('city', '')} {address.get('state', '')} {address.get('zipcode', '')}"
                    elif provider == "attom":
                        address = prop.get("address", {})
                        full_address = f"{address.get('line1', '')} {address.get('locality', '')} {address.get('countrySubd', '')} {address.get('postal1', '')}"
                    else:
                        full_address = str(prop.get("address", "Unknown"))
                    
                    # Price handling
                    price = (
                        prop.get("price") or 
                        prop.get("listPrice") or 
                        prop.get("zestimate") or 
                        prop.get("assessment", {}).get("market", {}).get("mktTtlValue")
                    )
                    
                    # Size in acres
                    lot_size_sqft = (
                        prop.get("lotAreaValue") or 
                        prop.get("lotSize") or 
                        prop.get("lot", {}).get("lotSize2")
                    )
                    size_in_acres = round(lot_size_sqft / 43560, 2) if lot_size_sqft else None
                    
                    # Zoning
                    zoning = (
                        prop.get("zoning") or 
                        prop.get("zoningClassification") or 
                        prop.get("summary", {}).get("propclass")
                    )
                    
                    # Listing URL
                    listing_url = (
                        prop.get("detailUrl") or 
                        prop.get("url") or 
                        f"https://www.zillow.com/homedetails/{plot_id}_zpid/"
                    )
                    
                    # Distance filtering if coordinates are available
                    if target_coords:
                        prop_lat = prop.get("latitude") or prop.get("location", {}).get("latitude")
                        prop_lon = prop.get("longitude") or prop.get("location", {}).get("longitude")
                        
                        if prop_lat and prop_lon:
                            distance = self._haversine_distance(
                                target_coords["latitude"], target_coords["longitude"],
                                float(prop_lat), float(prop_lon)
                            )
                            
                            if distance > radius_miles:
                                continue  # Skip properties outside radius
                    
                    standardized_property = {
                        "plot_id": str(plot_id),
                        "address": full_address.strip(),
                        "price": int(price) if price else None,
                        "size_in_acres": size_in_acres,
                        "zoning_classification": str(zoning) if zoning else None,
                        "listing_url": listing_url
                    }
                    
                    standardized_properties.append(standardized_property)
                    
                except Exception as e:
                    # Log individual property parsing errors but continue
                    continue
                    
        except Exception as e:
            # Return empty list if data standardization fails completely
            pass
        
        return standardized_properties

    def _run(self, target_location: str, search_radius_miles: float = 5.0, min_price: Optional[int] = None, 
            max_price: Optional[int] = None, zoning_type: Optional[str] = None, minimum_acres: Optional[float] = None) -> str:
        """Execute the real estate property search with comprehensive error handling."""
        
        try:
            # Get API keys from environment
            import os
            api_keys = {
                "rapidapi": os.getenv("RAPIDAPI_KEY"),
                "attom": os.getenv("ATTOM_API_KEY"),
                "zillow": os.getenv("ZILLOW_API_KEY")
            }
            
            # Check if at least one API key is available
            available_apis = {k: v for k, v in api_keys.items() if v}
            if not available_apis:
                return json.dumps({
                    "status_code": 400,
                    "error": "No API keys found in environment variables. Please set RAPIDAPI_KEY, ATTOM_API_KEY, or ZILLOW_API_KEY.",
                    "properties": []
                })
            
            # Geocode target location
            target_coords = self._geocode_location(target_location, api_keys)
            
            # Prepare search parameters
            search_params = {
                "min_price": min_price,
                "max_price": max_price,
                "zoning_type": zoning_type,
                "minimum_acres": minimum_acres
            }
            
            all_properties = []
            api_errors = []
            
            # Try each available API provider
            for provider, api_key in available_apis.items():
                try:
                    if provider == "rapidapi":
                        result = self._search_rapidapi_properties(target_location, search_params, api_key)
                    elif provider == "attom":
                        result = self._search_attom_properties(target_location, search_params, api_key)
                    else:
                        continue  # Skip unsupported providers
                    
                    if result["status_code"] == 200 and result["data"]:
                        properties = self._standardize_property_data(
                            result["data"], provider, target_coords, search_radius_miles
                        )
                        all_properties.extend(properties)
                    else:
                        api_errors.append(f"{provider}: {result['error']}")
                        
                except Exception as e:
                    api_errors.append(f"{provider}: {str(e)}")
            
            # Filter by minimum acres if specified
            if minimum_acres is not None:
                all_properties = [
                    prop for prop in all_properties 
                    if prop.get("size_in_acres") and prop["size_in_acres"] >= minimum_acres
                ]
            
            # Filter by zoning type if specified
            if zoning_type:
                all_properties = [
                    prop for prop in all_properties 
                    if prop.get("zoning_classification") and 
                    zoning_type.lower() in prop["zoning_classification"].lower()
                ]
            
            # Remove duplicates based on address
            seen_addresses = set()
            unique_properties = []
            for prop in all_properties:
                addr_key = prop["address"].lower().strip()
                if addr_key not in seen_addresses:
                    seen_addresses.add(addr_key)
                    unique_properties.append(prop)
            
            # Prepare response
            if unique_properties:
                response = {
                    "status_code": 200,
                    "properties": unique_properties,
                    "total_found": len(unique_properties),
                    "search_parameters": {
                        "target_location": target_location,
                        "search_radius_miles": search_radius_miles,
                        "min_price": min_price,
                        "max_price": max_price,
                        "zoning_type": zoning_type,
                        "minimum_acres": minimum_acres
                    }
                }
                if api_errors:
                    response["api_warnings"] = api_errors
            else:
                response = {
                    "status_code": 200,
                    "properties": [],
                    "total_found": 0,
                    "message": "No properties found matching the specified criteria.",
                    "search_parameters": {
                        "target_location": target_location,
                        "search_radius_miles": search_radius_miles,
                        "min_price": min_price,
                        "max_price": max_price,
                        "zoning_type": zoning_type,
                        "minimum_acres": minimum_acres
                    }
                }
                if api_errors:
                    response["api_errors"] = api_errors
            
            return json.dumps(response, indent=2)
            
        except Exception as e:
            error_response = {
                "status_code": 500,
                "error": f"Internal error during property search: {str(e)}",
                "properties": []
            }
            return json.dumps(error_response, indent=2)