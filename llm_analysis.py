import requests
import json
from openai import OpenAI

def split_news_data(news_content, num_parts=2):
    """Split news content into specified number of parts"""
    lines = news_content.strip().split('\n')
    
    # Skip header lines (first 4 lines are headers)
    header_lines = lines[:4]
    content_lines = lines[4:]
    
    # Calculate split points
    lines_per_part = len(content_lines) // num_parts
    parts = []
    
    for i in range(num_parts):
        start_idx = i * lines_per_part
        if i == num_parts - 1:  # Last part gets remaining lines
            end_idx = len(content_lines)
        else:
            end_idx = (i + 1) * lines_per_part
        
        part_content = '\n'.join(header_lines + content_lines[start_idx:end_idx])
        parts.append(part_content)
        print(f"📄 Part {i+1}: {len(content_lines[start_idx:end_idx])} news articles")
    
    return parts

def analyze_news_part(part_data, part_number):
    """Analyze a single part of news data"""
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )
    
    # Create focused prompt for this part
    part_prompt = f"""
    You are an expert stock market analyst. Analyze the following Indian stock market news data (Part {part_number}) and identify SPECIFIC stocks/companies with HIGH PROBABILITY of significant price movement in the next trading day.

    **CRITICAL REQUIREMENTS:**
    1. Focus ONLY on Indian companies and stocks
    2. Identify stocks with SURE-SHOT volatility potential
    3. Provide specific company names and stock symbols where possible
    4. Categorize as BULLISH (likely UP) or BEARISH (likely DOWN)
    5. Rate impact as HIGH, MEDIUM, or LOW
    6. Provide brief reason for each

    **OUTPUT FORMAT (be concise):**
    PART {part_number} ANALYSIS:
    
    🚀 BULLISH STOCKS:
    • [Company] ([Symbol]) - Impact: [HIGH/MED/LOW] - Reason: [brief catalyst]
    
    📉 BEARISH STOCKS:
    • [Company] ([Symbol]) - Impact: [HIGH/MED/LOW] - Reason: [brief catalyst]
    
    🎯 SECTOR TRENDS:
    • [Sector]: [trend and reason]
    
    ⚠️ KEY RISKS:
    • [Major risk factors]

    **NEWS DATA PART {part_number}:**
    {part_data}
    """
    
    try:
        print(f"🔍 Analyzing Part {part_number}...")
        
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://your-site-url.com",  # Optional
                "X-Title": "Stock News Analyzer",  # Optional
            },
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": part_prompt
                }
            ]
        )
        
        analysis = completion.choices[0].message.content
        print(f"✅ Part {part_number} analysis complete!")
        return analysis
            
    except Exception as e:
        print(f"❌ Error analyzing Part {part_number}: {e}")
        return f"Part {part_number}: Error - {str(e)}"

def merge_analyses(analysis1, analysis2):
    """Merge two separate analyses into final recommendations"""
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )
    
    merge_prompt = f"""
    You are a senior trading analyst. I have analyzed Indian stock market news in two parts. Now merge these analyses to create FINAL INTRADAY TRADING RECOMMENDATIONS.

    **TASK:**
    1. Combine findings from both parts
    2. Remove duplicates and rank by impact
    3. Create prioritized trading list
    4. Add timing and strategy suggestions
    5. Use web search for latest prices and sentiment

    **FINAL OUTPUT FORMAT:**
    
    🔥 TOP INTRADAY OPPORTUNITIES (FINAL RECOMMENDATIONS):
    
    📈 HIGH-IMPACT BULLISH (BUY):
    1. [Company] ([Symbol]) 
       • Catalyst: [consolidated reason]
       • Strategy: [entry/exit/timing]
       • Target: [price levels if possible]
    
    📉 HIGH-IMPACT BEARISH (SELL/SHORT):
    1. [Company] ([Symbol])
       • Catalyst: [consolidated reason] 
       • Strategy: [entry/exit/timing]
       • Target: [price levels if possible]
    
    ⚡ MEDIUM-IMPACT PLAYS:
    • [Quick list of secondary opportunities]
    
    🎯 SECTOR STRATEGIES:
    • [Key sector trends and plays]
    
    ⏰ TIMING NOTES:
    • [Best times to enter/exit]
    
    ⚠️ MAJOR RISKS TODAY:
    • [Key risks to watch]
    
    **ANALYSIS PART 1:**
    {analysis1}
    
    **ANALYSIS PART 2:**
    {analysis2}
    """
    
    try:
        print("🔄 Merging analyses and creating final recommendations...")
        
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://your-site-url.com",  # Optional
                "X-Title": "Stock News Analyzer",  # Optional
            },
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": merge_prompt
                }
            ]
        )
        
        final_analysis = completion.choices[0].message.content
        print("✅ Final analysis complete!")
        return final_analysis
            
    except Exception as e:
        print(f"❌ Error during merge: {e}")
        return f"Merge error: {str(e)}"

def analyze_stock_opportunities():
    """Main function - Split data, analyze parts, merge results"""
    
    # Read the news file
    try:
        with open('FULL_INDIAN_STOCK_NEWS.txt', 'r', encoding='utf-8') as file:
            news_content = file.read()
        print("✅ News file loaded successfully!")
        print(f"📰 Total characters: {len(news_content)}")
    except FileNotFoundError:
        print("❌ Error: FULL_INDIAN_STOCK_NEWS.txt not found!")
        return
    except Exception as e:
        print(f"❌ Error reading news file: {e}")
        return
    
    print("\n🔄 Splitting news data to avoid context window limits...")
    
    # Split news into two parts
    news_parts = split_news_data(news_content, num_parts=2)
    
    print(f"\n📊 Starting analysis of {len(news_parts)} parts...")
    
    # Analyze each part separately
    analyses = []
    for i, part in enumerate(news_parts, 1):
        print(f"\n{'='*20} ANALYZING PART {i} {'='*20}")
        analysis = analyze_news_part(part, i)
        analyses.append(analysis)
        
        # Small delay between API calls
        if i < len(news_parts):
            print("⏳ Waiting 5 seconds before next part...")
            import time
            time.sleep(5)
    
    print(f"\n{'='*20} MERGING RESULTS {'='*20}")
    
    # Merge all analyses
    if len(analyses) >= 2:
        final_analysis = merge_analyses(analyses[0], analyses[1])
    else:
        final_analysis = "Analysis incomplete - not enough parts analyzed"
    
    # Display and save results
    print("\n" + "="*80)
    print("📈 FINAL INTRADAY TRADING RECOMMENDATIONS")
    print("="*80)
    print(final_analysis)
    
    # Save to file
    try:
        with open('trading_analysis_output.txt', 'w', encoding='utf-8') as output_file:
            output_file.write("INTRADAY TRADING ANALYSIS (MERGED RESULTS)\n")
            output_file.write("="*60 + "\n")
            output_file.write("Generated by: AI Analysis + Web Search\n")
            output_file.write("Method: Split analysis + merge for context window optimization\n\n")
            output_file.write("PART 1 ANALYSIS:\n")
            output_file.write("-"*30 + "\n")
            output_file.write(analyses[0] if len(analyses) > 0 else "No Part 1 analysis")
            output_file.write("\n\nPART 2 ANALYSIS:\n")
            output_file.write("-"*30 + "\n")
            output_file.write(analyses[1] if len(analyses) > 1 else "No Part 2 analysis")
            output_file.write("\n\nFINAL MERGED RECOMMENDATIONS:\n")
            output_file.write("-"*40 + "\n")
            output_file.write(final_analysis)
        print(f"\n💾 Complete analysis saved to: trading_analysis_output.txt")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

def quick_stock_check(company_name):
    """Quick check for specific company news with web search"""
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )
    
    prompt = f"""
    Search the web for the latest news and developments about {company_name} in the Indian stock market today.
    
    Provide:
    1. Current stock price and today's movement
    2. Latest news affecting the stock
    3. Trading recommendation (BUY/SELL/HOLD)
    4. Intraday strategy if applicable
    5. Key levels to watch
    
    Focus on actionable trading insights for today/tomorrow.
    """
    
    try:
        print(f"🔍 Checking latest updates for: {company_name}")
        
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://your-site-url.com",  # Optional
                "X-Title": "Stock News Analyzer",  # Optional
            },
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        analysis = completion.choices[0].message.content
        print(f"\n📊 ANALYSIS FOR {company_name.upper()}:")
        print("="*50)
        print(analysis)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🎯 INDIAN STOCK MARKET - OPTIMIZED INTRADAY TRADING ANALYZER")
    print("="*70)
    print("📰 Analyzing comprehensive news data in optimized chunks")
    print("🔍 Using AI + Web Search with context window optimization")
    print("⚡ Method: Split → Analyze → Merge for better accuracy")
    print("="*70)
    
    # Run main analysis
    analyze_stock_opportunities()
    
    print("\n" + "="*70)
    print("💡 ADDITIONAL OPTIONS:")
    print("• For specific company check: quick_stock_check('Company Name')")
    print("• Example: quick_stock_check('Reliance Industries')")
    print("• Example: quick_stock_check('TCS')")
    print("="*70)
    print("\n⚠️  DISCLAIMER: This is for educational purposes only.")
    print("    Always do your own research before trading!")
    print("\n📝 Full analysis saved to: trading_analysis_output.txt")