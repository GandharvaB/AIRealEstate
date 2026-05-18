"""
99acres.com India Real Estate Data Tool
Scrapes property listings from 99acres.com for Indian locations.
Provides structured property data including plots, flats, and commercial properties.
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, List, Optional
import requests
import re
import json
import time
from urllib.parse import quote


class NinetyNineAcresSearchInput(BaseModel):
    """Input schema for 99acres India Real Estate Tool."""
    target_location: str = Field(
        ...,
        description="Indian city or locality name (e.g., 'Mumbai', 'Bangalore', 'Pune', 'Whitefield Bangalore')"
    )
    property_type: str = Field(
        default="plot",
        description="Type of property: 'plot', 'flat', 'house', 'commercial', 'agricultural'"
    )
    min_budget: Optional[str] = Field(
        default=None,
        description="Minimum budget (e.g., '50-lakhs', '1-crore', '10-lakhs')"
    )
    max_budget: Optional[str] = Field(
        default=None,
        description="Maximum budget (e.g., '1-crore', '5-crores', '50-lakhs')"
    )
    max_results: int = Field(
        default=10,
        description="Maximum number of properties to return"
    )


# ── Indian City → 99acres URL slug mappings ──────────────────────
CITY_SLUGS = {
    "mumbai": "mumbai",
    "delhi": "delhi",
    "bangalore": "bangalore",
    "bengaluru": "bangalore",
    "hyderabad": "hyderabad",
    "pune": "pune",
    "chennai": "chennai",
    "kolkata": "kolkata",
    "ahmedabad": "ahmedabad",
    "jaipur": "jaipur",
    "lucknow": "lucknow",
    "noida": "noida",
    "gurgaon": "gurgaon",
    "gurugram": "gurgaon",
    "thane": "mumbai-thane",
    "navi mumbai": "navi-mumbai",
    "goa": "goa",
    "north goa": "north-goa",
    "south goa": "south-goa",
    "chandigarh": "chandigarh",
    "indore": "indore",
    "bhopal": "bhopal",
    "nagpur": "nagpur",
    "nashik": "nashik",
    "surat": "surat",
    "vadodara": "vadodara",
    "kochi": "kochi",
    "coimbatore": "coimbatore",
    "visakhapatnam": "visakhapatnam",
    "mysore": "mysore",
    "mysuru": "mysore",
    "dehradun": "dehradun",
    "rishikesh": "rishikesh",
    "mangalore": "mangalore",
    "trivandrum": "trivandrum",
    "thiruvananthapuram": "trivandrum",
}

# ── Property type → URL path mappings ────────────────────────────
PROPERTY_TYPE_URLS = {
    "plot": "residential-land-in-{city}-ffid",
    "flat": "flats-in-{city}-ffid",
    "house": "independent-house-in-{city}-ffid",
    "commercial": "commercial-property-in-{city}-ffid",
    "agricultural": "agricultural-land-in-{city}-ffid",
}

# ── Price trend URL pattern ──────────────────────────────────────
PRICE_TRENDS_URL = "https://www.99acres.com/property-rates-and-price-trends-in-{city}-prffid"
LISTING_URL = "https://www.99acres.com/{path}"


class NinetyNineAcresApiTool(BaseTool):
    """Tool for scraping real estate data from 99acres.com for Indian locations.
    
    Fetches property listings, price trends, and locality insights from 99acres.com.
    Supports plots, flats, houses, commercial, and agricultural properties across
    major Indian cities. Returns structured data with addresses, prices, descriptions,
    and listing URLs.
    """

    name: str = "ninetynine_acres_india_tool"
    description: str = (
        "Searches 99acres.com for Indian real estate property listings. "
        "Supports plots, flats, houses, and commercial properties across 30+ major Indian cities. "
        "Returns structured property data including address, price, description, property type, "
        "and listing URLs from India's largest property portal."
    )
    args_schema: Type[BaseModel] = NinetyNineAcresSearchInput

    def _normalize_city(self, location: str) -> str:
        """Normalize an Indian city/locality name to a 99acres URL slug."""
        location_lower = location.strip().lower()

        # Direct match
        if location_lower in CITY_SLUGS:
            return CITY_SLUGS[location_lower]

        # Try matching the last word as city (e.g., "Whitefield Bangalore" → "bangalore")
        parts = location_lower.split()
        for part in reversed(parts):
            if part in CITY_SLUGS:
                return CITY_SLUGS[part]

        # Fall back to slugifying the input
        slug = re.sub(r'[^a-z0-9]+', '-', location_lower).strip('-')
        return slug

    def _get_locality_from_location(self, location: str) -> Optional[str]:
        """Extract locality name if a specific area within a city is specified."""
        location_lower = location.strip().lower()
        parts = location_lower.split(',')

        if len(parts) >= 2:
            return parts[0].strip()

        words = location_lower.split()
        if len(words) >= 2:
            city_found = False
            for word in words:
                if word in CITY_SLUGS:
                    city_found = True
                    break
            if city_found:
                locality_parts = [w for w in words if w not in CITY_SLUGS]
                if locality_parts:
                    return ' '.join(locality_parts)

        return None

    def _fetch_page(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Fetch a page from 99acres.com with retry logic."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
        }

        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 403:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return None
            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        return None

    def _parse_listings(self, html: str, max_results: int, property_type: str) -> List[Dict[str, Any]]:
        """Parse property listings from 99acres HTML."""
        properties = []

        # Extract listing blocks — 99acres uses structured listing URLs
        # Pattern: residential-land-plot-for-sale-in-{location}-{size}-spid-{id}
        listing_pattern = re.compile(
            r'href="(https://www\.99acres\.com/[^"]*-spid-[A-Z0-9]+)"',
            re.IGNORECASE
        )

        # Also match project listings
        project_pattern = re.compile(
            r'href="(https://www\.99acres\.com/[^"]*-npxid-[a-z0-9]+)"',
            re.IGNORECASE
        )

        seen_urls = set()
        urls = listing_pattern.findall(html) + project_pattern.findall(html)

        for url in urls:
            if url in seen_urls or len(properties) >= max_results:
                continue
            seen_urls.add(url)

            prop = self._extract_property_from_url(url, property_type)
            if prop:
                properties.append(prop)

        # Fallback: extract structured text blocks
        if len(properties) < max_results:
            block_pattern = re.compile(
                r'##\s+(Residential land.*?|Plot.*?|Flat.*?|House.*?|Commercial.*?)(?=\n##|\n\[|$)',
                re.IGNORECASE | re.DOTALL
            )
            blocks = block_pattern.findall(html)
            for block in blocks:
                if len(properties) >= max_results:
                    break
                prop = self._parse_text_block(block, property_type)
                if prop and prop.get('address') not in [p.get('address') for p in properties]:
                    properties.append(prop)

        return properties

    def _extract_property_from_url(self, url: str, property_type: str) -> Optional[Dict[str, Any]]:
        """Extract property information from a 99acres listing URL."""
        try:
            # Parse location from URL
            # e.g., residential-land-plot-for-sale-in-uran-navi-mumbai-2057-sqyd-r1-spid-G86505820
            url_path = url.split('99acres.com/')[-1]

            # Extract location
            location_match = re.search(r'(?:sale|rent)-in-(.*?)(?:-\d+-sq|-spid|-npxid)', url_path)
            if location_match:
                location = location_match.group(1).replace('-', ' ').title()
            else:
                location = url_path.split('-spid')[0].split('-npxid')[0].replace('-', ' ').title()

            # Extract size
            size_match = re.search(r'(\d+)-sq(?:yd|ft|mt)', url_path)
            size_str = f"{size_match.group(1)} sq" if size_match else None

            unit_match = re.search(r'\d+-(sqyd|sqft|sqmt)', url_path)
            if unit_match and size_str:
                unit_map = {'sqyd': 'sq.yd', 'sqft': 'sq.ft', 'sqmt': 'sq.mt'}
                size_str = f"{size_match.group(1)} {unit_map.get(unit_match.group(1), 'sq.yd')}"

            # Extract ID
            id_match = re.search(r'spid-([A-Z0-9]+)', url_path)
            if not id_match:
                id_match = re.search(r'npxid-([a-z0-9]+)', url_path)
            prop_id = id_match.group(1) if id_match else url_path[-8:]

            return {
                "plot_id": f"99A-{prop_id}",
                "address": location,
                "price": None,  # Price needs page-level parsing
                "size": size_str,
                "property_type": property_type,
                "listing_url": url,
                "source": "99acres.com",
                "country": "India",
            }
        except Exception:
            return None

    def _parse_text_block(self, block: str, property_type: str) -> Optional[Dict[str, Any]]:
        """Parse a text description block into property data."""
        try:
            # Extract title/address
            title_match = re.match(r'(.*?)(?:\n|$)', block.strip())
            title = title_match.group(1).strip() if title_match else block[:100]

            # Extract price (₹ or Rs patterns)
            price = None
            price_match = re.search(
                r'(?:₹|Rs\.?|INR)\s*([\d,.]+)\s*(lacs?|lakhs?|crores?|cr)?',
                block, re.IGNORECASE
            )
            if price_match:
                amount = float(price_match.group(1).replace(',', ''))
                multiplier = price_match.group(2) or ''
                if 'crore' in multiplier.lower() or 'cr' in multiplier.lower():
                    price = amount * 10000000
                elif 'lac' in multiplier.lower() or 'lakh' in multiplier.lower():
                    price = amount * 100000
                else:
                    price = amount

            # Extract size
            size = None
            size_match = re.search(r'([\d,.]+)\s*(?:sq\.?\s*(?:ft|yd|mt|meter)|sqft|sqyd|sqmt|guntha|acre)', block, re.IGNORECASE)
            if size_match:
                size = size_match.group(0).strip()

            return {
                "plot_id": f"99A-{hash(title) % 100000:05d}",
                "address": title.split(' in ')[-1] if ' in ' in title else title,
                "description": block[:300].strip(),
                "price": price,
                "size": size,
                "property_type": property_type,
                "source": "99acres.com",
                "country": "India",
            }
        except Exception:
            return None

    def _fetch_price_trends(self, city_slug: str) -> Dict[str, Any]:
        """Fetch property price trends for a city."""
        url = PRICE_TRENDS_URL.format(city=city_slug)
        html = self._fetch_page(url)

        if not html:
            return {"available": False}

        trends = {"available": True, "city": city_slug, "localities": []}

        # Extract per-sqft prices
        price_pattern = re.compile(
            r'₹\s*([\d,]+)\s*per\s*sq\s*ft',
            re.IGNORECASE
        )
        prices = price_pattern.findall(html)
        if prices:
            numeric_prices = [int(p.replace(',', '')) for p in prices[:20]]
            trends["avg_price_per_sqft"] = sum(numeric_prices) // len(numeric_prices)
            trends["min_price_per_sqft"] = min(numeric_prices)
            trends["max_price_per_sqft"] = max(numeric_prices)

        # Extract popular localities
        locality_pattern = re.compile(
            r'property-rates-and-price-trends-in-([\w-]+)-(?:mumbai|delhi|bangalore|pune|hyderabad|chennai|kolkata|ahmedabad|jaipur|lucknow|noida|gurgaon|thane|goa)',
            re.IGNORECASE
        )
        localities = locality_pattern.findall(html)
        trends["popular_localities"] = list(set([l.replace('-', ' ').title() for l in localities[:15]]))

        return trends

    def _run(
        self,
        target_location: str,
        property_type: str = "plot",
        min_budget: Optional[str] = None,
        max_budget: Optional[str] = None,
        max_results: int = 10,
    ) -> str:
        """Search 99acres.com for properties in Indian locations."""

        # Normalize city
        city_slug = self._normalize_city(target_location)
        locality = self._get_locality_from_location(target_location)

        # Build listing URL
        prop_type_key = property_type.lower().strip()
        if prop_type_key not in PROPERTY_TYPE_URLS:
            prop_type_key = "plot"

        url_path = PROPERTY_TYPE_URLS[prop_type_key].format(city=city_slug)

        # Add budget filters to URL if specified
        if min_budget and max_budget:
            budget_suffix = f"-{min_budget}-to-{max_budget}"
            url_path = url_path.replace('-ffid', f'{budget_suffix}-ffid')
        elif min_budget:
            url_path = url_path.replace('-ffid', f'-above-{min_budget}-ffid')
        elif max_budget:
            url_path = url_path.replace('-ffid', f'-below-{max_budget}-ffid')

        listing_url = LISTING_URL.format(path=url_path)

        # Fetch listings page
        html = self._fetch_page(listing_url)

        properties = []
        if html:
            properties = self._parse_listings(html, max_results, prop_type_key)

        # Fetch price trends
        price_trends = self._fetch_price_trends(city_slug)

        # Build result
        result = {
            "source": "99acres.com",
            "country": "India",
            "search_location": target_location,
            "city_slug": city_slug,
            "locality": locality,
            "property_type": prop_type_key,
            "listing_page_url": listing_url,
            "total_properties_found": len(properties),
            "properties": properties,
            "price_trends": price_trends,
            "budget_filter": {
                "min": min_budget,
                "max": max_budget,
            },
            "notes": (
                "Data sourced from 99acres.com property listings. "
                "Prices in Indian Rupees (INR). "
                "For complete details, visit individual listing URLs."
            ),
        }

        return json.dumps(result, indent=2, ensure_ascii=False)
