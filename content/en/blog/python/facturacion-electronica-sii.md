---
title: SII Chile Integration - Electronic Invoicing
slug: facturacion-electronica-sii
date: 2024-08-20
tags:
  - Python
  - SII
  - XML
  - Invoicing
excerpt: Practical guide to integrate Chilean SII electronic invoicing in your Python application.
---

# SII Chile Integration

Electronic invoicing in Chile is mandatory for most taxpayers. Integrating it correctly requires understanding the complete flow: from XML generation to status verification.

## System Components

```
┌─────────────┐     ┌──────────────┐     ┌─────────┐
│ Your System │────▶│ XML + Sign   │────▶│   SII   │
└─────────────┘     └──────────────┘     └─────────┘
       │                   │                   │
       │              Digital                  │
       │            Certificate                │
       ▼                                       ▼
┌─────────────┐                         ┌─────────┐
│     PDF     │                         │ Status  │
│   + QR TED  │◀────────────────────────│ (SOAP)  │
└─────────────┘                         └─────────┘
```

## 1. Obtain Session Token

SII requires SOAP authentication with your digital certificate:

```python
import zeep
from signxml import XMLSigner

def get_token(cert_path: str, key_path: str) -> str:
    """Obtains session token from SII."""

    # 1. Get seed
    client = zeep.Client('https://palena.sii.cl/DTEWS/CrSeed.jws?WSDL')
    response = client.service.getSeed()

    # 2. Sign seed with certificate
    signed_seed = sign_xml(response, cert_path, key_path)

    # 3. Get token
    client = zeep.Client('https://palena.sii.cl/DTEWS/GetTokenFromSeed.jws?WSDL')
    token_response = client.service.getToken(signed_seed)

    return extract_token(token_response)
```

## 2. Build the DTE (Electronic Tax Document)

The XML must follow the exact SII schema:

```python
from lxml import etree

def build_receipt(sale: Sale, folio: int) -> str:
    """Builds Electronic Receipt XML (type 39)."""

    dte = etree.Element('DTE', version='1.0')
    document = etree.SubElement(dte, 'Documento', ID=f'DTE-{folio}')

    # Header
    header = etree.SubElement(document, 'Encabezado')
    id_doc = etree.SubElement(header, 'IdDoc')
    etree.SubElement(id_doc, 'TipoDTE').text = '39'  # Receipt
    etree.SubElement(id_doc, 'Folio').text = str(folio)
    etree.SubElement(id_doc, 'FchEmis').text = sale.date.isoformat()

    # Issuer
    issuer = etree.SubElement(header, 'Emisor')
    etree.SubElement(issuer, 'RUTEmisor').text = sale.company.rut
    etree.SubElement(issuer, 'RznSoc').text = sale.company.business_name

    # Item details
    for i, item in enumerate(sale.items.all(), 1):
        detail = etree.SubElement(document, 'Detalle')
        etree.SubElement(detail, 'NroLinDet').text = str(i)
        etree.SubElement(detail, 'NmbItem').text = item.product.name
        etree.SubElement(detail, 'QtyItem').text = str(item.quantity)
        etree.SubElement(detail, 'PrcItem').text = str(item.price)

    return etree.tostring(dte, encoding='unicode')
```

## 3. Sign with Digital Certificate

```python
from signxml import XMLSigner, methods
from cryptography import x509
from cryptography.hazmat.primitives import serialization

def sign_dte(xml: str, cert_path: str, key_path: str) -> str:
    """Signs XML with SII .pfx certificate."""

    # Load certificate
    with open(cert_path, 'rb') as f:
        cert = x509.load_pem_x509_certificate(f.read())

    with open(key_path, 'rb') as f:
        key = serialization.load_pem_private_key(f.read(), password=None)

    # Sign
    root = etree.fromstring(xml.encode())
    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm='rsa-sha1',
        digest_algorithm='sha1'
    )

    signed = signer.sign(root, key=key, cert=cert)
    return etree.tostring(signed, encoding='unicode')
```

## 4. Generate TED (Electronic Stamp)

The TED is a code that allows authenticity verification:

```python
import qrcode
from io import BytesIO

def generate_ted(signed_dte: str) -> bytes:
    """Generates QR with TED for printing."""

    # Extract TED data from signed XML
    root = etree.fromstring(signed_dte.encode())
    ted = root.find('.//TED')
    ted_string = etree.tostring(ted, encoding='unicode')

    # Generate QR
    qr = qrcode.QRCode(version=1, box_size=3)
    qr.add_data(ted_string)
    qr.make(fit=True)

    img = qr.make_image()
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()
```

## 5. Verify Status

```python
def verify_status(issuer_rut: str, dte_type: int, folio: int) -> dict:
    """Queries DTE status from SII."""

    client = zeep.Client(
        'https://palena.sii.cl/DTEWS/QueryEstDte.jws?WSDL'
    )

    response = client.service.getEstDte(
        RutConsultante=issuer_rut,
        DvConsultante=calculate_dv(issuer_rut),
        RutCompania=issuer_rut,
        DvCompania=calculate_dv(issuer_rut),
        RutReceptor='66666666',  # Receipts go to generic RUT
        DvReceptor='6',
        TipoDte=dte_type,
        FolioDte=folio,
        Token=get_token()
    )

    return {
        'status': response.ESTADO,
        'message': response.GLOSA_ESTADO,
        'accepted': response.ESTADO == 'DOK'
    }
```

## Retry System

Submissions can fail. Implement robust retries:

```python
from celery import shared_task
from datetime import timedelta

@shared_task(bind=True, max_retries=3)
def send_dte_async(self, dte_id: int):
    try:
        dte = DTE.objects.get(id=dte_id)
        result = send_to_sii(dte)
        dte.status = result['status']
        dte.save()
    except Exception as e:
        # Retry in 30 minutes
        raise self.retry(exc=e, countdown=1800)
```

## Conclusion

SII integration is complex but manageable if you divide the problem into clear steps. Most importantly, handle errors well and have a robust retry system.
