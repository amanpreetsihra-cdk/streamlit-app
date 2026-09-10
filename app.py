import streamlit as st
import requests
import json
import re
from typing import Any, Dict
import difflib
from html import escape

st.set_page_config(page_title="AWP Claim Analyzer", layout="wide")

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Metric cards ── */
div[data-testid="stMetric"] {
    border: none !important;
    box-shadow: none !important;
}
div[data-testid="stMetric"] label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #94a3b8 !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

/* ── Tabs ── */
button[data-baseweb="tab"] {
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}
/* ── Expander cards ── */
div[data-testid="stExpander"] {
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

/* ── Primary button ── */
button[kind="primary"] {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: transform 0.1s ease, box-shadow 0.15s ease;
}
button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

/* ── JSON viewer ── */
div[data-testid="stJson"] {
    background: #000000 !important;
    border-radius: 10px;
    border: 1px solid #333333;
    color: #ffffff !important;
}

/* ── Tab content panels ── */
div[data-testid="stTabs"] [role="tabpanel"],
div[data-testid="stTabs"] [role="tabpanel"] div,
div[data-testid="stTabs"] [role="tabpanel"] section {
    background: #000000 !important;
}
div[data-testid="stTabs"] [role="tabpanel"] {
    border-radius: 0 0 10px 10px;
    padding: 12px;
}
div[data-testid="stTabs"] [role="tabpanel"] * {
    color: #ffffff !important;
}

/* ── Text input / text area ── */
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
    border-radius: 8px !important;
}

/* ── File uploader ── */
div[data-testid="stFileUploader"] section {
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Styled header ────────────────────────────────────────────────────────────
st.markdown(
    '<div style="background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 50%,#3b82f6 100%);'
    'padding:2rem 2.5rem;border-radius:16px;margin-bottom:1.5rem;'
    'box-shadow:0 4px 20px rgba(37,99,235,0.25);">'
    '<h1 style="color:white;margin:0;font-size:2.2rem;font-weight:800;'
    'letter-spacing:-0.02em;">'
    'AWP Claim Analyzer</h1>'
    '<p style="color:rgba(255,255,255,0.85);margin:0.5rem 0 0;font-size:1.05rem;">'
    'Takes a warranty claim and returns the most relevant repair operation code, '
    'ranked by confidence.</p></div>',
    unsafe_allow_html=True,
)

DEMO_CLAIM = {"header":{"claimHeaderId":None,"customerName":"MEHRIAN,SHIRIN","customerNumber":"86547","vin":"SALKP9E99SA295637","isOEMVin":None,"vehicleId":"SA295637","vehicle":None,"brand":"LAND_ROVER","make":"LAND","fullMake":"LAND ROVER","model":"RANGE ROVER","year":"2025","status":"CLOSED","fleet":None,"dealerCountry":"U","dealerCode":"0432","fullDealerCode":"P4038R0432","repairOrderId":"108635","externalRepairOrderId":None,"departmentId":None,"defaultOdometerUom":"MI","stateOfRegistration":None,"openDate":"2026-07-08","closeDate":"2026-07-31","vehicleSoldDate":None,"odometerReadingDate":"2026-07-08","odometerReadingTime":"09:53:06","vehicleDateIn":"2026-07-08","vehicleDateOut":"2026-07-31","isDistanceOverride":None,"lastKnownMileage":5453,"mileageIn":6683,"mileageOut":6710,"fieldServiceActionOptionCode":None,"appealCode":None,"appealComment":None,"approvalCodes":[],"isActive":False,"isRelatedDamage":False,"isReciprocalTransaction":None,"validationErrors":[],"manufacturerCode":"LAR","manufacturerNumber":"167","confirmFullServHistory":False,"customerContactDate":None,"customerContactIndicator":False,"customerContactTime":None,"customerHomePhone":None,"daysInShop":0},"detail":[{"claimDetailId":None,"roLineId":"C","externalLineId":None,"retailerReference":"108635C","source":"RO","status":"CREATED_BY_CLOSED_RO","repairOrderLineStatus":None,"oemClaimNumber":None,"claimTypeCode":"11","warrantyCause":"RVC: TSOOFA2R","customerComplaint":"CUSTOMER STATES ON A DAILY BASIS VEHICLE HAS A ROUGH IDLE CHECK AND ADVISE","causeCode":None,"complaintCode":None,"complaintCodeCategory":None,"technicalDescription":"6686 RVC: TSOOFA2R CONFIRMED CLIENT'S CONCERN. DIAGNOSED AND NO RELATED FAULT CODES STORED. UTILIZED MISFIRE COUNTER AND FOUND NUMBER 7 CYLINDER WITH EVIDENCE OF MISFIRE. REMOVED SPARK PLUGS AND FOUND INSULATOR FOR NUMBER 7 SPARK PLUG LOOSE AND PARTIALLY COVERING ELECTRODE AND 5, 6, AND 8 SPARK PLUGS WITH EVIDENCE OF FOULING. CREATED TECHNICAL ASSISTANCE CASE #4184514. RENEWED NUMBER 5, 6, 7, AND NUMBER 8 SPARK PLUGS. CLEARED PCM ADAPTIONS AND ROAD TESTED... NO RECURRING FAULT CODES STORED, HOWEVER, ENGINE CONTINUES TO RUN ROUGH. REMOVED SPARK PLUGS AND PERFORMED BORESCOPE INSPECTION OF ALL 8 CYLINDERS. SUPPLIED IMAGES TO TA. RENEWED CYLINDER NUMBER 1, 2, 3, AND 4 SPARK PLUGS. RESET PCM AND PCMB ADAPTIONS, PERFORMED LEARN VARIABLE VALVE LIFT ADAPTION ROUTINE FOR PCM AND PCMB, PERFORMED THROTTLE VALVE ACTUATOR REPLACEMENT ROUTINE ON PCM AND PCMB. ALLOWED ENGINE TO IDLE FOR 40 MINUTES. CLEARED FAULT CODES, ADDED FUEL INJECTOR CLEANER AND PERFORMED HIGH LOAD DRIVE CYCLE. ALLOWED ENGINE TO IDLE FOR ONE HOUR AND PERFORMED QUALITY CONTROL ROAD TEST. RECHECKED FOR FAULT CODES AND NO RELATED FAULT CODES STORED AFTER PROCEDURES.","isRelatedDamage":None,"damageCode":None,"approvalCodes":None,"repairFleet":None,"isAuthorizationRequested":None,"authorizationRequestReason":None,"warrantyAuthorizationReason":None,"isManualReviewRequired":None,"isAddOnRepair":None,"deductible":None,"customerParticipationAmount":0.00,"customerParticipationPercentage":0,"dealerParticipationAmount":0.00,"dealerParticipationPercentage":0,"oemParticipationAmount":0.00,"oemParticipationPercentage":100,"taxLocal":0.00,"taxCounty":0.00,"taxState":0.00,"taxFed":0.00,"estimate":None,"approvedAmount":None,"totalTaxAmount":0.00,"totalPartsAmount":228.93,"totalExpensesAmount":0.00,"totalLaborAmount":937.89,"totalLaborHours":3.30,"totalHandlingAmount":193.18,"totalClaimAmount":1360.00,"submitDate":None,"billingDate":None,"isAttached":None,"isHoldAtPreValidation":None,"technicianStory":None,"serviceEmployees":None,"repairDateStart":"2026-07-08","repairDateFinish":"2026-07-28","deliveryReceiptDate":None,"deliveryReceiptNumber":None,"carrierCode":None,"authorizationCode":None,"preAuthorizationCode":None,"conditionCode":"CK","customerConcernCode":"SXXV99RVC","programCode":"VW","campaignOptionCode":None,"promptForCausalPart":False,"originalPartReplacementDate":None,"originalPartDistance":0,"originalReplacementRepairOrder":None,"repairMileageOut":None,"repairEngineOperatingHours":None,"generalComments":None,"appealReasonCode":None,"appealComments":None,"authorizationType":None,"claimSummaryVersion":None,"rentalNotes":None,"isSubmissionReady":None,"businessCenter":None,"miscellaneousNotes":None,"authorizationNumber":None,"causalPartNumber":"LR158761","causalPartCondition":"1","causalPartQty":1,"causalLaborOperation":None,"serviceAdvisorName":None,"serviceAdvisorTelephone":None,"dmsServiceAdvisorId":"83182","oemServiceAdvisorId":None,"dmsTechnicianId":None,"oemTechnicianId":None,"technicianName":None,"selectedTechnicianId":None,"technicianDmsIds":["86494"],"technicianManufacturerIds":[],"operations":[{"claimLaborOperationId":None,"sequenceNumber":"12","opCode":"182057","opCodeDescription":"SPARK PLUG - RIGHT BANK - SET - RENEW","laborType":"W","actualHours":0.00,"soldHours":0.90,"saleAmount":255.79,"dealerParticipation":0,"dealerSale":0,"customerParticipation":0,"customerSale":0,"oemParticipation":100,"oemSale":255.79,"technicianNumbers":["86494"],"isCausal":None,"isScratch":False,"isValid":None,"adjustment":None,"toBePaid":None,"value":None,"overlapSRODescr":None,"atdSROTime":None,"sroTimeFlag":None,"sroTimeDescription":None,"repairType":None,"refTypeId":None,"causalSRORefNumber":None,"validationMsg":None,"isSROValid":None,"isOemLabor":False},{"claimLaborOperationId":None,"sequenceNumber":"13","opCode":"851806","opCodeDescription":"READ AND CLEAR FAULT CODES","laborType":"W","actualHours":0.00,"soldHours":0.20,"saleAmount":56.84,"dealerParticipation":0,"dealerSale":0,"customerParticipation":0,"customerSale":0,"oemParticipation":100,"oemSale":56.84,"technicianNumbers":["86494"],"isCausal":None,"isScratch":False,"isValid":None,"adjustment":None,"toBePaid":None,"value":None,"overlapSRODescr":None,"atdSROTime":None,"sroTimeFlag":None,"sroTimeDescription":None,"repairType":None,"refTypeId":None,"causalSRORefNumber":None,"validationMsg":None,"isSROValid":None,"isOemLabor":False},{"claimLaborOperationId":None,"sequenceNumber":"14","opCode":"851810","opCodeDescription":"VARIABLE VALVE LIFT - ADAPTIONS","laborType":"W","actualHours":0.00,"soldHours":0.20,"saleAmount":56.84,"dealerParticipation":0,"dealerSale":0,"customerParticipation":0,"customerSale":0,"oemParticipation":100,"oemSale":56.84,"technicianNumbers":["86494"],"isCausal":None,"isScratch":False,"isValid":None,"adjustment":None,"toBePaid":None,"value":None,"overlapSRODescr":None,"atdSROTime":None,"sroTimeFlag":None,"sroTimeDescription":None,"repairType":None,"refTypeId":None,"causalSRORefNumber":None,"validationMsg":None,"isSROValid":None,"isOemLabor":False},{"claimLaborOperationId":None,"sequenceNumber":"15","opCode":"851807","opCodeDescription":"ELECTRIC THROTTLE VALVE ACTUATOR ADAPTIONS","laborType":"W","actualHours":0.00,"soldHours":0.20,"saleAmount":56.84,"dealerParticipation":0,"dealerSale":0,"customerParticipation":0,"customerSale":0,"oemParticipation":100,"oemSale":56.84,"technicianNumbers":["86494"],"isCausal":None,"isScratch":False,"isValid":None,"adjustment":None,"toBePaid":None,"value":None,"overlapSRODescr":None,"atdSROTime":None,"sroTimeFlag":None,"sroTimeDescription":None,"repairType":None,"refTypeId":None,"causalSRORefNumber":None,"validationMsg":None,"isSROValid":None,"isOemLabor":False},{"claimLaborOperationId":None,"sequenceNumber":"16","opCode":"020202","opCodeDescription":"DRIVE IN-DRIVE OUT","laborType":"W","actualHours":0.00,"soldHours":0.20,"saleAmount":56.84,"dealerParticipation":0,"dealerSale":0,"customerParticipation":0,"customerSale":0,"oemParticipation":100,"oemSale":56.84,"technicianNumbers":["86494"],"isCausal":None,"isScratch":False,"isValid":None,"adjustment":None,"toBePaid":None,"value":None,"overlapSRODescr":None,"atdSROTime":None,"sroTimeFlag":None,"sroTimeDescription":None,"repairType":None,"refTypeId":None,"causalSRORefNumber":None,"validationMsg":None,"isSROValid":None,"isOemLabor":False},{"claimLaborOperationId":None,"sequenceNumber":"3","opCode":"182056","opCodeDescription":"SPARK PLUG - LEFT BANK - SET - RENEW","laborType":"W","actualHours":5.39,"soldHours":1.60,"saleAmount":454.74,"dealerParticipation":0,"dealerSale":0,"customerParticipation":0,"customerSale":0,"oemParticipation":100,"oemSale":454.74,"technicianNumbers":["86494"],"isCausal":None,"isScratch":False,"isValid":None,"adjustment":None,"toBePaid":None,"value":None,"overlapSRODescr":None,"atdSROTime":None,"sroTimeFlag":None,"sroTimeDescription":None,"repairType":None,"refTypeId":None,"causalSRORefNumber":None,"validationMsg":None,"isSROValid":None,"isOemLabor":False}],"parts":[{"claimPartId":None,"partNumber":"LR158761","partSequenceNumber":"1","laborSequenceNumber":"3","laborId":None,"oemPartNumber":None,"prefix":None,"partDescription":"SPARK PLUG","unitOfMeasure":None,"partDistance":None,"partInvoiceNumber":None,"partInvoiceDate":None,"causalConditionCode":None,"quantitySold":8,"costPrice":26.00,"extendedCostPrice":208.00,"salePrice":47.94,"extendedSalePrice":383.52,"coreSalePrice":0.00,"requestedAmount":None,"dealerParticipation":0,"dealerSale":0,"customerParticipation":0,"customerSale":0,"oemParticipation":100,"oemSale":47.94,"coreUnitAmount":None,"handlingPrice":175.52,"serialNumberDetails":None,"isScratch":False,"isCausal":None,"isOemPart":None,"isValid":None,"itemTypeId":None,"optionCode":None,"invoiceNumber":None,"causalPartTypeId":None,"causalPartIndicator":None,"emergencyOrderFlag":None,"handlingPercentage":None,"extendedHandlingAmount":None,"validationMsg":None,"isPartValid":None},{"claimPartId":None,"partNumber":"208","partSequenceNumber":"3","laborSequenceNumber":"3","laborId":None,"oemPartNumber":None,"prefix":None,"partDescription":"44K TREATMENT","unitOfMeasure":None,"partDistance":None,"partInvoiceNumber":None,"partInvoiceDate":None,"causalConditionCode":None,"quantitySold":1,"costPrice":20.93,"extendedCostPrice":20.93,"salePrice":38.59,"extendedSalePrice":38.59,"coreSalePrice":0.00,"requestedAmount":None,"dealerParticipation":0,"dealerSale":0,"customerParticipation":0,"customerSale":0,"oemParticipation":100,"oemSale":38.59,"coreUnitAmount":None,"handlingPrice":17.66,"serialNumberDetails":None,"isScratch":False,"isCausal":None,"isOemPart":None,"isValid":None,"itemTypeId":None,"optionCode":None,"invoiceNumber":None,"causalPartTypeId":None,"causalPartIndicator":None,"emergencyOrderFlag":None,"handlingPercentage":None,"extendedHandlingAmount":None,"validationMsg":None,"isPartValid":None}],"expenses":[],"claimInfo":{"causalPartTypeId":None,"approver":None,"approvalFlag":None,"jobCardNo":"108635","dtcs":[],"template":None,"techRefTypeId":"00","techRefNumber":None,"labourContribution":None,"materialContribution":None,"miscContribution":None,"ncsCentralVersion":None,"participationTypeId":None,"goodwillCategory":None,"reasonCode":None,"goodwillTypeId":None,"authorityCode":None,"authorizeType":None,"crcCaseNo":None,"reasonForApproval":None,"requestedDays":None,"stolenFlag":None,"newVehicleFlag":None,"bookingType":None,"refClaimClaimedDays":None,"campaignOption":None,"claimNote":None},"batteryInfo":{"testerType":None,"testerCode1":None,"testerCode2":None,"testerCode3":None},"mobilityInfo":{"vehicleType":None,"reasonCode":None,"vin":None,"vehicleMake":None,"vehicleModel":None,"vehicleComments":None,"refClaimStatus":None,"refClaimBOType":None,"refClaimBONumber":None},"calcTypeId":None,"vinGroup":None,"claimStatus":None,"claimStatusDesc":None,"isAppealAllowed":True,"isChargebackAllowed":True,"isModifyAllowed":True,"isLaborPartsLoaded":False,"isRVCItemsLoaded":False,"isClaimPaid":False,"isPreAuthorization":False}],"errors": None
}

def clean_json_string(json_str: str) -> str:
    """
    Clean JSON string by:
    1. Replacing 'None' with 'null'
    2. Removing trailing commas
    """
    # Skip quoted strings so complaint/narrative text is never modified.
    return re.sub(
        r'"(?:\\.|[^"\\])*"|(?P<none>\bNone\b)|(?P<comma>,(?=\s*[}\]]))',
        lambda match: "null" if match.lastgroup == "none" else
        "" if match.lastgroup == "comma" else match.group(0),
        json_str,
    )

def wrap_with_data_and_inputs(data_obj: Dict) -> Dict:
    """
    Wraps the data object with 'data' and 'inputs' fields.
    Inputs stores the data as a list.

    Example:
    Input: {"header": {...}}
    Output: {"inputs": [{"data": {"header": {...}}}]}
    """
    return {
        "inputs": [{
            "data": data_obj
        }],
    }


def clear_analysis():
    for key in ("response", "response_time", "submitted_claim", "request_details"):
        st.session_state.pop(key, None)


def new_claim():
    clear_analysis()
    st.session_state.claim_draft = json.dumps(DEMO_CLAIM, indent=2)
    st.session_state.claim_json = st.session_state.claim_draft
    st.session_state.input_mode = "Type JSON"
    # File-uploader values cannot be assigned directly; use a fresh widget key.
    st.session_state.upload_generation += 1
    for key in ("uploaded_text", "uploaded_name", "upload_error"):
        st.session_state.pop(key, None)


def save_draft():
    st.session_state.claim_draft = st.session_state.claim_json
    clear_analysis()


def load_upload(widget_key):
    clear_analysis()
    for key in ("uploaded_text", "uploaded_name", "upload_error"):
        st.session_state.pop(key, None)
    uploaded = st.session_state.get(widget_key)
    if uploaded is not None:
        try:
            text = uploaded.getvalue().decode("utf-8-sig")
            parse_claim(text)
            st.session_state.uploaded_text = text
            st.session_state.uploaded_name = uploaded.name
        except (UnicodeDecodeError, ValueError) as exc:
            st.session_state.upload_error = f"Upload a valid UTF-8 JSON claim: {exc}"


def parse_claim(text):
    if not text or not text.strip():
        raise ValueError("Enter or upload a claim before requesting a recommendation.")
    claim = json.loads(clean_json_string(text))
    if not isinstance(claim, dict) or not claim:
        raise ValueError("The claim must be a non-empty JSON object.")
    return claim


def show_comparison(before, after):
    """Show only changed lines from the submitted object and prediction."""
    left = json.dumps(before, indent=2, ensure_ascii=False, sort_keys=True).splitlines()
    right = json.dumps(after, indent=2, ensure_ascii=False, sort_keys=True).splitlines()
    left_lines, right_lines = [], []

    def line_html(line, changed, added=False):
        background = ("#dcfce7" if added else "#fee2e2") if changed else "transparent"
        color = ("#14532d" if added else "#7f1d1d") if changed else "inherit"
        marker = ("+ " if added else "− ") if changed else "  "
        return (
            f'<div style="background:{background};color:{color};padding:2px 6px;'
            'white-space:pre-wrap;overflow-wrap:anywhere;">'
            f'{marker}{escape(line)}</div>'
        )

    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, left, right, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        left_lines.extend(line_html(line, tag != "equal") for line in left[i1:i2])
        right_lines.extend(line_html(line, tag != "equal", added=True) for line in right[j1:j2])

    if not left_lines and not right_lines:
        st.info("No differences found between the submitted claim and prediction.")
        return

    before_col, after_col = st.columns(2)
    for col, title, lines in (
        (before_col, "Before analysis · Submitted claim", left_lines),
        (after_col, "After analysis · API output", right_lines),
    ):
        with col:
            st.markdown(f"**{title}**")
            if not lines:
                st.caption("No changed lines on this side.")
                continue
            st.markdown(
                '<div style="font-family:monospace;font-size:0.85rem;'
                'border:1px solid #94a3b8;border-radius:8px;padding:8px;">'
                + "".join(lines) + "</div>",
                unsafe_allow_html=True,
            )


st.session_state.setdefault("claim_draft", json.dumps(DEMO_CLAIM, indent=2))
st.session_state.setdefault("upload_generation", 0)
st.session_state.setdefault("input_mode", "Type JSON")

# Sidebar configuration
with st.sidebar:
    st.header("Connection Settings")

    # Endpoint URL
    endpoint = st.text_input(
        "Endpoint URL",
        placeholder="https://api.example.com/endpoint",
        help="Full URL of the API endpoint"
    )

    # Token/API Key
    st.subheader("Authentication")
    token = st.text_input(
        "Token/API Key",
        type="password",
        placeholder="your-token-here",
        help="Bearer token or API key if needed"
    )

    if token:
        st.caption("Token will be added to Authorization header")

    # Auto-wrap option
    st.subheader("JSON Wrapping")
    auto_wrap = st.checkbox(
        "Auto-wrap JSON",
        value=True,
        help="Automatically wrap JSON with 'data' and 'inputs' fields"
    )

    st.subheader("Query Parameters")
    use_query_params = st.checkbox(
        "Add section",
        value=False,
        help="Add section to include query parameters in request"
    )

    # Timeout
    timeout = st.number_input("Timeout (seconds)", min_value=1, max_value=300, value=100)

if "response" in st.session_state:
    st.button("New Claim", on_click=new_claim)

if "response" not in st.session_state:
    input_mode = st.radio(
        "Claim input", ["Type JSON", "Upload JSON"], horizontal=True,
        key="input_mode", on_change=clear_analysis,
    )

    if use_query_params:
        col1, col2 = st.columns(2)
    else:
        col1, = st.columns(1)

    # Left column - Request configuration
    with col1:
        st.subheader("Request Body")
        if input_mode == "Type JSON":
            st.session_state.setdefault("claim_json", st.session_state.claim_draft)
            request_body = st.text_area(
                "Body (JSON)", height=200, key="claim_json", on_change=save_draft,
                help="Type or paste the claim JSON."
            )
        else:
            upload_key = f"claim_upload_{st.session_state.upload_generation}"
            st.file_uploader(
                "Upload a claim JSON file", type=["json"], key=upload_key,
                on_change=load_upload, args=(upload_key,),
            )
            request_body = st.session_state.get("uploaded_text", "")
            if "upload_error" in st.session_state:
                st.error(st.session_state.upload_error)
            elif request_body:
                st.caption(f'Loaded: {st.session_state.uploaded_name}')
                with st.expander("Preview uploaded claim"):
                    st.json(parse_claim(request_body))

    # Right column - Query Parameters
    if use_query_params:
        with col2:
            st.subheader("Query Parameters")
            query_params_text = st.text_area(
                "Query Parameters (JSON)",
                value='{}',
                height=200,
                help="Provide query parameters as JSON object (supports trailing commas and None values)"
            )

    # Send button
    st.divider()
    if st.button("Get Recommendation", type="primary", use_container_width=True):
        clear_analysis()
        if not endpoint:
            st.error("Please enter an endpoint URL")
        else:
            try:
                # Parse headers
                try:
                    headers = {"Content-Type": "application/json"}
                except json.JSONDecodeError as e:
                    st.error(f"Invalid Headers JSON: {e}")
                    headers = {}

                # Add token to headers if provided
                if token:
                    headers["Authorization"] = f"Bearer {token}"

                # Invalid input must not be sent to the endpoint.
                if use_query_params:
                    params_cleaned = clean_json_string(query_params_text)
                    params = json.loads(params_cleaned) if params_cleaned.strip() else {}
                    if not isinstance(params, dict):
                        raise ValueError("Query parameters must be a JSON object.")
                else:
                    params = {}

                body = parse_claim(request_body)
                # Snapshot before wrapping, so later edits cannot change the comparison.
                submitted_claim = json.loads(json.dumps(body))

                # Auto-wrap with data and inputs if enabled
                if auto_wrap and body:
                    body = wrap_with_data_and_inputs(body)

                # Make POST request
                with st.spinner("Analyzing claim — please wait..."):
                    response = requests.post(endpoint, headers=headers, params=params, json=body, timeout=timeout)

                st.session_state.response = response
                st.session_state.submitted_claim = submitted_claim
                st.session_state.response_time = response.elapsed.total_seconds()
                st.session_state.request_details = {
                    "method": "POST",
                    "endpoint": endpoint
                }
                # Switch to results only after the endpoint returns.
                st.rerun()

            except ValueError as e:
                st.error(f"Invalid input: {e}")
            except requests.exceptions.Timeout:
                st.error("Request timed out. Try increasing the timeout value.")
            except requests.exceptions.ConnectionError:
                st.error("Connection error. Check the endpoint URL and your internet connection.")
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {str(e)}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Render the response once, only after the request completes.
if "response" in st.session_state:
    response = st.session_state.response
    response_time = st.session_state.response_time

    st.divider()
    st.subheader("📤 Response")

    # Response metadata cards
    m1, m2, m3 = st.columns(3)
    with m1:
        status_color = "🟢" if response.status_code < 400 else "🔴"
        st.metric("Status Code", f"{status_color} {response.status_code}")
    with m2:
        st.metric("Response Time", f"{response_time:.2f}s")
    with m3:
        try:
            resp_size = len(response.content)
            size_label = f"{resp_size / 1024:.1f} KB" if resp_size >= 1024 else f"{resp_size} B"
        except Exception:
            size_label = "—"
        st.metric("Response Size", size_label)

    try:
        response_json = response.json()
        response_is_json = True
    except ValueError:
        response_json = None
        response_is_json = False

    # The endpoint wraps the single-claim result inside predictions.
    prediction_missing = False
    if response_is_json and 200 <= response.status_code < 300:
        if isinstance(response_json, dict) and "predictions" in response_json:
            predictions = response_json["predictions"]
            if isinstance(predictions, list):
                response_json = predictions[0] if predictions else None
                if len(predictions) > 1:
                    st.caption("Showing the first item in predictions.")
            else:
                response_json = predictions
            prediction_missing = response_json is None

    # ── Tabbed results ──────────────────────────────────────────────────
    tab_diff, tab_response, tab_details = st.tabs([
        "🔀 Diff View", "📄 Full Response", "📋 Request Details"
    ])

    with tab_diff:
        if not (200 <= response.status_code < 300):
            st.error(f"Analysis failed (HTTP {response.status_code}). See the Full Response tab.")
        elif prediction_missing:
            st.info("The endpoint returned no prediction.")
        elif response_is_json and "submitted_claim" in st.session_state:
            show_comparison(st.session_state.submitted_claim, response_json)
        else:
            st.info("No diff available for this response type.")

    with tab_response:
        if prediction_missing:
            st.info("The endpoint returned no prediction.")
        elif response_is_json:
            st.json(response_json, expanded=False)
            st.download_button(
                label="📥 Download JSON", data=json.dumps(response_json, indent=2),
                file_name="response.json", mime="application/json"
            )
        else:
            st.code(response.text if response.text else "(Empty response)", language="json")
            st.download_button(
                label="📥 Download Response", data=response.text,
                file_name="response.txt", mime="text/plain"
            )

    with tab_details:
        if "request_details" in st.session_state:
            details = st.session_state.request_details
            st.markdown(
                'font-size:0.92rem;line-height:1.8;">'
                f'<strong>Method:</strong> {escape(details.get("method", "—"))}<br>'
                f'<strong>Endpoint:</strong> {escape(details.get("endpoint", "—"))}<br>'
                f'<strong>Status:</strong> {response.status_code}<br>'
                f'<strong>Response Time:</strong> {response_time:.2f}s<br>'
                f'<strong>Content-Type:</strong> '
                f'{escape(response.headers.get("Content-Type", "—"))}'
                '</div>',
                unsafe_allow_html=True,
            )
        with st.expander("Response Headers"):
            st.json(dict(response.headers))
