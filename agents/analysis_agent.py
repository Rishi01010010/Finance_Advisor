# from fastapi import FastAPI, Request
# from typing import Dict
# from fastapi.responses import JSONResponse

# app = FastAPI()

# @app.post("/risk_exposure")
# async def calculate_exposure(request: Request):
#     try:
#         data = await request.json()
#         portfolio: Dict[str, float] = data.get("portfolio", {})

#         exposure_report = {
#             asset: value
#             for asset, value in portfolio.items()
#             if any(term in asset.lower() for term in ["asia", "tsmc", "samsung"])
#         }

#         total_exposure = sum(exposure_report.values())
#         total_value = sum(portfolio.values())
#         percent_exposure = (total_exposure / total_value) * 100 if total_value > 0 else 0

#         return JSONResponse(content={
#             "exposure": f"{percent_exposure:.2f}% of your portfolio is exposed to Asia tech stocks.",
#             "details": exposure_report
#         })

#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=400)


from fastapi import FastAPI, Request
from typing import Dict
from fastapi.responses import JSONResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/risk_exposure")
async def calculate_exposure(request: Request):
    try:
        data = await request.json()
        portfolio: Dict[str, float] = data.get("portfolio", {})
        
        if not portfolio:
            return JSONResponse(content={
                "exposure": "0.00% - No portfolio data provided",
                "details": {}
            })

        # Look for Asia tech exposure
        exposure_report = {}
        for asset, value in portfolio.items():
            if any(term in asset.lower() for term in ["asia", "tsmc", "samsung", "taiwan", "korea", "china"]):
                exposure_report[asset] = value

        total_exposure = sum(exposure_report.values())
        total_value = sum(portfolio.values())
        percent_exposure = (total_exposure / total_value) * 100 if total_value > 0 else 0

        response_data = {
            "exposure": f"{percent_exposure:.2f}% of your portfolio is exposed to Asia tech stocks.",
            "details": exposure_report,
            "total_exposure_value": total_exposure,
            "total_portfolio_value": total_value
        }
        
        logger.info(f"Calculated exposure: {response_data}")
        return JSONResponse(content=response_data)

    except Exception as e:
        logger.error(f"Error in calculate_exposure: {str(e)}")
        return JSONResponse(
            content={"error": f"Analysis error: {str(e)}"}, 
            status_code=400
        )