# Look Creator - AI Fashion Search Agent

An AI-powered Streamlit app that analyzes fashion images and helps you find similar products on Indian e-commerce platforms.

## Features

- 🤖 **AI Image Analysis**: Uses Claude Vision to identify clothing items, colors, styles, and features
- 🛍️ **Multi-Platform Search**: Generates search links for Amazon.in, Flipkart, Myntra, Ajio, and Nykaa Fashion
- 📊 **Detailed Breakdown**: Provides comprehensive analysis of each fashion item
- 💾 **Export Results**: Download analysis as JSON for later reference

## Prerequisites

- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

## Local Setup

### 1. Clone or Download the Project

```bash
# If you have the files, navigate to the directory
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

### 4. Set Up Your API Key

**Option A: Using .env file (Recommended)**

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API key:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx
```

3. Load environment variables:
```bash
# On Mac/Linux, add to your terminal startup file:
export $(cat .env | xargs)

# Or use python-dotenv (already in requirements.txt)
```

**Option B: Set environment variable directly**

```bash
# On Windows
set ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx

# On Mac/Linux
export ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx
```

### 5. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How to Use

1. **Paste an image URL** or select an example image
2. Click **"Analyze Look"** to process the image
3. View the identified items with details
4. Click on shopping links to search for similar products
5. Download the analysis as JSON if needed

## Deployment Options

### Deploy to Streamlit Cloud (Easiest - FREE)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository
6. Add your `ANTHROPIC_API_KEY` in "Advanced settings" → "Secrets"
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-api03-xxxxxxxxxxxx"
   ```
7. Click "Deploy"!

Your app will be live at `https://your-app-name.streamlit.app`

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

3. Add your API key in Railway dashboard under "Variables"

### Deploy to Render.com

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Add environment variable: `ANTHROPIC_API_KEY`

## Project Structure

```
look-creator/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── README.md          # This file
```

## How It Works

1. **Image Input**: User provides an image URL
2. **AI Analysis**: Claude Vision API analyzes the image and identifies fashion items
3. **Structured Output**: Claude returns JSON with item details (type, color, style, features)
4. **Search Generation**: App creates optimized search links for Indian e-commerce sites
5. **Display Results**: User can click through to shop for similar items

## API Costs

- Claude Sonnet 4: ~$3 per 1M input tokens, ~$15 per 1M output tokens
- Typical analysis: ~$0.01-0.05 per image
- Image input tokens are calculated based on image size

## Customization Ideas

### Add More E-commerce Sites
Edit the `generate_search_links()` function to add more platforms:
```python
links["NewSite"] = f"https://www.newsite.com/search?q={search_query}"
```

### Change Claude Model
In `analyze_image_with_claude()`, change the model:
```python
model="claude-opus-4-20250514"  # For more detailed analysis
```

### Add Image Upload
Replace URL input with file upload:
```python
uploaded_file = st.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg'])
```

### Add Product Price Scraping
Integrate with SerpAPI or web scraping libraries to fetch actual prices.

## Troubleshooting

**"ANTHROPIC_API_KEY not found"**
- Make sure you've set the environment variable correctly
- For Streamlit Cloud, check that secrets are configured

**"Unable to display image"**
- Some URLs may be behind authentication
- Try a direct image URL (ending in .jpg, .png, etc.)

**"Failed to parse Claude's response"**
- The AI might return malformed JSON occasionally
- Check the raw response shown in the error message
- Try with a different image

**Rate Limits**
- Free tier has rate limits
- Add error handling or upgrade your Anthropic plan

## Next Steps

To enhance this app into a full agent:

1. **Add Web Scraping**: Use BeautifulSoup or Playwright to fetch actual products
2. **Implement LangGraph**: Create a multi-step agent workflow
3. **Add Price Comparison**: Scrape and compare prices across platforms
4. **Visual Similarity**: Use CLIP embeddings to find visually similar products
5. **User Accounts**: Add Firebase/Supabase for saving favorite looks
6. **Shopping Cart**: Integrate with e-commerce APIs for direct purchasing

## Contributing

Feel free to fork and enhance this project! Some ideas:
- Add more Indian e-commerce platforms
- Implement actual product scraping
- Add user authentication
- Create a mobile version

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues or questions:
- Check the [Anthropic API documentation](https://docs.anthropic.com)
- Review [Streamlit documentation](https://docs.streamlit.io)
- Open an issue on GitHub

---

Built with ❤️ using Claude AI and Streamlit
