# Document OCR Processor - Sistema Inteligente de Extracción de Datos

## 📋 Descripción General

Este proyecto es un **sistema completo de procesamiento automático de documentos con OCR** diseñado específicamente para la extracción inteligente de datos de documentos. Combina múltiples tecnologías de vanguardia para convertir documentos físicos y digitales en datos estructurados, automatizando procesos que tradicionalmente requieren intervención manual.

## 🏗️ Arquitectura y Tecnologías

### 🔄 Procesamiento Multi-etapa
- **Conversión de PDFs**: Transforma documentos PDF (estructurados y no estructurados) en imágenes procesables
- **OCR Híbrido**: Implementa dos estrategias complementarias de reconocimiento óptico de caracteres
- **Extracción Inteligente**: Utiliza IA generativa para interpretar y estructurar la información extraída

### 🛠️ Tecnologías Implementadas

#### OCR Local con Tesseract
- Procesamiento avanzado de imágenes con OpenCV
- Técnicas de preprocesamiento: escalado, umbralización adaptativa, reducción de ruido
- Reconocimiento multilingüe (español/inglés) con configuración optimizada
- Extracción basada en expresiones regulares flexibles que manejan errores de OCR

#### OCR Cloud con Azure Cognitive Services
- Integración completa con Azure Computer Vision API
- Procesamiento asíncrono de alta precisión
- Manejo robusto de diferentes formatos de imagen
- Validación automática de archivos

#### Procesamiento Inteligente con IA
- Integración con OpenAI GPT-3.5-turbo para análisis semántico
- Extracción estructurada de campos específicos de facturas
- Interpretación contextual de datos ambiguos
- Generación de respuestas en formato JSON estandarizado

## 📊 Campos Extraídos Automáticamente
- ✅ Fecha de emisión
- ✅ Número de factura
- ✅ Información del cliente (nombre, domicilio, ciudad)
- ✅ Identificación fiscal (NIF/DNI)
- ✅ Desglose económico (subtotal, IVA, total)
- ✅ Conceptos y detalles específicos

## 💾 Gestión de Datos
- Almacenamiento estructurado en archivos CSV
- Sistema de logging de errores para seguimiento de fallos
- Persistencia de datos procesados exitosamente
- Archivos de auditoría para debugging

## 🎯 Casos de Uso
- **Automatización de Contabilidad**: Procesamiento masivo de facturas para empresas
- **Digitalización de Archivos**: Conversión de documentos físicos a datos digitales
- **Extracción de Datos Empresariales**: Análisis automático de documentos comerciales
- **Integración con Sistemas ERP**: Alimentación automática de bases de datos contables

## ⚡ Ventajas Técnicas
- **Alta Tolerancia a Errores**: Maneja documentos de baja calidad y diferentes formatos
- **Escalabilidad**: Arquitectura modular permite procesamiento batch
- **Flexibilidad**: Soporte para múltiples tipos de documento
- **Integración Cloud**: Aprovecha servicios de IA de última generación
- **Mantenibilidad**: Código bien documentado y modular

**Desarrollado como proyecto académico de Desarrollo Cloud**
