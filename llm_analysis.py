import requests
import json

def analyze_stock_opportunities():
    """Analyze news data for intraday trading opportunities using Gemini 1.5 Flash with web search"""
    
    # API configuration
    api_key = "AIzaSyAFTmL3mxhhSoZoMT8uaBp6c0Rvsf15IK4"
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    # Read the news file
    try:
        with open('FULL_INDIAN_STOCK_NEWS_20250805_112525.txt', 'r', encoding='utf-8') as file:
            news_content = file.read()
        print("✅ News file loaded successfully!")
        print(f"📰 Total characters: {len(news_content)}")
    except FileNotFoundError:
        print("❌ Error: FULL_INDIAN_STOCK_NEWS_20250805_112525.txt not found!")
        return
    except Exception as e:
        print(f"❌ Error reading news file: {e}")
        return
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    
    # Create focused prompt for trading analysis
    trading_prompt = f"""
    You are an expert stock market analyst specializing in intraday trading opportunities. Analyze the following Indian stock market news data and identify SPECIFIC stocks/companies that have HIGH PROBABILITY of significant price movement (up or down) in the next trading day.

    **CRITICAL REQUIREMENTS:**
    1. Focus ONLY on Indian companies and stocks
    2. Identify stocks with SURE-SHOT volatility potential (not speculative)
    3. Provide specific company names and stock symbols where possible
    4. Categorize as BULLISH (likely to go UP) or BEARISH (likely to go DOWN)
    5. Explain the specific news catalyst for each recommendation
    6. Rate impact as HIGH, MEDIUM, or LOW for each stock
    7. Suggest entry/exit strategies for intraday trading

    **ANALYSIS FRAMEWORK:**
    - Look for earnings results, major contracts, policy changes, regulatory news
    - Focus on companies with concrete financial impact
    - Identify sector-wide impacts (semiconductors, oil, banking, etc.)
    - Find merger/acquisition news, partnership announcements
    - Spot regulatory approvals, government policy changes
    - Search for any breaking news that could trigger immediate market reaction

    **OUTPUT FORMAT:**
    🚀 BULLISH OPPORTUNITIES (Likely to go UP):
    1. [Company Name] ([Stock Symbol if known])
       - Impact: HIGH/MEDIUM/LOW
       - Catalyst: [Specific news reason]
       - Strategy: [Entry/exit suggestion]

    📉 BEARISH OPPORTUNITIES (Likely to go DOWN):
    1. [Company Name] ([Stock Symbol if known])
       - Impact: HIGH/MEDIUM/LOW  
       - Catalyst: [Specific news reason]
       - Strategy: [Entry/exit suggestion]

    🎯 SECTOR PLAYS:
    - [Sector-wide opportunities based on news]

    ⚠️ KEY RISKS TO WATCH:
    - [Major risks that could affect overall market]

    Use web search to get additional real-time information about these companies and verify current market sentiment.

    **NEWS DATA TO ANALYZE:**
    {news_content}
    """
    
    # Request payload with web search enabled
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": trading_prompt
                    }
                ]
            }
        ],
        "tools": [
            {
                "googleSearchRetrieval": {
                    "dynamicRetrievalConfig": {
                        "mode": "MODE_DYNAMIC",
                        "dynamicThreshold": 0.7
                    }
                }
            }
        ]
    }
    
    try:
        print("\n🔍 Analyzing news for intraday trading opportunities...")
        print("📡 Using Gemini 1.5 Flash with web search for comprehensive analysis...")
        print("⏳ This may take 30-60 seconds for thorough analysis...\n")
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis complete!")
            print("\n" + "="*80)
            print("📈 INTRADAY TRADING OPPORTUNITIES - BASED ON NEWS ANALYSIS")
            print("="*80)
            
            # Extract and display the response
            if 'candidates' in result and len(result['candidates']) > 0:
                analysis = result['candidates'][0]['content']['parts'][0]['text']
                print(analysis)
                
                # Save analysis to file
                with open('trading_analysis_output.txt', 'w', encoding='utf-8') as output_file:
                    output_file.write("INTRADAY TRADING ANALYSIS\n")
                    output_file.write("="*50 + "\n")
                    output_file.write(f"Generated on: {json.dumps(result.get('generationConfig', {}))}\n\n")
                    output_file.write(analysis)
                print(f"\n💾 Analysis saved to: trading_analysis_output.txt")
                
            else:
                print("❌ No analysis generated. Response may be filtered.")
                print("Raw response:", json.dumps(result, indent=2))
                
        elif response.status_code == 429:
            print("⏳ Rate limit exceeded. Please wait 2-3 minutes and try again.")
            print("💡 Gemini 1.5 Flash has generous limits - should reset soon!")
            
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")

def quick_stock_check(company_name):
    """Quick check for specific company news with web search"""
    
    api_key = "AIzaSyAFTmL3mxhhSoZoMT8uaBp6c0Rvsf15IK4"
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    
    prompt = f"""
    Search the web for the latest news and developments about {company_name} in the Indian stock market. 
    
    Provide:
    1. Current stock price and today's movement
    2. Latest news affecting the stock
    3. Trading recommendation (BUY/SELL/HOLD)
    4. Intraday strategy if applicable
    5. Key levels to watch
    
    Focus on actionable trading insights for today/tomorrow.
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"googleSearchRetrieval": {"dynamicRetrievalConfig": {"mode": "MODE_DYNAMIC", "dynamicThreshold": 0.7}}}]
    }
    
    try:
        print(f"🔍 Checking latest updates for: {company_name}")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                analysis = result['candidates'][0]['content']['parts'][0]['text']
                print(f"\n📊 ANALYSIS FOR {company_name.upper()}:")
                print("="*50)
                print(analysis)
            else:
                print("❌ No analysis available")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🎯 INDIAN STOCK MARKET - INTRADAY TRADING ANALYZER")
    print("="*60)
    print("📰 Analyzing comprehensive news data for trading opportunities")
    print("🔍 Using AI + Web Search for real-time market intelligence")
    print("⚡ Focus: HIGH-IMPACT stocks with SURE volatility potential")
    print("="*60)
    
    # Run main analysis
    analyze_stock_opportunities()
    
    print("\n" + "="*60)
    print("💡 ADDITIONAL OPTIONS:")
    print("• For specific company check, use: quick_stock_check('Company Name')")
    print("• Example: quick_stock_check('Reliance Industries')")
    print("• Example: quick_stock_check('TCS')")
    print("="*60)
    print("\n⚠️  DISCLAIMER: This is for educational purposes only.")
    print("    Always do your own research before trading!")