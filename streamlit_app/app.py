# import streamlit as st
# import requests
# import json

# st.title("📈 Morning Market Brief Assistant")

# query = st.text_input("Ask a Market Question:", value="What’s our risk exposure in Asia tech stocks today, and highlight any earnings surprises?")
# portfolio_str = st.text_area("Paste Your Portfolio JSON:", value='{"TSMC (Asia Tech)": 1000000, "Samsung": 1500000, "Apple": 2000000}')
# texts = st.text_area("Context Documents:", value="TSMC earnings beat expectations by 4%. Samsung missed estimates by 2%.")

# if st.button("Generate Market Brief"):
#     try:
#         portfolio = json.loads(portfolio_str)
#         res = requests.post("http://localhost:8005/brief", json={
#             "query": query,
#             "portfolio": portfolio,
#             "texts": [texts]
#         })
#         data = res.json()
#         st.subheader("📊 Summary")
#         st.write(data["summary"])
#         st.subheader("📌 Exposure")
#         st.json(data["exposure"])
#     except Exception as e:
#         st.error(f"Error: {e}")


import streamlit as st
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Morning Market Brief", page_icon="📈")
st.title("📈 Morning Market Brief Assistant")

# Input fields
query = st.text_input(
    "Ask a Market Question:", 
    value="What's our risk exposure in Asia tech stocks today, and highlight any earnings surprises?"
)

portfolio_str = st.text_area(
    "Paste Your Portfolio JSON:", 
    value='{"TSMC (Asia Tech)": 1000000, "Samsung": 1500000, "Apple": 2000000}',
    height=100
)

context_text = st.text_area(
    "Context Documents:", 
    value="TSMC earnings beat expectations by 4%. Samsung missed estimates by 2%.",
    height=100
)

if st.button("Generate Market Brief", type="primary"):
    if not query.strip():
        st.error("Please enter a market question.")
    else:
        try:
            # Parse portfolio JSON
            try:
                portfolio = json.loads(portfolio_str) if portfolio_str.strip() else {}
            except json.JSONDecodeError as e:
                st.error(f"Invalid portfolio JSON: {e}")
                st.stop()

            # Show loading spinner
            with st.spinner("Generating market brief..."):
                # Make request to orchestrator
                response = requests.post(
                    "http://localhost:8005/brief", 
                    json={
                        "query": query,
                        "portfolio": portfolio,
                        "context": context_text,
                        "texts": [context_text] if context_text.strip() else []
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Display results
                    st.subheader("📊 AI Summary")
                    summary = data.get("summary", "No summary available")
                    st.write(summary)
                    
                    st.subheader("📌 Risk Exposure Analysis")
                    exposure = data.get("exposure", {})
                    if isinstance(exposure, dict) and "error" not in exposure:
                        if "exposure" in exposure:
                            st.info(exposure["exposure"])
                        if "details" in exposure and exposure["details"]:
                            st.subheader("Detailed Breakdown:")
                            for asset, value in exposure["details"].items():
                                st.write(f"• **{asset}**: ${value:,.2f}")
                        if "total_exposure_value" in exposure:
                            st.metric(
                                "Total Asia Tech Exposure", 
                                f"${exposure['total_exposure_value']:,.2f}"
                            )
                    else:
                        st.error(f"Exposure analysis error: {exposure}")
                    
                    # Show retrieved documents
                    with st.expander("📄 Retrieved Context Documents"):
                        documents = data.get("documents", [])
                        for i, doc in enumerate(documents, 1):
                            st.write(f"**Document {i}:** {doc}")
                
                else:
                    st.error(f"Service returned status code: {response.status_code}")
                    st.text(response.text)
                    
        except requests.RequestException as e:
            st.error(f"Connection error: {e}")
            st.info("Make sure all microservices are running on their respective ports.")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            logger.error(f"Streamlit error: {e}")

# Add service status check
st.sidebar.subheader("🔧 Service Status")
if st.sidebar.button("Check Services"):
    services = {
        "Retriever (8002)": "http://localhost:8002/retrieve?query=test",
        "Analysis (8003)": None,  # POST only
        "Language (8004)": None,  # POST only  
        "Orchestrator (8005)": None  # POST only
    }
    
    for service_name, url in services.items():
        if url:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    st.sidebar.success(f"✅ {service_name}")
                else:
                    st.sidebar.error(f"❌ {service_name}")
            except:
                st.sidebar.error(f"❌ {service_name}")
        else:
            st.sidebar.info(f"ℹ️ {service_name} (POST only)")