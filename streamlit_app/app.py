import streamlit as st
import requests
import json
import time
from datetime import datetime
import subprocess
import time
import sys
import os
import signal
from typing import List, Dict
import threading
import requests

# Page configuration
st.set_page_config(
    page_title="Finance Assistant",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Morning Market Brief Assistant")
st.markdown("*Multi-Agent Finance Assistant with Voice & Text I/O*")

# Sidebar for configuration
with st.sidebar:
    st.header("🔧 Configuration")
    orchestrator_url = st.text_input("Orchestrator URL", value="http://localhost:8005")
    
    st.header("📊 Service Status")
    if st.button("Check Health"):
        try:
            health_response = requests.get(f"{orchestrator_url}/health", timeout=5)
            if health_response.status_code == 200:
                health_data = health_response.json()
                st.success("Orchestrator: ✅ Healthy")
                
                for service, status in health_data.get("services", {}).items():
                    if status == "healthy":
                        st.success(f"{service}: ✅ Healthy")
                    elif status == "unhealthy":
                        st.warning(f"{service}: ⚠️ Unhealthy")
                    else:
                        st.error(f"{service}: ❌ Unreachable")
            else:
                st.error("❌ Orchestrator unreachable")
        except Exception as e:
            st.error(f"❌ Health check failed: {str(e)}")

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Query Interface")
    
    # Default query
    default_query = "What's our risk exposure in Asia tech stocks today, and highlight any earnings surprises?"
    query = st.text_area(
        "Market Question:",
        value=default_query,
        height=100,
        help="Ask about portfolio risk, market analysis, or earnings information"
    )
    
    # Portfolio input
    st.subheader("💼 Portfolio Configuration")
    default_portfolio = {
        "TSMC (Asia Tech)": 1000000,
        "Samsung Electronics": 1500000,
        "Apple Inc": 2000000,
        "Taiwan Semiconductor": 800000,
        "SK Hynix": 600000
    }
    
    portfolio_str = st.text_area(
        "Portfolio JSON:",
        value=json.dumps(default_portfolio, indent=2),
        height=150,
        help="Enter your portfolio holdings in JSON format"
    )
    
    # Context documents
    st.subheader("📋 Market Context")
    default_context = """
    TSMC Q4 2024 earnings beat expectations by 4%, reporting revenue of $23.7B vs $22.8B estimate.
    Samsung Electronics missed Q4 estimates by 2%, with semiconductor division showing weakness.
    Asia tech sector showing mixed signals with regulatory concerns in China offset by AI chip demand.
    Rising interest rates in the region creating headwinds for growth stocks.
    Geopolitical tensions around Taiwan continue to create uncertainty for semiconductor supply chains.
    """
    
    context = st.text_area(
        "Context Documents:",
        value=default_context.strip(),
        height=200,
        help="Provide relevant market news, earnings reports, or analysis"
    )

with col2:
    st.header("🎙️ Voice Interface")
    st.info("Voice features coming soon...")
    
    # Audio upload placeholder
    audio_file = st.file_uploader(
        "Upload Audio Query",
        type=['wav', 'mp3', 'mp4'],
        help="Upload audio file for speech-to-text processing"
    )
    
    if audio_file:
        st.audio(audio_file)
        if st.button("🎤 Process Audio"):
            st.info("Audio processing not yet implemented")
    
    st.markdown("---")
    st.markdown("### 🔊 Text-to-Speech")
    if st.button("🗣️ Enable Voice Output"):
        st.info("TTS will be enabled in response")

# Generate brief button
st.markdown("---")
if st.button("🚀 Generate Market Brief", type="primary", use_container_width=True):
    
    # Validate inputs
    try:
        portfolio = json.loads(portfolio_str)
    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid Portfolio JSON: {str(e)}")
        st.stop()
    
    if not query.strip():
        st.error("❌ Please enter a market question")
        st.stop()
    
    # Show loading
    with st.spinner("🔄 Generating market brief..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Update progress
            status_text.text("📡 Contacting orchestrator...")
            progress_bar.progress(20)
            
            # Make request to orchestrator
            response = requests.post(
                f"{orchestrator_url}/brief",
                json={
                    "query": query,
                    "portfolio": portfolio,
                    "context": context
                },
                timeout=30
            )
            
            progress_bar.progress(60)
            status_text.text("🤖 Processing with AI agents...")
            
            if response.status_code == 200:
                data = response.json()
                progress_bar.progress(100)
                status_text.text("✅ Brief generated successfully!")
                
                # Display results
                st.success("📊 Market Brief Generated Successfully!")
                
                # Main summary
                st.header("📝 Executive Summary")
                summary = data.get("summary", "No summary available")
                st.markdown(summary)
                
                # Risk exposure
                if data.get("exposure"):
                    st.header("⚖️ Risk Exposure Analysis")
                    st.info(data["exposure"])
                
                # Market data
                if data.get("market_data"):
                    st.header("📈 Market Data")
                    market_data = data["market_data"]
                    
                    # Create columns for market data
                    if market_data:
                        cols = st.columns(min(len(market_data), 3))
                        for i, (ticker, ticker_data) in enumerate(market_data.items()):
                            with cols[i % 3]:
                                if "error" not in ticker_data:
                                    st.metric(
                                        label=f"{ticker}",
                                        value=f"${ticker_data.get('current_price', 'N/A'):.2f}" if ticker_data.get('current_price') else "N/A",
                                        delta=f"{ticker_data.get('change_pct', 0):.2f}%" if ticker_data.get('change_pct') else None
                                    )
                                    st.caption(f"Sector: {ticker_data.get('sector', 'N/A')}")
                                else:
                                    st.error(f"{ticker}: Data unavailable")
                
                # Retrieved documents
                if data.get("documents"):
                    st.header("📚 Source Documents")
                    with st.expander("View Retrieved Context"):
                        for i, doc in enumerate(data["documents"], 1):
                            st.markdown(f"**Document {i}:**")
                            st.text(doc)
                
                # Raw response (for debugging)
                with st.expander("🔍 Raw API Response"):
                    st.json(data)
                    
            else:
                st.error(f"❌ API Error: {response.status_code}")
                st.text(response.text)
                
        except requests.exceptions.Timeout:
            st.error("⏰ Request timed out. Please check if all services are running.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection failed. Please verify the orchestrator URL and service status.")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
        finally:
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🤖 Multi-Agent Finance Assistant | Built with FastAPI, Streamlit & AI</p>
        <p>⚠️ For educational purposes only. Not financial advice.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Auto-refresh option
if st.checkbox("🔄 Auto-refresh every 5 minutes"):
    time.sleep(300)  # 5 minutes
    st.experimental_rerun()



class ServiceManager:
    def __init__(self):
        self.services = {
            "api_agent": {"port": 8001, "file": "agents/api_agent.py", "process": None},
            "retriever_agent": {"port": 8002, "file": "agents/retriever_agent.py", "process": None},
            "analysis_agent": {"port": 8003, "file": "agents/analysis_agent.py", "process": None},
            "language_agent": {"port": 8004, "file": "agents/language_agent.py", "process": None},
            "orchestrator": {"port": 8005, "file": "orchestrator/main.py", "process": None},
            "voice_agent": {"port": 8006, "file": "agents/voice_agent.py", "process": None},
            "scraping_agent": {"port": 8007, "file": "agents/scraping_agent.py", "process": None}
        }
        self.running = True

    def start_service(self, name: str, config: Dict) -> bool:
        """Start a single service"""
        try:
            print(f"🚀 Starting {name} on port {config['port']}...")
            
            # Check if file exists
            if not os.path.exists(config['file']):
                print(f"❌ Error: {config['file']} not found!")
                return False
            
            # Start the service
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn",
                config['file'].replace('/', '.').replace('.py', '') + ":app",
                "--host", "0.0.0.0",
                "--port", str(config['port']),
                "--reload"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            config['process'] = process
            print(f"✅ {name} started with PID {process.pid}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {name}: {str(e)}")
            return False

    def check_service_health(self, name: str, port: int) -> bool:
        """Check if a service is responding"""
        try:
            response = requests.get(f"http://localhost:{port}/docs", timeout=2)
            return response.status_code == 200
        except:
            return False

    def start_all_services(self):
        """Start all services"""
        print("🏁 Starting Finance Assistant Multi-Agent System...")
        print("=" * 60)
        
        success_count = 0
        for name, config in self.services.items():
            if self.start_service(name, config):
                success_count += 1
            time.sleep(2)  # Give each service time to start
        
        print("\n" + "=" * 60)
        print(f"✅ Started {success_count}/{len(self.services)} services")
        
        # Wait for services to be ready
        print("\n⏳ Waiting for services to be ready...")
        time.sleep(5)
        
        # Check health
        print("\n🏥 Health Check:")
        healthy_services = 0
        for name, config in self.services.items():
            if self.check_service_health(name, config['port']):
                print(f"✅ {name}: Healthy")
                healthy_services += 1
            else:
                print(f"❌ {name}: Not responding")
        
        print(f"\n📊 {healthy_services}/{len(self.services)} services are healthy")
        
        if healthy_services > 0:
            print("\n🎉 Finance Assistant is ready!")
            print("\n📋 Service URLs:")
            for name, config in self.services.items():
                print(f"   • {name}: http://localhost:{config['port']}/docs")
            
            print(f"\n🌐 Streamlit App: http://localhost:8501")
            print("💡 Run 'streamlit run streamlit_app/app.py' in another terminal")
        
        return healthy_services > 0

    def stop_all_services(self):
        """Stop all running services"""
        print("\n🛑 Stopping all services...")
        self.running = False
        
        for name, config in self.services.items():
            if config['process']:
                try:
                    config['process'].terminate()
                    config['process'].wait(timeout=5)
                    print(f"✅ Stopped {name}")
                except subprocess.TimeoutExpired:
                    config['process'].kill()
                    print(f"🔪 Force killed {name}")
                except Exception as e:
                    print(f"❌ Error stopping {name}: {str(e)}")

    def monitor_services(self):
        """Monitor running services"""
        while self.running:
            time.sleep(30)  # Check every 30 seconds
            
            for name, config in self.services.items():
                if config['process'] and config['process'].poll() is not None:
                    print(f"⚠️  {name} has stopped unexpectedly!")
                    # Optionally restart the service
                    # self.start_service(name, config)

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n\n🛑 Received interrupt signal...')
    if 'manager' in globals():
        manager.stop_all_services()
    sys.exit(0)



def main():
    global manager
    
    # Set up signal handling
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    manager = ServiceManager()
    
    try:
        # Start all services
        if manager.start_all_services():
            print("\n🔄 Services are running. Press Ctrl+C to stop.")
            
            # Start monitoring in a separate thread
            monitor_thread = threading.Thread(target=manager.monitor_services)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Keep the main thread alive
            while manager.running:
                time.sleep(1)
        else:
            print("❌ Failed to start services properly")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    finally:
        manager.stop_all_services()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
