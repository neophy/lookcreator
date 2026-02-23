"""
Product search module for e-commerce platforms
Uses SerpAPI with Google Lens for visual search and Shopping API for text search
"""

import os
from typing import List, Dict, Optional, Callable
from serpapi import GoogleSearch


# Indian e-commerce domains we want to prioritize
INDIAN_ECOMMERCE = {
    'amazon.in': 'Amazon India',
    'flipkart.com': 'Flipkart',
    'myntra.com': 'Myntra',
    'ajio.com': 'Ajio',
    'nykaa.com': 'Nykaa',
    'nykaafashion.com': 'Nykaa Fashion',
    'tatacliq.com': 'Tata CLiQ',
    'shoppersstop.com': 'Shoppers Stop',
    'lifestyle.com': 'Lifestyle',
    'maxfashion.in': 'Max Fashion',
    'westside.com': 'Westside',
    'zara.com/in': 'Zara India',
}


def search_via_google_lens(
    image_url: str,
    max_results: int = 20,
    debug_callback: Optional[Callable] = None
) -> List[Dict]:
    """
    Use Google Lens to find visually similar products
    This gives MUCH better visual matching than text search
    
    Args:
        image_url: URL of the image to search
        max_results: Maximum results to return
        debug_callback: Function to call for logging
    
    Returns:
        List of visually similar products
    """
    
    def log(msg):
        if debug_callback:
            debug_callback(msg)
        print(msg)
    
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        log("⚠️ SERPAPI_API_KEY not found")
        return []
    
    log(f"🔍 Google Lens search for image: {image_url[:50]}...")
    
    params = {
        "api_key": api_key,
        "engine": "google_lens",
        "url": image_url,
        "hl": "en",
        "gl": "in",  # Bias towards India
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        log(f"✅ Google Lens response received")
        log(f"   Keys: {list(results.keys())}")
        
        if 'error' in results:
            log(f"❌ Google Lens error: {results['error']}")
            return []
        
        # Google Lens returns visual_matches - these are the best matches
        visual_matches = results.get("visual_matches", [])
        log(f"   Found {len(visual_matches)} visual matches")
        
        products = []
        indian_products = []
        global_products = []
        
        for idx, match in enumerate(visual_matches[:max_results * 2]):  # Get extra to filter
            link = match.get('link', '')
            title = match.get('title', '')
            
            if not link or not title:
                continue
            
            product = {
                "title": title,
                "link": link,
                "thumbnail": match.get('thumbnail', ''),
                "source": match.get('source', ''),
                "price": match.get('price', ''),
                "rating": None,
                "reviews": None,
                "match_percentage": 90,  # Google Lens already did visual matching
                "search_method": "google_lens"
            }
            
            # Check if it's from Indian e-commerce
            is_indian = False
            for domain, name in INDIAN_ECOMMERCE.items():
                if domain in link.lower():
                    product['source'] = name
                    is_indian = True
                    indian_products.append(product)
                    break
            
            if not is_indian:
                global_products.append(product)
        
        # Prioritize Indian products, then add global ones if needed
        products = indian_products[:max_results]
        
        if len(products) < max_results:
            remaining = max_results - len(products)
            products.extend(global_products[:remaining])
        
        log(f"✅ Extracted {len(indian_products)} Indian products, {len(global_products)} global")
        log(f"✅ Returning {len(products)} total products")
        
        return products
    
    except Exception as e:
        log(f"❌ Google Lens error: {type(e).__name__}: {str(e)}")
        return []


def search_products_serpapi(
    query: str,
    platform: str = "google_shopping",
    max_results: int = 15,
    debug_callback: Optional[Callable] = None
) -> List[Dict]:
    """
    Search for products using text-based shopping search
    Fallback when Google Lens doesn't work or for text queries
    
    Args:
        query: Search query (e.g., "blue floral dress")
        platform: Platform to search
        max_results: Maximum results to return
        debug_callback: Function for logging
    
    Returns:
        List of product dictionaries
    """
    
    def log(msg):
        if debug_callback:
            debug_callback(msg)
        print(msg)
    
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        log("⚠️ SERPAPI_API_KEY not found")
        return []
    
    log(f"🔍 Shopping search: {query[:50]}...")
    log(f"   Platform: {platform}")
    
    params = {
        "api_key": api_key,
        "q": query,
        "num": max_results,
        "hl": "en",
        "gl": "in",
    }
    
    if platform == "amazon":
        params["q"] = f"{query} site:amazon.in"
        params["tbm"] = "shop"
    elif platform == "flipkart":
        params["q"] = f"{query} site:flipkart.com"
        params["tbm"] = "shop"
    elif platform == "myntra":
        params["q"] = f"{query} site:myntra.com"
        params["tbm"] = "shop"
    else:
        params["tbm"] = "shop"
        params["q"] = f"{query} india"
    
    log(f"   Final query: {params['q']}")
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        log(f"✅ Shopping search response received")
        
        if 'error' in results:
            log(f"❌ SerpAPI error: {results['error']}")
            return []
        
        shopping_results = results.get("shopping_results", [])
        log(f"   Found {len(shopping_results)} shopping results")
        
        products = []
        for idx, item in enumerate(shopping_results[:max_results]):
            product = {
                "title": item.get("title", ""),
                "price": item.get("extracted_price", item.get("price", "")),
                "link": item.get("product_link", item.get("link", "")),
                "thumbnail": item.get("thumbnail", ""),
                "source": item.get("source", ""),
                "rating": item.get("rating", None),
                "reviews": item.get("reviews", None),
                "match_percentage": 0,  # Will be calculated by CLIP
                "search_method": "text_search"
            }
            
            if product["title"] and product["link"]:
                products.append(product)
        
        log(f"✅ Extracted {len(products)} valid products")
        return products
    
    except Exception as e:
        log(f"❌ Shopping search error: {type(e).__name__}: {str(e)}")
        return []


def hybrid_search(
    image_url: str,
    search_keywords: str,
    max_results: int = 10,
    debug_callback: Optional[Callable] = None
) -> List[Dict]:
    """
    BEST STRATEGY: Combine Google Lens + Text Search for optimal results
    
    1. Try Google Lens first (best visual matching)
    2. If < 5 Indian results, supplement with text search
    3. Deduplicate and return top results
    
    Args:
        image_url: Image to search
        search_keywords: Fallback text query
        max_results: Total results to return
        debug_callback: Logging function
    
    Returns:
        Combined list of best products
    """
    
    def log(msg):
        if debug_callback:
            debug_callback(msg)
        print(msg)
    
    log("🎯 Starting hybrid search (Lens + Text)")
    
    # Step 1: Google Lens visual search
    lens_products = search_via_google_lens(image_url, max_results=15, debug_callback=debug_callback)
    
    # Count Indian products from Lens
    indian_lens = [p for p in lens_products if any(domain in p['link'].lower() for domain in INDIAN_ECOMMERCE.keys())]
    
    log(f"📊 Lens results: {len(indian_lens)} Indian, {len(lens_products) - len(indian_lens)} global")
    
    # Step 2: If we have enough good Indian results, we're done
    if len(indian_lens) >= max_results:
        log(f"✅ Sufficient Indian results from Lens alone")
        return indian_lens[:max_results]
    
    # Step 3: Supplement with text search
    log(f"🔍 Supplementing with text search: {search_keywords}")
    text_products = search_products_serpapi(
        search_keywords,
        platform="google_shopping",
        max_results=max_results,
        debug_callback=debug_callback
    )
    
    # Step 4: Combine and deduplicate
    all_products = indian_lens + lens_products  # Prioritize Indian from Lens
    
    # Add text results that aren't duplicates
    seen_links = {p['link'] for p in all_products}
    for product in text_products:
        if product['link'] not in seen_links:
            all_products.append(product)
            seen_links.add(product['link'])
    
    log(f"✅ Combined total: {len(all_products)} unique products")
    
    return all_products[:max_results * 2]  # Return more for CLIP to filter


def search_multiple_platforms(
    query: str,
    platforms: List[str] = None,
    max_per_platform: int = 10
) -> Dict[str, List[Dict]]:
    """
    Search across multiple platforms (legacy function for compatibility)
    """
    if platforms is None:
        platforms = ["google_shopping", "amazon"]
    
    results = {}
    for platform in platforms:
        products = search_products_serpapi(query, platform=platform, max_results=max_per_platform)
        if products:
            results[platform] = products
    
    return results
