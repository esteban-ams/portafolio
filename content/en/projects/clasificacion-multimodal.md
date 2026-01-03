---
title: Multimodal Classification
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
excerpt: Research project comparing text vs multimodal classification models (BERT, CLIP, FLAVA, ViLT) across multiple datasets. CUDA optimization for large-scale training.
---

# Multimodal Classification

Research project comparing the performance of unimodal (text-only) models against multimodal (text + image) models in classification tasks.

## Research Question

> When does adding visual information significantly improve text classification, and when is it just computational overhead?

## Models Evaluated

### Unimodal Models (Text)

| Model | Parameters | Description |
|-------|------------|-------------|
| BERT-base | 110M | Pretrained transformer encoder |
| RoBERTa | 125M | BERT with better pretraining |
| BETO | 110M | BERT for Spanish |

### Multimodal Models

| Model | Parameters | Modalities |
|-------|------------|------------|
| CLIP | 400M | Image + Text (contrastive) |
| FLAVA | 350M | Image + Text (fusion) |
| ViLT | 113M | Vision-Language Transformer |

## Methodology

### Training Pipeline

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

### Datasets Used

1. **Hateful Memes** (Facebook): Hate content detection in memes
2. **SNLI-VE**: Textual inference with visual evidence
3. **VQA v2**: Question answering about images
4. **Custom News Dataset**: Chilean news classification with images

### Preprocessing

```python
class MultimodalProcessor:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.image_processor = AutoImageProcessor.from_pretrained(model_name)

    def process(self, text: str, image: Image) -> Dict:
        # Tokenize text
        text_inputs = self.tokenizer(
            text,
            max_length=512,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )

        # Process image
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

## CUDA Optimizations

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
# Reduce memory usage in large models
model.gradient_checkpointing_enable()
```

### Multi-GPU with DataParallel

```python
if torch.cuda.device_count() > 1:
    model = nn.DataParallel(model)
    print(f"Using {torch.cuda.device_count()} GPUs")
```

## Results

### Hateful Memes Dataset

| Model | Accuracy | F1 | AUC-ROC |
|-------|----------|-----|---------|
| BERT | 62.3% | 0.58 | 0.67 |
| CLIP | 68.7% | 0.65 | 0.74 |
| FLAVA | **71.2%** | **0.68** | **0.77** |
| ViLT | 69.5% | 0.66 | 0.75 |

### News Classification (Custom)

| Model | Accuracy | F1 Macro |
|-------|----------|----------|
| BETO | 87.2% | 0.86 |
| CLIP | 85.4% | 0.84 |
| FLAVA | 86.8% | 0.85 |

## Conclusions

1. **Multimodal helps when image is relevant**: In Hateful Memes, where meaning depends on text-image combination, FLAVA outperforms BERT by ~9%.

2. **Text is sufficient in many cases**: In news classification, where images are generic, BETO matches or exceeds multimodal models.

3. **Computational trade-off**: Multimodal models require ~4x more VRAM and ~3x more training time.

```
Recommendation:
├── Image is part of meaning → Multimodal (FLAVA)
├── Image is decorative → Unimodal (BERT/BETO)
└── Limited resources → ViLT (more efficient)
```

## Code and Reproducibility

The repository includes:
- Training scripts for all models
- Results analysis notebooks
- Hyperparameter configurations
- Trained model checkpoints

```bash
# Train FLAVA on Hateful Memes
python train.py \
    --model flava \
    --dataset hateful_memes \
    --epochs 10 \
    --batch_size 16 \
    --learning_rate 2e-5
```
