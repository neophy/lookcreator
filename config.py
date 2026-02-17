# Configuration file for Look Creator app

# E-commerce platforms
ECOMMERCE_PLATFORMS = {
    "Amazon.in": "https://www.amazon.in/s?k=",
    "Flipkart": "https://www.flipkart.com/search?q=",
    "Myntra": "https://www.myntra.com/",
    "Ajio": "https://www.ajio.com/search/?text=",
    "Nykaa Fashion": "https://www.nykaafashion.com/search/product?q=",
}

# Items that should also search on Nykaa
NYKAA_ITEM_KEYWORDS = ['bag', 'jewelry', 'accessory', 'sunglasses', 'watch', 'earring', 'necklace', 'bracelet']

# Claude Vision prompt for analysis
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

# Example images for testing
EXAMPLE_IMAGES = {
    "Street Style": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800",
    "Casual Outfit": "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800",
    "Formal Look": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800",
}

# Claude model to use
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Max tokens for Claude response
MAX_TOKENS = 2048
