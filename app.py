import streamlit as st
import anthropic
import json
import os
import base64
from typing import Dict
from product_search import search_products_serpapi, search_multiple_platforms
from image_matcher import find_best_matches
import time

# Page configuration
st.set_page_config(
    page_title="Look Creator - AI Fashion Search",
    page_icon="👗",
    layout="wide"
)

# Debug mode toggle
DEBUG_MODE = st.sidebar.checkbox("🐛 Debug Mode", value=True, help="Show detailed logs")

def debug_log(message: str, data=None):
    """Print debug messages if debug mode is on"""
    if DEBUG_MODE:
        timestamp = time.strftime("%H:%M:%S")
        st.sidebar.text(f"[{timestamp}] {message}")
        if data:
            with st.sidebar.expander("View data"):
                st.json(data)

# Initialize Anthropic client
@st.cache_resource
def get_anthropic_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except:
            pass
    if not api_key:
        st.error("⚠️ ANTHROPIC_API_KEY not found!")
        st.stop()
    debug_log("✅ Anthropic client initialized")
    return anthropic.Anthropic(api_key=api_key)

def check_serpapi_key():
    """Check if SerpAPI key is available"""
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("SERPAPI_API_KEY")
        except:
            pass
    
    has_key = bool(api_key)
    debug_log(f"SerpAPI key {'found' if has_key else 'NOT found'}")
    return has_key

def is_social_media_url(url: str):
    """Detect social media page URLs and return the platform name"""
    blocked = {
        "pinterest.com": "Pinterest",
        "instagram.com": "Instagram",
        "facebook.com": "Facebook",
        "twitter.com": "Twitter/X",
        "x.com": "Twitter/X",
        "tiktok.com": "TikTok",
    }
    for domain, name in blocked.items():
        if domain in url:
            return name
    return None

def parse_claude_json(response_text: str) -> Dict:
    """Safely extract JSON from Claude's response"""
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        json_str = response_text[json_start:json_end].strip()
    elif "```" in response_text:
        json_start = response_text.find("```") + 3
        json_end = response_text.find("```", json_start)
        json_str = response_text[json_start:json_end].strip()
    else:
        json_str = response_text
    return json.loads(json_str)

ANALYSIS_PROMPT = """Analyze this image and identify all fashion items (clothing, shoes, accessories, bags, jewelry, etc.).

For each item you identify, provide:
1. Item type (e.g., dress, jeans, sneakers, handbag, sunglasses)
2. Color(s) - be specific
3. Style/pattern (e.g., floral print, solid, striped, distressed)
4. Material if visible (e.g., denim, leather, cotton)
5. Key features (e.g., V-neck, high-waisted, platform sole)
6. Search keywords - the best keywords to use when searching for similar items online

Return your response as a JSON object with this structure:
{
  "items": [
    {
      "type": "item type",
      "color": "color description",
      "style": "style description",
      "material": "material if visible",
      "features": ["feature1", "feature2"],
      "search_keywords": "optimized search query"
    }
  ],
  "overall_style": "brief description of the overall look/aesthetic",
  "occasion": "suggested occasion for this outfit"
}

Be thorough and identify as many items as possible."""

@st.cache_data(ttl=3600, show_spinner="🤖 Analyzing image with Claude...")
def analyze_via_url_cached(image_url: str, _client: anthropic.Anthropic) -> Dict:
    """Analyze image using a URL - CACHED to avoid repeated API calls"""
    debug_log(f"🔍 Starting Claude analysis for URL: {image_url[:50]}...")
    
    try:
        # Test if URL is accessible
        debug_log("🌐 Testing image URL accessibility...")
        import requests
        test_response = requests.head(image_url, timeout=5, allow_redirects=True)
        debug_log(f"✅ URL accessible (status: {test_response.status_code})")
        
        debug_log("📤 Sending request to Claude API...")
        message = _client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "url", "url": image_url}
                    },
                    {"type": "text", "text": ANALYSIS_PROMPT}
                ]
            }]
        )
        debug_log("✅ Received response from Claude API")
        
        debug_log("📝 Parsing JSON from response...")
        response_text = message.content[0].text
        debug_log(f"Response length: {len(response_text)} chars")
        
        result = parse_claude_json(response_text)
        debug_log(f"✅ Successfully parsed. Found {len(result.get('items', []))} items")
        
        return result
        
    except requests.exceptions.RequestException as e:
        debug_log(f"❌ URL not accessible: {str(e)}")
        st.error(f"Cannot access image URL: {str(e)}")
        st.info("Try uploading the image file directly instead of using URL")
        raise
    except json.JSONDecodeError as e:
        debug_log(f"❌ JSON parsing failed: {str(e)}")
        debug_log(f"Raw response: {response_text[:500]}")
        st.error("Failed to parse Claude's response")
        with st.expander("View raw response"):
            st.text(response_text)
        raise
    except Exception as e:
        debug_log(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")
        st.error(f"Analysis failed: {str(e)}")
        raise

@st.cache_data(ttl=3600, show_spinner="🤖 Analyzing uploaded image...")
def analyze_via_upload_cached(image_bytes: bytes, media_type: str, _client: anthropic.Anthropic) -> Dict:
    """Analyze image using base64 - CACHED"""
    debug_log(f"🔍 Starting analysis of uploaded image ({len(image_bytes)} bytes, type: {media_type})")
    
    try:
        debug_log("🔄 Encoding image to base64...")
        image_data = base64.standard_b64encode(image_bytes).decode("utf-8")
        debug_log(f"✅ Encoded to {len(image_data)} chars")
        
        debug_log("📤 Sending request to Claude API...")
        message = _client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {"type": "text", "text": ANALYSIS_PROMPT}
                ]
            }]
        )
        debug_log("✅ Received response from Claude API")
        
        debug_log("📝 Parsing JSON from response...")
        response_text = message.content[0].text
        debug_log(f"Response length: {len(response_text)} chars")
        
        result = parse_claude_json(response_text)
        debug_log(f"✅ Successfully parsed. Found {len(result.get('items', []))} items")
        
        return result
        
    except json.JSONDecodeError as e:
        debug_log(f"❌ JSON parsing failed: {str(e)}")
        debug_log(f"Raw response: {response_text[:500]}")
        st.error("Failed to parse Claude's response")
        with st.expander("View raw response"):
            st.text(response_text)
        raise
    except Exception as e:
        debug_log(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")
        st.error(f"Analysis failed: {str(e)}")
        raise

def generate_search_links(item: Dict) -> Dict:
    """Generate search links for Indian e-commerce platforms"""
    search_query = item.get('search_keywords', '').replace(' ', '+')
    links = {
        "Amazon.in": f"https://www.amazon.in/s?k={search_query}",
        "Flipkart": f"https://www.flipkart.com/search?q={search_query}",
        "Myntra": f"https://www.myntra.com/{search_query}",
        "Ajio": f"https://www.ajio.com/search/?text={search_query}",
    }
    if any(kw in item.get('type', '').lower() for kw in ['bag', 'jewelry', 'accessory', 'sunglasses', 'watch']):
        links["Nykaa Fashion"] = f"https://www.nykaafashion.com/search/product?q={search_query}"
    return links

def search_parallel_platforms(search_query: str, platforms: list = None) -> Dict:
    """Search multiple platforms in parallel using threads"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    if platforms is None:
        platforms = ["google_shopping", "amazon"]
    
    debug_log(f"🔍 Searching {len(platforms)} platforms for: {search_query}")
    
    all_products = []
    
    with ThreadPoolExecutor(max_workers=len(platforms)) as executor:
        future_to_platform = {
            executor.submit(
                search_products_serpapi, 
                search_query, 
                platform, 
                10,
                debug_log  # ← Pass debug_log here
            ): platform
            for platform in platforms
        }
        
        for future in as_completed(future_to_platform):
            platform = future_to_platform[future]
            try:
                products = future.result()
                debug_log(f"✅ {platform}: Found {len(products)} products")
                all_products.extend(products)
            except Exception as e:
                debug_log(f"❌ {platform} search failed: {str(e)}")
    
    debug_log(f"✅ Total products found: {len(all_products)}")
    return all_products

def display_matched_products(item: Dict, original_image, item_idx: int):
    """Search and display matched products for an item"""
    
    search_query = item.get('search_keywords', '')
    debug_log(f"Starting product search for: {search_query}")
    
    st.info(f"🔍 Searching query: **{search_query}**")
    
    # Parallel search across platforms
    platforms = ["google_shopping", "amazon"]
    
    with st.spinner(f"🔍 Searching platforms..."):
        debug_log("🔍 Calling SerpAPI directly (bypassing parallel)")
        products = search_products_serpapi(search_query, "google_shopping", 15, debug_log)
        debug_log(f"✅ Direct call returned {len(products)} products")
    
    if not products:
        st.error("❌ No products found. Check debug logs in sidebar.")
        debug_log("❌ No products returned from any platform")
        st.info("Check SerpAPI dashboard at https://serpapi.com/dashboard")
        return
    
    st.success(f"✅ Found {len(products)} products from {len(platforms)} platforms")
    
    # Show sample products for debugging
    # if DEBUG_MODE and products:
    #     with st.expander("🔍 Sample product data"):
    #         st.json(products[0])
    
    # Find best matches using image similarity
    st.info("🎯 Analyzing visual similarity...")
    
    with st.spinner("🎯 Comparing products with your image..."):
        try:
            matches = find_best_matches(original_image, products, top_k=5, min_similarity=0.15)
            debug_log(f"✅ Found {len(matches)} matches above threshold")
        except Exception as e:
            st.error(f"❌ Image matching failed: {str(e)}")
            debug_log(f"❌ Matching error: {str(e)}")
            
            # Show products anyway without similarity scores
            st.warning("Showing search results without similarity scoring...")
            matches = products[:5]
            for m in matches:
                m['match_percentage'] = 0
    
    if not matches:
        st.warning("⚠️ No similar products found. Try adjusting search or use manual links.")
        return
    
    st.success(f"✅ Found {len(matches)} visually similar products!")
    
    # Display matches
    for idx, match in enumerate(matches, 1):
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if match.get('thumbnail'):
                    try:
                        st.image(match['thumbnail'], use_column_width=True)
                    except:
                        st.text("Image unavailable")
            
            with col2:
                # Match indicator with color coding
                match_pct = match.get('match_percentage', 0)
                if match_pct >= 70:
                    badge_color = "🟢"
                elif match_pct >= 50:
                    badge_color = "🟡"
                elif match_pct > 0:
                    badge_color = "🟠"
                else:
                    badge_color = "⚪"  # No score
                
                if match_pct > 0:
                    st.markdown(f"### {badge_color} Match #{idx} - {match_pct}% Similar")
                else:
                    st.markdown(f"### Match #{idx}")
                
                st.markdown(f"**{match.get('title', 'Unknown Product')}**")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Price", match.get('price', 'N/A'))
                with col_b:
                    st.metric("Source", match.get('source', 'N/A'))
                with col_c:
                    if match.get('rating'):
                        st.metric("Rating", f"{match['rating']}⭐")
                
                if match.get('link'):
                    st.link_button("🛒 View Product", match['link'], use_container_width=True)
                else:
                    st.warning("No product link available")
            
            st.divider()

def display_results(result: Dict, original_image):
    """Render analysis results"""
    st.success("✅ Analysis complete!")
    
    debug_log("Rendering results")

    # Check if product matching is available
    has_serpapi = check_serpapi_key()

    st.subheader("Overall Style Assessment")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Style:**")
        st.info(result.get('overall_style', 'N/A'))
    with col2:
        st.markdown("**Occasion:**")
        st.info(result.get('occasion', 'N/A'))

    st.markdown("---")
    st.subheader("Identified Items")

    items = result.get('items', [])
    if not items:
        st.warning("No items were identified in the image.")
        return

    for idx, item in enumerate(items, 1):
        with st.expander(f"**{idx}. {item.get('type', 'Unknown Item').title()}**", expanded=True):
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown("**Details:**")
                st.markdown(f"**Color:** {item.get('color', 'N/A')}")
                st.markdown(f"**Style:** {item.get('style', 'N/A')}")
                st.markdown(f"**Material:** {item.get('material', 'N/A')}")
                if item.get('features'):
                    st.markdown("**Features:**")
                    for feature in item['features']:
                        st.markdown(f"- {feature}")
            with col2:
                st.markdown("**Search Query:**")
                st.code(item.get('search_keywords', 'N/A'), language=None)
                st.markdown("**Manual Search Links:**")
                for platform, link in generate_search_links(item).items():
                    st.markdown(f"[🔗 {platform}]({link})")
            
            st.markdown("---")
            
            # Product matching button
            if has_serpapi:
                # Initialize session state for this item
                button_key = f"match_item_{idx}"
                if button_key not in st.session_state:
                    st.session_state[button_key] = False
                
                debug_log(f"🔍 Item {idx}: button_key={button_key}, state={st.session_state[button_key]}")
                
                # Button to trigger search
                if st.button(f"🎯 Find Best Matching Products", key=f"match_btn_{idx}", use_container_width=True):
                    debug_log(f"🔘 Match button clicked for item {idx}")
                    st.session_state[button_key] = True
                    st.rerun()  # ← ADD THIS! Force immediate rerun
                
                # Display products if button was clicked
                if st.session_state[button_key]:
                    debug_log(f"📦 Displaying products for item {idx}")
                    with st.container():
                        display_matched_products(item, original_image, idx)
                        
                        # Add reset button
                        if st.button(f"🔄 Search Again", key=f"reset_btn_{idx}"):
                            st.session_state[button_key] = False
                            st.rerun()
            else:
                st.warning("⚠️ **SerpAPI not configured** - Add SERPAPI_API_KEY to enable smart matching")
                st.info("Get free API key at https://serpapi.com (100 searches/month)")

    st.markdown("---")
    st.subheader("Export Results")
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download Analysis (JSON)",
            data=json.dumps(result, indent=2),
            file_name="look_analysis.json",
            mime="application/json"
        )
    with col2:
        if st.button("🗑️ Clear Cache & Reanalyze"):
            st.cache_data.clear()
            st.success("Cache cleared! Refresh page to reanalyze.")

def main():
    st.title("👗 Look Creator")
    st.markdown("### AI-Powered Fashion Search for Indian E-commerce")
    st.markdown("Upload a photo or paste an image URL to find similar products you can buy in India!")

    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        **Look Creator** uses Claude's vision AI to:
        - Analyze fashion items in any image
        - Identify colors, styles, and features
        - Generate search links for Indian e-commerce sites
        - Find visually similar products (with SerpAPI)
        """)
        
        # API Status
        st.markdown("---")
        st.markdown("**API Status:**")
        claude_status = "✅" if os.environ.get("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY", None) else "❌"
        serpapi_status = "✅" if check_serpapi_key() else "❌"
        st.markdown(f"{claude_status} Claude API")
        st.markdown(f"{serpapi_status} SerpAPI (Smart Matching)")
        
        if serpapi_status == "❌":
            st.info("Get SerpAPI key for smart product matching at [serpapi.com](https://serpapi.com)")
        
        st.markdown("---")

    client = get_anthropic_client()

    # Input method
    st.subheader("Step 1: Provide an Image")
    
    # Remove horizontal to avoid session state issues
    input_method = st.radio(
        "Choose input method:",
        ["📁 Upload from computer", "🔗 Image URL", "🖼️ Example Images"]
    )

    image_url = None
    uploaded_bytes = None
    uploaded_media_type = None

    # Upload from computer
    if input_method == "📁 Upload from computer":
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=["jpg", "jpeg", "png", "webp", "gif"],
            help="Upload any photo from your computer or phone"
        )
        if uploaded_file:
            uploaded_bytes = uploaded_file.read()
            uploaded_media_type = uploaded_file.type
            st.image(uploaded_bytes, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)
            debug_log(f"File uploaded: {uploaded_file.name} ({len(uploaded_bytes)} bytes)")

    # Image URL
    elif input_method == "🔗 Image URL":
        image_url = st.text_input(
            "Paste image URL:",
            placeholder="https://example.com/fashion-image.jpg",
            help="Must be a direct image link ending in .jpg, .png, etc."
        )

        if image_url:
            platform = is_social_media_url(image_url)
            if platform:
                st.error(f"⚠️ This looks like a **{platform} page URL**, not a direct image link.")
                if platform == "Pinterest":
                    st.info("""
**How to get the direct image URL from Pinterest:**
1. Open the Pinterest link in your browser
2. Click on the image to expand it
3. Right-click the image → **"Copy Image Address"**
4. The URL should look like: `https://i.pinimg.com/originals/xx/xx/xx/photo.jpg`
                    """)
                else:
                    st.info(f"Right-click on the image on {platform} → **Copy Image Address** → paste that URL here.")
                image_url = None
            else:
                try:
                    st.image(image_url, caption="Preview", use_column_width=True)
                    debug_log(f"Image URL loaded: {image_url[:50]}...")
                except Exception as e:
                    st.warning(f"Can't preview this URL: {e}")

    # Example Images
    else:
        examples = {
            "Street Style": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800",
            "Casual Outfit": "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800",
            "Formal Look": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800",
        }
        selected = st.selectbox("Choose an example:", list(examples.keys()))
        image_url = examples[selected]
        st.image(image_url, caption=selected, use_column_width=True)
        debug_log(f"Example selected: {selected}")

    # Analyze button
    # has_input = bool(image_url) or bool(uploaded_bytes)
    # if st.button("🔍 Analyze Look", type="primary", use_container_width=True, disabled=not has_input):
    #     # Store original image for matching
    #     original_image = uploaded_bytes if uploaded_bytes else image_url
        
    #     debug_log("=" * 50)
    #     debug_log("STARTING ANALYSIS")
    #     debug_log("=" * 50)
        
    #     try:
    #         if uploaded_bytes:
    #             result = analyze_via_upload_cached(uploaded_bytes, uploaded_media_type, client)
    #         else:
    #             result = analyze_via_url_cached(image_url, client)
            
    #         if result:
    #             # Store results in session state
    #             st.session_state['analysis_result'] = result
    #             st.session_state['original_image'] = original_image
    #         else:
    #             st.error("Analysis returned no results")

    #     except json.JSONDecodeError as e:
    #         st.error(f"Failed to parse response: {e}")
    #         debug_log(f"JSON error: {str(e)}")
    #     except Exception as e:
    #         st.error(f"Error analyzing image: {str(e)}")
    #         debug_log(f"Error: {str(e)}")
            
    #         with st.expander("🔧 Error Details"):
    #             st.code(str(e))

    # # Display results if they exist in session state
    # if 'analysis_result' in st.session_state and 'original_image' in st.session_state:
    #     display_results(st.session_state['analysis_result'], st.session_state['original_image'])
    # Analyze button
    has_input = bool(image_url) or bool(uploaded_bytes)
    if st.button("🔍 Analyze Look", type="primary", use_container_width=True, disabled=not has_input):
        # Store original image for matching
        original_image = uploaded_bytes if uploaded_bytes else image_url
        
        debug_log("=" * 50)
        debug_log("USING HARDCODED ANALYSIS (TESTING)")
        debug_log("=" * 50)
        
        # HARDCODED RESULT - Comment out Claude API calls
        result = {
            "items": [
                {
                    "type": "sweater",
                    "color": "multicolor striped",
                    "style": "cropped, v-neck",
                    "material": "knit",
                    "features": ["v-neck", "cropped length", "striped pattern"],
                    "search_keywords": "striped cropped sweater v-neck multicolor knit top"
                }
            ],
            "overall_style": "Casual colorful style",
            "occasion": "Everyday casual wear"
        }
        
        debug_log(f"✅ Using hardcoded result with {len(result.get('items', []))} items")
        
        # Store results in session state
        st.session_state['analysis_result'] = result
        st.session_state['original_image'] = original_image

    # Display results if they exist in session state
    if 'analysis_result' in st.session_state and 'original_image' in st.session_state:
        display_results(st.session_state['analysis_result'], st.session_state['original_image'])
if __name__ == "__main__":
    main()
