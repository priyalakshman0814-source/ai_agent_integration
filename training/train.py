import torch
from pathlib import Path

from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from peft import (
    LoraConfig,
    prepare_model_for_kbit_training,
)
from trl import SFTConfig, SFTTrainer


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "Qwen/Qwen3-4B-Instruct-2507"

BASE_DIR = Path(__file__).parent

TRAIN_FILE = BASE_DIR / "train.jsonl"
VALIDATION_FILE = BASE_DIR / "validation.jsonl"

OUTPUT_DIR = BASE_DIR / "soft-flower-qwen3-lora"

MAX_LENGTH = 512


# ============================================================
# START
# ============================================================

print()
print("=" * 60)
print("SOFT FLOWER QWEN3 QLoRA TRAINING")
print("=" * 60)


# ============================================================
# GPU CHECK
# ============================================================

if not torch.cuda.is_available():

    raise RuntimeError(
        "CUDA GPU was not detected."
    )


gpu_name = torch.cuda.get_device_name(0)

gpu_memory = (
    torch.cuda.get_device_properties(0).total_memory
    / (1024 ** 3)
)


print()
print("GPU:")
print(gpu_name)

print()
print(
    f"GPU memory: {gpu_memory:.2f} GB"
)

print()
print(
    f"PyTorch: {torch.__version__}"
)


# ============================================================
# PRECISION
# ============================================================

if torch.cuda.is_bf16_supported():

    compute_dtype = torch.bfloat16

    print()
    print("Compute dtype: bfloat16")

else:

    compute_dtype = torch.float16

    print()
    print("Compute dtype: float16")


# ============================================================
# DATASET CHECK
# ============================================================

if not TRAIN_FILE.exists():

    raise FileNotFoundError(
        f"Training dataset not found:\n{TRAIN_FILE}"
    )


if not VALIDATION_FILE.exists():

    raise FileNotFoundError(
        f"Validation dataset not found:\n{VALIDATION_FILE}"
    )


# ============================================================
# LOAD DATASET
# ============================================================

print()
print("Loading dataset...")


dataset = load_dataset(
    "json",
    data_files={
        "train": str(TRAIN_FILE),
        "validation": str(VALIDATION_FILE),
    }
)


print()
print(
    f"Training examples: {len(dataset['train'])}"
)

print(
    f"Validation examples: {len(dataset['validation'])}"
)


# ============================================================
# 4-BIT QLoRA
# ============================================================

print()
print("Creating 4-bit QLoRA configuration...")


bnb_config = BitsAndBytesConfig(

    load_in_4bit=True,

    bnb_4bit_quant_type="nf4",

    bnb_4bit_use_double_quant=True,

    bnb_4bit_compute_dtype=compute_dtype,
)


# ============================================================
# TOKENIZER
# ============================================================

print()
print("Loading tokenizer...")


tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
)


if tokenizer.pad_token is None:

    tokenizer.pad_token = tokenizer.eos_token


# ============================================================
# MODEL
# ============================================================

print()
print("Loading Qwen3-4B model...")
print()


model = AutoModelForCausalLM.from_pretrained(

    MODEL_NAME,

    quantization_config=bnb_config,

    device_map="auto",

    dtype=compute_dtype,

    trust_remote_code=True,
)


# ============================================================
# PREPARE MODEL
# ============================================================

print()
print("Preparing model for QLoRA...")


model = prepare_model_for_kbit_training(
    model
)


model.config.use_cache = False


# ============================================================
# LoRA CONFIGURATION
# ============================================================

print()
print("Creating LoRA configuration...")


peft_config = LoraConfig(

    r=8,

    lora_alpha=16,

    lora_dropout=0.05,

    bias="none",

    task_type="CAUSAL_LM",

    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
    ],
)


# ============================================================
# SFT CONFIGURATION
# ============================================================

print()
print("Creating SFT configuration...")


training_args = SFTConfig(

    output_dir=str(OUTPUT_DIR),

    # Training
    num_train_epochs=3,

    per_device_train_batch_size=1,

    per_device_eval_batch_size=1,

    gradient_accumulation_steps=8,

    # Sequence length
    max_length=MAX_LENGTH,

    # Memory optimization
    gradient_checkpointing=True,

    gradient_checkpointing_kwargs={
        "use_reentrant": False
    },

    # Learning
    learning_rate=2e-4,

    weight_decay=0.01,

    warmup_steps=5,

    lr_scheduler_type="cosine",

    # Logging
    logging_steps=5,

    # Evaluation
    eval_strategy="steps",

    eval_steps=25,

    # Saving
    save_strategy="steps",

    save_steps=25,

    save_total_limit=2,

    # Precision
    fp16=(
        compute_dtype == torch.float16
    ),

    bf16=(
        compute_dtype == torch.bfloat16
    ),

    # Optimizer
    optim="paged_adamw_8bit",

    # Disable external logging
    report_to="none",

    # Dataset
    remove_unused_columns=False,

    # Packing
    packing=False,

    # Train assistant responses
    assistant_only_loss=True,
)


# ============================================================
# SFT TRAINER
# ============================================================

print()
print("Creating SFT trainer...")


trainer = SFTTrainer(

    model=model,

    args=training_args,

    train_dataset=dataset["train"],

    eval_dataset=dataset["validation"],

    processing_class=tokenizer,

    peft_config=peft_config,
)


# ============================================================
# START TRAINING
# ============================================================

print()
print("=" * 60)
print("STARTING TRAINING")
print("=" * 60)

print()
print("Training will now begin.")
print("Do not close this terminal.")
print()


trainer.train()


# ============================================================
# SAVE
# ============================================================

print()
print("=" * 60)
print("SAVING MODEL")
print("=" * 60)


trainer.save_model(
    str(OUTPUT_DIR)
)


tokenizer.save_pretrained(
    str(OUTPUT_DIR)
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 60)
print("TRAINING COMPLETE")
print("=" * 60)

print()
print("LoRA adapter saved to:")

print(
    OUTPUT_DIR
)

print()
print("Next step: test the trained model.")

print("=" * 60)