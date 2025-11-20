import os
from datetime import date, datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import Client, create_client

load_dotenv()

app = FastAPI()

# Supabase setup
url: str = os.environ.get("SUPABASE_ENDPOINT")
# Use service role key to bypass RLS policies
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

TABLE_NAME = os.environ.get("TABLE_NAME")


class Claim(BaseModel):
    claim_number: Optional[str] = None
    claim_status: Optional[str] = None
    created_timestamp: Optional[datetime] = None
    report_date: Optional[date] = None
    policy_number: Optional[str] = None
    claimant_first_name: Optional[str] = None
    claimant_last_name: Optional[str] = None
    claimant_phone: Optional[str] = None
    claimant_email: Optional[str] = None
    vehicle_vin: Optional[str] = None
    vehicle_year: Optional[int] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    loss_date: Optional[date] = None
    loss_location: Optional[str] = None
    loss_type: Optional[str] = None
    injury_involved: Optional[bool] = None
    police_report_filed: Optional[bool] = None
    accident_description: Optional[str] = None
    adjuster_id: Optional[str] = None
    coverage_confirmed: Optional[bool] = None
    deductible_amount: Optional[float] = None
    subrogation_potential: Optional[bool] = None
    triage_completed: Optional[datetime] = None
    first_contact_date: Optional[datetime] = None
    inspection_completed: Optional[datetime] = None
    damage_assessment: Optional[float] = None
    repair_authorized: Optional[bool] = None
    repair_shop_name: Optional[str] = None
    payment_amount: Optional[float] = None
    payment_date: Optional[datetime] = None
    subrogation_demand_sent: Optional[bool] = None
    claim_closed_date: Optional[datetime] = None
    closure_reason: Optional[str] = None
    cycle_time_days: Optional[int] = None
    customer_satisfaction: Optional[float] = None


@app.get("/claims", response_model=list[Claim])
async def get_claims():
    """
    Retrieve all claims from the Supabase table.
    """
    response = supabase.table(TABLE_NAME).select("*").execute()
    if response.data:
        return response.data
    return []


@app.post("/claims", response_model=Claim)
async def create_claim(claim: Claim):
    """
    Create a new claim in the Supabase table.
    """
    claim_data = claim.dict(exclude_unset=True)
    for key, value in claim_data.items():
        if isinstance(value, (datetime, date)):
            claim_data[key] = value.isoformat()

    response = supabase.table(TABLE_NAME).insert(claim_data).execute()
    if response.data:
        return response.data[0]
    raise HTTPException(status_code=400, detail="Claim could not be created.")


@app.delete("/claims/{claim_number}", response_model=dict)
async def delete_claim(claim_number: str):
    """
    Delete a claim from the Supabase table by claim_number.
    """
    response = (
        supabase.table(TABLE_NAME).delete().eq("claim_number", claim_number).execute()
    )
    if response.data:
        return {"message": f"Claim {claim_number} deleted successfully."}
    raise HTTPException(status_code=404, detail=f"Claim {claim_number} not found.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
