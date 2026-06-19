import csv
import json
import os

# I know this is basic but it works for cleaning up names
def normalize_name(name):
    if not name:
        return ""
    return name.lower().strip()

# This is where I calculate how much I trust a contact
# Not perfect but it's my best attempt at being honest about confidence
def calculate_confidence(contact_name, company_data):
    reg = company_data.get("registry", {})
    lst = company_data.get("listing", {})
    enr = company_data.get("enrichment", {})

    score = 0
    has_contact = False

    # Start with provider's own confidence if they have it
    if enr and (enr.get("email") or enr.get("phone")):
        score = enr.get("provider_confidence", 0)
        has_contact = True
    elif lst and lst.get("phone"):
        # Listing has phone but no confidence score, so I give a default
        score = 40
        has_contact = True
        
    if not has_contact:
        return 0

    # If registry and listing agree on name, that's good
    reg_name = normalize_name(reg.get("name"))
    lst_name = normalize_name(lst.get("name"))

    if reg_name and lst_name and (reg_name in lst_name or lst_name in reg_name or reg_name[0] == lst_name[0]):
        score += 20
        
    # If enrichment found someone and registry has a real person, that's also good
    if enr and reg_name:
        score += 15

    # If phone number matches across sources, even better
    enr_phone = enr.get("phone")
    lst_phone = lst.get("phone")
    if enr_phone and lst_phone and enr_phone == lst_phone:
        score += 20

    # Penalty for generic names (info@, office, etc.) or missing name entirely
    if not contact_name or "info" in contact_name.lower() or "office" in contact_name.lower():
        score -= 30

    # Keep score between 0 and 100
    return min(100, max(0, score))

def process_companies(csv_path, mocks_path, output_path):
    # Load the mock data (in real life this would be API calls)
    with open(mocks_path, 'r') as f:
        mocks = json.load(f)

    results = []
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            company = row["company_name"]
            data = mocks.get(company, {})
            
            # If company not found in any provider, just mark as needs review
            if not data:
                results.append({
                    "company_name": company,
                    "contact_name": "",
                    "contact_role": "",
                    "contact_email_or_phone": "",
                    "confidence_score": 0,
                    "source": "",
                    "needs_human_review": "true"
                })
                continue
            
            reg = data.get("registry", {})
            lst = data.get("listing", {})
            enr = data.get("enrichment", {})
            
            # Try multiple sources for name and role
            contact_name = reg.get("name") or lst.get("name") or ""
            contact_role = reg.get("role") or lst.get("role") or enr.get("role") or ""
            
            # Prefer email over phone
            email = enr.get("email")
            phone = enr.get("phone") or lst.get("phone")
            contact_email_or_phone = email if email else phone
            
            # Track where each piece came from
            sources = []
            if reg and reg.get("source_url"):
                sources.append(reg.get("source_url"))
            if lst and lst.get("source_url"):
                sources.append(lst.get("source_url"))
            if enr and enr.get("source_url"):
                sources.append(enr.get("source_url"))
            
            score = calculate_confidence(contact_name, data)
            
            # Per CLARIFICATIONS.md, threshold is 70
            needs_human_review = score < 70
            if needs_human_review:
                # Don't output contact info if confidence is too low
                contact_email_or_phone = ""
                
            results.append({
                "company_name": company,
                "contact_name": contact_name,
                "contact_role": contact_role,
                "contact_email_or_phone": contact_email_or_phone,
                "confidence_score": score,
                "source": ", ".join(sources) if sources else "",
                "needs_human_review": "true" if needs_human_review else "false"
            })

    # Write results to CSV
    fieldnames = ["company_name", "contact_name", "contact_role", "contact_email_or_phone", 
                  "confidence_score", "source", "needs_human_review"]
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Processed {len(results)} companies. Output saved to {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_input = os.path.join(base_dir, "sample_data.csv")
    mocks_input = os.path.join(base_dir, "mock_responses.json")
    csv_output = os.path.join(base_dir, "output_sample.csv")
    
    process_companies(csv_input, mocks_input, csv_output)