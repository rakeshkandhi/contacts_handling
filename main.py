import csv
import re
import pandas as pd
import vobject
import chardet
import csv
import vobject

name_pattern = re.compile(r"N:([^;]*);([^;]*)")
full_name_pattern = re.compile(r"FN:(.*)")
phone_pattern = re.compile(r"TEL.*:(.*)")
email_pattern = re.compile(r"EMAIL.*:(.*)")
photo_pattern = re.compile(r"PHOTO.*:(.*)")

def detect_encoding(file_path):
    """Detect the encoding of a file."""
    with open(file_path, "rb") as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result["encoding"]

def save_vcf_to_text(input_file_path, output_file_path="contactsTxt.txt"):
    """Read a VCF file and save its content to a text file."""
    try:
        encoding = detect_encoding(input_file_path)
        with open(input_file_path, "r", encoding=encoding, errors="replace") as vcf:
            vcard_data = vcf.read()
        with open(output_file_path, "w", encoding="utf-8") as txt:
            txt.write(vcard_data)
        print(f"VCF data successfully saved to {output_file_path}")
    except FileNotFoundError:
        print(f"Error: The file {input_file_path} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

def vcf_to_sorted_csv(vcf_file, csv_file):
    """Convert VCF to CSV and sort by Full Name."""
    contacts = []
    encoding = detect_encoding(vcf_file)
    with open(vcf_file, "r", encoding=encoding, errors="replace") as vcf:
        contact = {}
        for line in vcf:
            name_match = name_pattern.search(line)
            if name_match:
                last_name = name_match.group(1)
                first_name = name_match.group(2)
                contact["first_name"] = first_name
                contact["last_name"] = last_name
                contact["name"] = f"{first_name} {last_name}"
            full_name_match = full_name_pattern.search(line)
            if full_name_match:
                contact["full_name"] = full_name_match.group(1)
            phone_match = phone_pattern.search(line)
            if phone_match:
                if "phones" not in contact:
                    contact["phones"] = []
                contact["phones"].append(phone_match.group(1))
            email_match = email_pattern.search(line)
            if email_match:
                contact["email"] = email_match.group(1)
            photo_match = photo_pattern.search(line)
            if photo_match:
                contact["photo"] = photo_match.group(1)
            if line.startswith("END:VCARD"):
                contact["phones"] = ", ".join(contact.get("phones", []))
                contacts.append(
                    [
                        contact.get("first_name", ""),
                        contact.get("last_name", ""),
                        contact.get("full_name", ""),
                        contact.get("phones", ""),
                        contact.get("email", ""),
                        contact.get("photo", ""),
                    ]
                )
                contact = {}
    with open(csv_file, "w", newline="", encoding="utf-8") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(
            ["First Name", "Last Name", "Full Name", "Phone Numbers", "Email", "Photo"]
        )
        writer.writerows(contacts)
    df = pd.read_csv(csv_file)
    df = df.sort_values("Full Name")
    df.to_csv(csv_file, index=False)
    print(f"VCF data successfully converted to and sorted in {csv_file}")

def csv_to_vcf(csv_file, vcf_file):
    """
    Convert CSV file to VCF format.
    Args:
    csv_file (str): Path to the input CSV file.
    vcf_file (str): Path to the output VCF file.
    """
    vcf_data = ""
    try:
        with open(csv_file, "r", encoding="utf-8") as csvf:
            reader = csv.DictReader(csvf)
            for row in reader:
                vcard = vobject.vCard()
                full_name = row.get("Full Name", "").strip()
                if full_name:
                    vcard.add("fn").value = full_name
                else:
                    first_name = row.get("First Name", "").strip()
                    last_name = row.get("Last Name", "").strip()
                    if first_name or last_name:
                        vcard.add("fn").value = f"{first_name} {last_name}".strip()
                    else:
                        continue
                name_field = vcard.add("n")
                name_field.value = vobject.vcard.Name(
                    family=row.get("Last Name", "").strip(),
                    given=row.get("First Name", "").strip()
                )
                phone_numbers = row.get("Phone Numbers", "").split(", ")
                for phone in phone_numbers:
                    if phone:  
                        vcard.add("tel").value = phone
                email = row.get("Email", "").strip()
                if email:
                    vcard.add("email").value = email
                vcf_data += vcard.serialize() + "\n"  
    except FileNotFoundError:
        print(f"Error: The file {csv_file} does not exist.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return
    try:
        with open(vcf_file, "w", encoding="utf-8") as vcf:
            vcf.write(vcf_data)
        print(f"VCF data successfully saved to {vcf_file}")
    except Exception as e:
        print(f"An error occurred while writing to {vcf_file}: {e}")
