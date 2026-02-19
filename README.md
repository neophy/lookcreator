# Look Creator - AI Fashion Search Agent

An AI-powered Streamlit app that analyzes fashion images and helps you find similar products on Indian e-commerce platforms with **smart visual matching**.

## ✨ Features

- 🤖 **AI Image Analysis**: Uses Claude Vision to identify clothing items, colors, styles, and features
- 🎯 **Smart Product Matching**: Uses CLIP embeddings to find visually similar products (NEW!)
- 🛍️ **Multi-Platform Search**: Searches Amazon.in, Flipkart, Myntra, Ajio, and Nykaa Fashion
- 📊 **Detailed Breakdown**: Provides comprehensive analysis of each fashion item
- 💾 **Export Results**: Download analysis as JSON for later reference
- 📁 **Local Upload**: Upload photos directly from your computer

## 🆕 What's New: Smart Product Matching

Instead of just search links, the app now:
1. **Searches** e-commerce sites for products
2. **Downloads** product images
3. **Compares** them with your original image using AI
4. **Ranks** products by visual similarity (match percentage)
5. **Shows** the top 5 most similar products with direct links

## Prerequisites

- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- SerpAPI key (Optional, for smart matching - [Get free tier](https://serpapi.com))

## Local Setup

### 1. Clone or Download the Project

```bash
cd look-creator
```

### 2. Create a Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: Installing PyTorch and sentence-transformers may take 5-10 minutes.

### 4. Set Up Your API Keys

**Option A: Using .env file (Recommended)**

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx
SERPAPI_API_KEY=your_serpapi_key_here  # Optional but recommended
```

**Option B: Set environment variables directly**

```bash
# On Windows
set ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx
set SERPAPI_API_KEY=your_serpapi_key_here

# On Mac/Linux
export ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx
export SERPAPI_API_KEY=your_serpapi_key_here
```

### 5. Run the App

```bash
# Load environment variables and run
export $(cat .env | xargs) && streamlit run app.py

# Or use the quick start script
./start.sh  # Mac/Linux
start.bat   # Windows
```

The app will open in your browser at `http://localhost:8501`

## How to Use

1. **Upload an image** or paste a direct image URL
2. Click **"Analyze Look"** to process the image
3. View identified items with details
4. Click **"Find Best Matching Products"** to get AI-matched products
5. Click on product links to buy similar items
6. Download the analysis as JSON if needed

## API Keys & Pricing

### Anthropic (Required)
- **Cost**: ~$3 per 1M input tokens, ~$15 per 1M output tokens
- **Per image**: ~$0.01-0.05
- Get key at: https://console.anthropic.com

### SerpAPI (Optional, enables smart matching)
- **Free tier**: 100 searches/month
- **Paid**: $50/month for 5,000 searches
- **Per search**: ~$0.01
- Get key at: https://serpapi.com

**Total cost per image with matching**: ~$0.05-0.20

## Deployment Options

### Deploy to Streamlit Cloud (Easiest - FREE)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository
6. Add your API keys in "Advanced settings" → "Secrets"
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-api03-xxxxxxxxxxxx"
   SERPAPI_API_KEY = "your_serpapi_key_here"
   ```
7. Click "Deploy"!

Your app will be live at `https://your-app-name.streamlit.app`

**Note**: First deployment may take 10-15 minutes due to PyTorch installation.

### Deploy to Railway.app

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Initialize and deploy:
```bash
railway login
railway init
railway up
```

3. Add API keys in Railway dashboard under "Variables"

### Deploy to Render.com

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Add environment variables for both API keys

## Project Structure

```
look-creator/
├── app.py                  # Main Streamlit application
├── product_search.py       # SerpAPI product search module
├── image_matcher.py        # CLIP-based image similarity matching
├── requirements.txt        # Python dependencies
├── config.py              # Configuration settings
├── .env.example           # Environment variable template
├── start.sh              # Quick start script (Mac/Linux)
├── start.bat             # Quick start script (Windows)
└── README.md             # This file
```

## How It Works

### Basic Flow
1. **Image Input**: User provides an image URL or uploads a file
2. **AI Analysis**: Claude Vision API analyzes and identifies fashion items
3. **Structured Output**: Claude returns JSON with item details

### Smart Matching Flow (NEW!)
4. **Product Search**: SerpAPI searches e-commerce sites for each item
5. **Image Download**: Downloads product images from search results
6. **Similarity Matching**: CLIP model compares product images with original
7. **Ranking**: Products ranked by visual similarity (0-100%)
8. **Display**: Top 5 matches shown with direct purchase links

## Troubleshooting

**"ANTHROPIC_API_KEY not found"**
- Make sure you've set the environment variable correctly
- For Streamlit Cloud, check that secrets are configured

**"SERPAPI_API_KEY not found" (Warning only)**
- App still works, but smart matching is disabled
- Manual search links will still be provided

**"Failed to load CLIP model"**
- First run downloads ~1GB model - be patient
- Ensure you have stable internet connection
- Model is cached after first download

**"No products found"**
- Try different search keywords manually
- Some items may not have good matches in current results
- Adjust `min_similarity` threshold in code if needed

**Rate Limits**
- Free SerpAPI tier has 100 searches/month
- Claude API has rate limits based on tier
- Consider upgrading if you hit limits

## Performance Optimization

The smart matching adds ~10-20 seconds per item:
- **Product search**: ~2-3 seconds
- **Image download**: ~3-5 seconds  
- **CLIP comparison**: ~5-10 seconds

**To optimize**:
1. Reduce `max_results` in search (default: 15)
2. Reduce `top_k` matches (default: 5)
3. Increase `min_similarity` threshold (default: 0.2)
4. Use smaller CLIP model (edit `image_matcher.py`)

## Customization Ideas

### Add More E-commerce Sites
Edit `product_search.py`:
```python
elif platform == "myntra":
    params["q"] = f"{query} site:myntra.com"
```

### Adjust Similarity Threshold
Edit `app.py` in `display_matched_products`:
```python
matches = find_best_matches(original_image, products, top_k=5, min_similarity=0.3)
```

### Use Different CLIP Model
Edit `image_matcher.py`:
```python
model = SentenceTransformer('clip-ViT-B-16')  # Smaller, faster
```

## Future Enhancements

- [ ] Add price comparison across platforms
- [ ] Save favorite looks to account
- [ ] Batch processing for multiple images
- [ ] Mobile app version
- [ ] Direct checkout integration
- [ ] Style recommendations based on body type
- [ ] Virtual try-on using AR

## Contributing

Feel free to fork and enhance this project! Some ideas:
- Add support for international e-commerce
- Implement actual web scraping (bypass SerpAPI cost)
- Add user authentication and saved searches
- Create browser extension version

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues or questions:
- Check the [Anthropic API documentation](https://docs.anthropic.com)
- Review [Streamlit documentation](https://docs.streamlit.io)
- Check [SerpAPI documentation](https://serpapi.com/docs)
- Open an issue on GitHub

---

Built with ❤️ using Claude AI, Streamlit, and CLIP
