---
title: Clasificacion Multimodal
slug: clasificacion-multimodal
technologies:
  - PyTorch
  - Transformers
  - CUDA
  - scikit-learn
  - HuggingFace
github: https://github.com/estebanmartinezsoto/multimodal-classification
demo: null
featured: false
image: /static/images/ml-research.jpg
excerpt: Proyecto de investigacion comparando modelos de clasificacion texto vs multimodal (BERT, CLIP, FLAVA, ViLT) en multiples datasets. Optimizacion CUDA para entrenamiento a gran escala.
---

# Clasificacion Multimodal

Proyecto de investigacion que compara el rendimiento de modelos unimodales (solo texto) contra modelos multimodales (texto + imagen) en tareas de clasificacion.

## Pregunta de Investigacion

> ¿Cuando agregar informacion visual mejora significativamente la clasificacion de texto, y cuando es solo overhead computacional?

## Modelos Evaluados

### Modelos Unimodales (Texto)

| Modelo | Parametros | Descripcion |
|--------|------------|-------------|
| BERT-base | 110M | Transformer encoder preentrenado |
| RoBERTa | 125M | BERT con mejor preentrenamiento |
| BETO | 110M | BERT para espanol |

### Modelos Multimodales

| Modelo | Parametros | Modalidades |
|--------|------------|-------------|
| CLIP | 400M | Imagen + Texto (contrastivo) |
| FLAVA | 350M | Imagen + Texto (fusion) |
| ViLT | 113M | Vision-Language Transformer |

## Metodologia

### Pipeline de Entrenamiento

```python
class MultimodalTrainer:
    def __init__(self, model_name: str, dataset: Dataset):
        self.model = self._load_model(model_name)
        self.dataset = dataset
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def train(self, epochs: int = 10, batch_size: int = 32):
        self.model.to(self.device)
        optimizer = AdamW(self.model.parameters(), lr=2e-5)

        for epoch in range(epochs):
            self.model.train()
            total_loss = 0

            for batch in DataLoader(self.dataset, batch_size=batch_size):
                # Forward pass
                if self.is_multimodal:
                    outputs = self.model(
                        input_ids=batch['input_ids'].to(self.device),
                        pixel_values=batch['pixel_values'].to(self.device),
                        labels=batch['labels'].to(self.device)
                    )
                else:
                    outputs = self.model(
                        input_ids=batch['input_ids'].to(self.device),
                        labels=batch['labels'].to(self.device)
                    )

                loss = outputs.loss
                total_loss += loss.item()

                # Backward pass
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()

            print(f"Epoch {epoch}: Loss = {total_loss / len(self.dataset)}")
```

### Datasets Utilizados

1. **Hateful Memes** (Facebook): Deteccion de contenido de odio en memes
2. **SNLI-VE**: Inferencia textual con evidencia visual
3. **VQA v2**: Respuesta a preguntas sobre imagenes
4. **Custom News Dataset**: Clasificacion de noticias chilenas con imagenes

### Preprocesamiento

```python
class MultimodalProcessor:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.image_processor = AutoImageProcessor.from_pretrained(model_name)

    def process(self, text: str, image: Image) -> Dict:
        # Tokenizar texto
        text_inputs = self.tokenizer(
            text,
            max_length=512,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )

        # Procesar imagen
        image_inputs = self.image_processor(
            image,
            return_tensors='pt'
        )

        return {
            'input_ids': text_inputs['input_ids'],
            'attention_mask': text_inputs['attention_mask'],
            'pixel_values': image_inputs['pixel_values']
        }
```

## Optimizaciones CUDA

### Mixed Precision Training

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for batch in dataloader:
    optimizer.zero_grad()

    with autocast():
        outputs = model(**batch)
        loss = outputs.loss

    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

### Gradient Checkpointing

```python
# Reducir uso de memoria en modelos grandes
model.gradient_checkpointing_enable()
```

### Multi-GPU con DataParallel

```python
if torch.cuda.device_count() > 1:
    model = nn.DataParallel(model)
    print(f"Using {torch.cuda.device_count()} GPUs")
```

## Resultados

### Hateful Memes Dataset

| Modelo | Accuracy | F1 | AUC-ROC |
|--------|----------|-----|---------|
| BERT | 62.3% | 0.58 | 0.67 |
| CLIP | 68.7% | 0.65 | 0.74 |
| FLAVA | **71.2%** | **0.68** | **0.77** |
| ViLT | 69.5% | 0.66 | 0.75 |

### News Classification (Custom)

| Modelo | Accuracy | F1 Macro |
|--------|----------|----------|
| BETO | 87.2% | 0.86 |
| CLIP | 85.4% | 0.84 |
| FLAVA | 86.8% | 0.85 |

## Conclusiones

1. **Multimodal ayuda cuando la imagen es relevante**: En Hateful Memes, donde el significado depende de la combinacion texto-imagen, FLAVA supera a BERT por ~9%.

2. **Texto es suficiente en muchos casos**: En clasificacion de noticias, donde las imagenes son genericas, BETO iguala o supera a modelos multimodales.

3. **Trade-off computacional**: Modelos multimodales requieren ~4x mas VRAM y ~3x mas tiempo de entrenamiento.

```
Recomendacion:
├── Imagen es parte del significado → Multimodal (FLAVA)
├── Imagen es decorativa → Unimodal (BERT/BETO)
└── Recursos limitados → ViLT (mas eficiente)
```

## Codigo y Reproducibilidad

El repositorio incluye:
- Scripts de entrenamiento para todos los modelos
- Notebooks de analisis de resultados
- Configuraciones de hiperparametros
- Checkpoints de modelos entrenados

```bash
# Entrenar FLAVA en Hateful Memes
python train.py \
    --model flava \
    --dataset hateful_memes \
    --epochs 10 \
    --batch_size 16 \
    --learning_rate 2e-5
```
