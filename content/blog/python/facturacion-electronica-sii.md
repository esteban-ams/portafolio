---
title: Integracion con SII Chile - Facturacion Electronica
slug: facturacion-electronica-sii
date: 2024-08-20
tags:
  - Python
  - SII
  - XML
  - Facturacion
excerpt: Guia practica para integrar facturacion electronica del SII Chile en tu aplicacion Python.
---

# Integracion con SII Chile

La facturacion electronica en Chile es obligatoria para la mayoria de contribuyentes. Integrarla correctamente requiere entender el flujo completo: desde la generacion del XML hasta la verificacion del estado.

## Componentes del Sistema

```
┌─────────────┐     ┌──────────────┐     ┌─────────┐
│  Tu Sistema │────▶│ XML + Firma  │────▶│   SII   │
└─────────────┘     └──────────────┘     └─────────┘
       │                   │                   │
       │              Certificado              │
       │               Digital                 │
       ▼                                       ▼
┌─────────────┐                         ┌─────────┐
│     PDF     │                         │ Estado  │
│   + QR TED  │◀────────────────────────│ (SOAP)  │
└─────────────┘                         └─────────┘
```

## 1. Obtener Token de Sesion

El SII requiere autenticacion via SOAP con tu certificado digital:

```python
import zeep
from signxml import XMLSigner

def obtener_token(cert_path: str, key_path: str) -> str:
    """Obtiene token de sesion del SII."""

    # 1. Obtener semilla
    client = zeep.Client('https://palena.sii.cl/DTEWS/CrSeed.jws?WSDL')
    response = client.service.getSeed()

    # 2. Firmar semilla con certificado
    semilla_firmada = firmar_xml(response, cert_path, key_path)

    # 3. Obtener token
    client = zeep.Client('https://palena.sii.cl/DTEWS/GetTokenFromSeed.jws?WSDL')
    token_response = client.service.getToken(semilla_firmada)

    return extraer_token(token_response)
```

## 2. Construir el DTE (Documento Tributario Electronico)

El XML debe seguir el schema exacto del SII:

```python
from lxml import etree

def construir_boleta(venta: Venta, folio: int) -> str:
    """Construye XML de Boleta Electronica (tipo 39)."""

    dte = etree.Element('DTE', version='1.0')
    documento = etree.SubElement(dte, 'Documento', ID=f'DTE-{folio}')

    # Encabezado
    encabezado = etree.SubElement(documento, 'Encabezado')
    id_doc = etree.SubElement(encabezado, 'IdDoc')
    etree.SubElement(id_doc, 'TipoDTE').text = '39'  # Boleta
    etree.SubElement(id_doc, 'Folio').text = str(folio)
    etree.SubElement(id_doc, 'FchEmis').text = venta.fecha.isoformat()

    # Emisor
    emisor = etree.SubElement(encabezado, 'Emisor')
    etree.SubElement(emisor, 'RUTEmisor').text = venta.empresa.rut
    etree.SubElement(emisor, 'RznSoc').text = venta.empresa.razon_social

    # Detalle de items
    for i, item in enumerate(venta.items.all(), 1):
        detalle = etree.SubElement(documento, 'Detalle')
        etree.SubElement(detalle, 'NroLinDet').text = str(i)
        etree.SubElement(detalle, 'NmbItem').text = item.producto.nombre
        etree.SubElement(detalle, 'QtyItem').text = str(item.cantidad)
        etree.SubElement(detalle, 'PrcItem').text = str(item.precio)

    return etree.tostring(dte, encoding='unicode')
```

## 3. Firmar con Certificado Digital

```python
from signxml import XMLSigner, methods
from cryptography import x509
from cryptography.hazmat.primitives import serialization

def firmar_dte(xml: str, cert_path: str, key_path: str) -> str:
    """Firma XML con certificado .pfx del SII."""

    # Cargar certificado
    with open(cert_path, 'rb') as f:
        cert = x509.load_pem_x509_certificate(f.read())

    with open(key_path, 'rb') as f:
        key = serialization.load_pem_private_key(f.read(), password=None)

    # Firmar
    root = etree.fromstring(xml.encode())
    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm='rsa-sha1',
        digest_algorithm='sha1'
    )

    signed = signer.sign(root, key=key, cert=cert)
    return etree.tostring(signed, encoding='unicode')
```

## 4. Generar TED (Timbre Electronico)

El TED es un codigo que permite verificar la autenticidad:

```python
import qrcode
from io import BytesIO

def generar_ted(dte_firmado: str) -> bytes:
    """Genera QR con el TED para impresion."""

    # Extraer datos del TED del XML firmado
    root = etree.fromstring(dte_firmado.encode())
    ted = root.find('.//TED')
    ted_string = etree.tostring(ted, encoding='unicode')

    # Generar QR
    qr = qrcode.QRCode(version=1, box_size=3)
    qr.add_data(ted_string)
    qr.make(fit=True)

    img = qr.make_image()
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()
```

## 5. Verificar Estado

```python
def verificar_estado(rut_emisor: str, tipo_dte: int, folio: int) -> dict:
    """Consulta estado de un DTE en el SII."""

    client = zeep.Client(
        'https://palena.sii.cl/DTEWS/QueryEstDte.jws?WSDL'
    )

    response = client.service.getEstDte(
        RutConsultante=rut_emisor,
        DvConsultante=calcular_dv(rut_emisor),
        RutCompania=rut_emisor,
        DvCompania=calcular_dv(rut_emisor),
        RutReceptor='66666666',  # Boletas van a RUT generico
        DvReceptor='6',
        TipoDte=tipo_dte,
        FolioDte=folio,
        Token=obtener_token()
    )

    return {
        'estado': response.ESTADO,
        'glosa': response.GLOSA_ESTADO,
        'aceptado': response.ESTADO == 'DOK'
    }
```

## Sistema de Reintentos

Los envios pueden fallar. Implementa reintentos robustos:

```python
from celery import shared_task
from datetime import timedelta

@shared_task(bind=True, max_retries=3)
def enviar_dte_async(self, dte_id: int):
    try:
        dte = DTE.objects.get(id=dte_id)
        resultado = enviar_al_sii(dte)
        dte.estado = resultado['estado']
        dte.save()
    except Exception as e:
        # Reintentar en 30 minutos
        raise self.retry(exc=e, countdown=1800)
```

## Conclusion

La integracion con el SII es compleja pero manejable si divides el problema en pasos claros. Lo mas importante es manejar bien los errores y tener un sistema de reintentos robusto.
