import streamlit as st
import anthropic
import json
import os
from typing import List, Dict

# Page configuration
st.set_page_config(
    page_title="Look Creator - AI Fashion Search",
    page_icon="👗",
    layout="wide"
)

# Initialize Anthropic client
@st.cache_resource
def get_anthropic_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("⚠️ ANTHROPIC_API_KEY not found in environment variables!")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

def analyze_image_with_claude(image_url: str, client: anthropic.Anthropic) -> Dict:
    """Analyze fashion items in an image using Claude Vision"""
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "url",
                                "url": image_url
                            }
                        },
                        {
                            "type": "text",
                            "text": """Analyze this image and identify all fashion items (clothing, shoes, accessories, bags, jewelry, etc.).

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
                        }
                    ]
                }
            ]
        )
        
        # Extract the text content
        response_text = message.content[0].text
        
        # Try to parse JSON from the response
        # Claude might wrap JSON in markdown code blocks
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
        
        result = json.loads(json_str)
        return result
        
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse Claude's response as JSON: {e}")
        st.text("Raw response:")
        st.text(response_text)
        return None
    except Exception as e:
        st.error(f"Error analyzing image: {str(e)}")
        return None

def generate_search_links(item: Dict) -> Dict[str, str]:
    """Generate search links for Indian e-commerce platforms"""
    
    search_query = item.get('search_keywords', '').replace(' ', '+')
    
    links = {
        "Amazon.in": f"https://www.amazon.in/s?k={search_query}",
        "Flipkart": f"https://www.flipkart.com/search?q={search_query}",
        "Myntra": f"https://www.myntra.com/{search_query}",
        "Ajio": f"https://www.ajio.com/search/?text={search_query}",
    }
    
    # Add Nykaa for accessories and beauty items
    if any(keyword in item.get('type', '').lower() for keyword in ['bag', 'jewelry', 'accessory', 'sunglasses', 'watch']):
        links["Nykaa Fashion"] = f"https://www.nykaafashion.com/search/product?q={search_query}"
    
    return links

def main():
    # Header
    st.title("👗 Look Creator")
    st.markdown("### AI-Powered Fashion Search for Indian E-commerce")
    st.markdown("Upload or paste an image URL to find similar products you can buy in India!")
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        **Look Creator** uses Claude's vision AI to:
        - Analyze fashion items in any image
        - Identify colors, styles, and features
        - Generate search links for Indian e-commerce sites
        
        **Supported Platforms:**
        - Amazon.in
        - Flipkart
        - Myntra
        - Ajio
        - Nykaa Fashion
        """)
        
        st.markdown("---")
        st.markdown("**Tips:**")
        st.markdown("""
        - Use clear, high-quality images
        - Images with single outfits work best
        - Right-click on any image online and select 'Copy Image Address'
        """)
    
    # Initialize client
    client = get_anthropic_client()
    
    # Input methods
    st.subheader("Step 1: Provide an Image")
    
    input_method = st.radio(
        "Choose input method:",
        ["Image URL", "Example Images"],
        horizontal=True
    )
    
    image_url = None
    
    if input_method == "Image URL":
        image_url = st.text_input(
            "Paste image URL:",
            placeholder="https://example.com/fashion-image.jpg",
            help="Right-click on any image and select 'Copy Image Address'"
        )
    else:
        # Example images for testing
        examples = {
            "Street Style": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800",
            "Casual Outfit": "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800",
            "Formal Look": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800",
        }
        
        selected_example = st.selectbox("Choose an example:", list(examples.keys()))
        image_url = examples[selected_example]
    
    # Display image if URL is provided
    if image_url:
        try:
            st.image(image_url, caption="Your selected image", use_container_width=True)
        except:
            st.warning("⚠️ Unable to display image. The URL might be invalid, but we'll try to analyze it anyway.")
    
    # Analyze button
    if st.button("🔍 Analyze Look", type="primary", use_container_width=True):
        if not image_url:
            st.warning("Please provide an image URL first!")
            return
        
        with st.spinner("🤖 Claude is analyzing the image..."):
            result = analyze_image_with_claude(image_url, client)
        
        if result:
            st.success("✅ Analysis complete!")
            
            # Display overall style
            st.subheader("Overall Style Assessment")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Style:**")
                st.info(result.get('overall_style', 'N/A'))
            
            with col2:
                st.markdown("**Occasion:**")
                st.info(result.get('occasion', 'N/A'))
            
            st.markdown("---")
            
            # Display identified items
            st.subheader("Identified Items")
            
            items = result.get('items', [])
            
            if not items:
                st.warning("No items were identified in the image.")
                return
            
            for idx, item in enumerate(items, 1):
                with st.expander(f"**{idx}. {item.get('type', 'Unknown Item').title()}**", expanded=True):
                    # Item details
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
                        
                        st.markdown("**Shop on:**")
                        search_links = generate_search_links(item)
                        
                        # Create buttons for each platform
                        for platform, link in search_links.items():
                            st.markdown(f"[🛍️ Search on {platform}]({link})")
            
            # Download results as JSON
            st.markdown("---")
            st.subheader("Export Results")
            
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="📥 Download Analysis (JSON)",
                data=json_str,
                file_name="look_analysis.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()
